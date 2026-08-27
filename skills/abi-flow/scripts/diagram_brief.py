#!/usr/bin/env python3
"""Validate DiagramSpec Brief sidecars and completed content reviews."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


ROOT = Path(__file__).resolve().parents[1]
PROFILES_PATH = ROOT / "references" / "diagram-thinking-profiles.json"
DENSITIES = {"low", "medium", "high"}
COMPOSITIONS = {"graph", "board"}
REQUIRED_STRINGS = {"goal", "audience", "narrative", "scope", "diagram_type", "composition", "density"}
REQUIRED_LISTS = {
    "must_show", "emphasize", "deemphasize", "relationships", "uncertainties",
    "assumptions", "content_risks", "quality_questions",
}
OPTIONAL_FIELDS = {"review_answers"}
PROFILE_FIELDS = {"question", "focus", "must_distinguish", "failure_modes", "quality_questions"}
STOP_WORDS = {
    "about", "after", "again", "against", "also", "and", "are", "been", "before", "being",
    "between", "both", "but", "can", "could", "does", "each", "every", "from", "have", "into",
    "only", "rather", "should", "that", "the", "their", "then", "there", "these", "they", "this",
    "those", "through", "under", "viewer", "when", "where", "which", "while", "with", "without",
}
GENERIC_EVIDENCE = {
    "verified in the rendered png", "verified in the rendered svg", "looks good", "checked", "passed",
}


@dataclass(frozen=True)
class BriefIssue:
    level: str
    code: str
    message: str

    def as_dict(self) -> Dict[str, str]:
        return {"level": self.level, "code": self.code, "message": self.message}


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and all(_non_empty_string(item) for item in value)


def canonical_sha256(value: Any) -> str:
    content = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def _semantic_tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    result = set()
    for word in words:
        if len(word) < 4 or word in STOP_WORDS:
            continue
        if word.endswith("ies") and len(word) > 5:
            word = word[:-3] + "y"
        elif word.endswith("ing") and len(word) > 6:
            word = word[:-3]
        elif word.endswith("ed") and len(word) > 5:
            word = word[:-2]
        elif word.endswith("s") and len(word) > 5:
            word = word[:-1]
        result.add(word)
    return result


def validate_profile_questions(brief: Dict[str, Any], profile: Dict[str, Any]) -> List[BriefIssue]:
    questions = brief.get("quality_questions")
    if not _string_list(questions):
        return []
    issues: List[BriefIssue] = []
    normalized = [" ".join(question.lower().split()) for question in questions]
    if len(set(normalized)) != len(normalized):
        issues.append(BriefIssue("error", "duplicate-quality-question", "quality_questions must be unique"))
    profile_text = " ".join(
        [profile.get("question", "")]
        + profile.get("focus", [])
        + profile.get("must_distinguish", [])
        + profile.get("failure_modes", [])
        + profile.get("quality_questions", [])
    )
    profile_tokens = _semantic_tokens(profile_text)
    grounded = [question for question in questions if len(_semantic_tokens(question) & profile_tokens) >= 2]
    total_overlap = set().union(*(_semantic_tokens(question) & profile_tokens for question in questions)) if questions else set()
    if len(grounded) < 3 or len(total_overlap) < 6:
        issues.append(BriefIssue(
            "error", "profile-quality-gap",
            "quality_questions must include at least three concrete checks grounded in this diagram type's thinking profile",
        ))
    return issues


def load_profiles() -> Dict[str, Dict[str, Any]]:
    data = json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not data:
        raise ValueError("diagram thinking profiles must be a non-empty JSON object")
    for slug, profile in data.items():
        if not isinstance(profile, dict) or not PROFILE_FIELDS.issubset(profile):
            raise ValueError(f"thinking profile {slug!r} is incomplete")
        for field in PROFILE_FIELDS - {"question"}:
            if not _string_list(profile[field]):
                raise ValueError(f"thinking profile {slug!r}.{field} must be a string array")
        if not _non_empty_string(profile["question"]):
            raise ValueError(f"thinking profile {slug!r}.question must be non-empty")
        if len(profile["failure_modes"]) < 2 or len(profile["quality_questions"]) < 3:
            raise ValueError(f"thinking profile {slug!r} needs failure modes and quality questions")
    return data


def profile_for(diagram_type: str) -> Dict[str, Any]:
    profiles = load_profiles()
    try:
        return {"slug": diagram_type, **profiles[diagram_type]}
    except KeyError as exc:
        raise KeyError(f"unknown diagram type: {diagram_type}") from exc


def validate_review_answers(brief: Dict[str, Any], require_review: bool) -> List[BriefIssue]:
    issues: List[BriefIssue] = []
    questions = brief.get("quality_questions", [])
    answers = brief.get("review_answers")
    if answers is None:
        if require_review:
            issues.append(BriefIssue("error", "missing-review-answers", "review_answers are required after visual review"))
        return issues
    if not isinstance(answers, list):
        return [BriefIssue("error", "invalid-review-answers", "review_answers must be an array")]

    seen = set()
    answered = set()
    evidence_seen = set()
    allowed_questions = set(questions) if _string_list(questions) else set()
    for index, answer in enumerate(answers):
        location = f"review_answers[{index}]"
        if not isinstance(answer, dict):
            issues.append(BriefIssue("error", "invalid-review-answer", f"{location} must be an object"))
            continue
        unknown = sorted(set(answer) - {"question", "status", "evidence"})
        if unknown:
            issues.append(BriefIssue("warning", "unknown-review-field", f"{location} contains unknown fields: {', '.join(unknown)}"))
        question = answer.get("question")
        status = answer.get("status")
        evidence = answer.get("evidence")
        if not _non_empty_string(question):
            issues.append(BriefIssue("error", "missing-review-question", f"{location}.question must be non-empty"))
            continue
        if question in seen:
            issues.append(BriefIssue("error", "duplicate-review-question", f"Review question is answered more than once: {question}"))
        seen.add(question)
        if allowed_questions and question not in allowed_questions:
            issues.append(BriefIssue("error", "unknown-review-question", f"Review answer does not match quality_questions: {question}"))
        else:
            answered.add(question)
        if status not in {"pass", "fail", "not-reviewed"}:
            issues.append(BriefIssue("error", "invalid-review-status", f"{location}.status must be pass, fail, or not-reviewed"))
        if not _non_empty_string(evidence):
            issues.append(BriefIssue("error", "missing-review-evidence", f"{location}.evidence must be non-empty"))
        else:
            normalized_evidence = " ".join(evidence.lower().strip().rstrip(".").split())
            if len(evidence.strip()) < 24 or normalized_evidence in GENERIC_EVIDENCE:
                issues.append(BriefIssue("error", "weak-review-evidence", f"{location}.evidence must cite a concrete visible label, route, boundary, or layout fact"))
            if normalized_evidence in evidence_seen:
                issues.append(BriefIssue("error", "duplicate-review-evidence", "Each review answer needs distinct visual evidence"))
            evidence_seen.add(normalized_evidence)
        if require_review and status != "pass":
            issues.append(BriefIssue("error", "content-review-not-passed", f"Review question did not pass: {question}"))

    if require_review and allowed_questions - answered:
        missing = sorted(allowed_questions - answered)
        issues.append(BriefIssue("error", "incomplete-content-review", "Missing review answers for: " + " | ".join(missing)))
    return issues


def validate_spec_alignment(brief: Dict[str, Any], spec: Any) -> List[BriefIssue]:
    if not isinstance(spec, dict):
        return [BriefIssue("error", "invalid-diagram-spec", "Diagram source must be a JSON object")]
    issues: List[BriefIssue] = []
    if brief.get("diagram_type") != spec.get("diagram_type", "process-flow"):
        issues.append(BriefIssue("error", "brief-type-mismatch", "Brief and diagram source use different diagram_type values"))
    source_composition = "board" if spec.get("layout") == "board" else "graph"
    if brief.get("composition") != source_composition:
        issues.append(BriefIssue("error", "brief-composition-mismatch", f"Brief expects {brief.get('composition')!r} but diagram source is {source_composition!r}"))
    return issues


def validate_brief(brief: Dict[str, Any], require_review: bool = False, spec: Any = None) -> List[BriefIssue]:
    if not isinstance(brief, dict):
        return [BriefIssue("error", "invalid-root", "Diagram Brief must be a JSON object")]

    issues: List[BriefIssue] = []
    try:
        profiles = load_profiles()
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [BriefIssue("error", "invalid-thinking-profiles", str(exc))]

    allowed_fields = REQUIRED_STRINGS | REQUIRED_LISTS | OPTIONAL_FIELDS
    for field in sorted(set(brief) - allowed_fields):
        issues.append(BriefIssue("warning", "unknown-brief-field", f"Unknown Diagram Brief field: {field}"))

    for field in sorted(REQUIRED_STRINGS):
        if not _non_empty_string(brief.get(field)):
            issues.append(BriefIssue("error", f"missing-{field.replace('_', '-')}", f"{field} must be a non-empty string"))
    for field in sorted(REQUIRED_LISTS):
        if field not in brief:
            issues.append(BriefIssue("error", f"missing-{field.replace('_', '-')}", f"{field} must be present as an array"))
        elif not _string_list(brief[field]):
            issues.append(BriefIssue("error", f"invalid-{field.replace('_', '-')}", f"{field} must contain only non-empty strings"))

    diagram_type = brief.get("diagram_type")
    if _non_empty_string(diagram_type) and diagram_type not in profiles:
        issues.append(BriefIssue("error", "unknown-diagram-type", f"Unsupported diagram_type: {diagram_type}"))
    if _non_empty_string(brief.get("density")) and brief["density"] not in DENSITIES:
        issues.append(BriefIssue("error", "invalid-density", "density must be low, medium, or high"))
    if _non_empty_string(brief.get("composition")) and brief["composition"] not in COMPOSITIONS:
        issues.append(BriefIssue("error", "invalid-composition", "composition must be graph or board"))

    for field in ("must_show", "emphasize", "relationships", "content_risks"):
        if _string_list(brief.get(field)) and not brief[field]:
            issues.append(BriefIssue("warning", f"empty-{field.replace('_', '-')}", f"{field} should contain at least one concrete item"))
    if _string_list(brief.get("quality_questions")) and len(brief["quality_questions"]) < 3:
        issues.append(BriefIssue("warning", "weak-quality-gate", "quality_questions should contain at least three concrete checks"))
    if _non_empty_string(diagram_type) and diagram_type in profiles:
        issues.extend(validate_profile_questions(brief, profiles[diagram_type]))

    must_show = brief.get("must_show", [])
    composition = brief.get("composition")
    if _string_list(must_show):
        limit = 45 if composition == "board" else 14
        if len(must_show) > limit:
            issues.append(BriefIssue("warning", "overloaded-must-show", f"must_show exceeds the {composition or 'selected'} composition limit of {limit}"))
    if _non_empty_string(brief.get("narrative")) and len(brief["narrative"].splitlines()) > 1:
        issues.append(BriefIssue("warning", "multi-line-narrative", "narrative should be one scannable sentence"))

    issues.extend(validate_review_answers(brief, require_review))
    if spec is not None:
        issues.extend(validate_spec_alignment(brief, spec))
    return issues


def command_validate(path: Path, strict: bool, reviewed: bool, spec_path: Optional[Path]) -> int:
    if reviewed and spec_path is None:
        print("error: reviewed-spec-required: --reviewed requires --spec so the completed review is bound to a concrete diagram source", file=sys.stderr)
        return 1
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON at line {exc.lineno}: {exc.msg}", file=sys.stderr)
        return 1

    diagram_spec = None
    if spec_path is not None:
        try:
            diagram_spec = json.loads(spec_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            print(f"error: diagram source not found: {spec_path}", file=sys.stderr)
            return 1
        except json.JSONDecodeError as exc:
            print(f"error: invalid diagram source JSON at line {exc.lineno}: {exc.msg}", file=sys.stderr)
            return 1

    issues = validate_brief(data, require_review=reviewed, spec=diagram_spec)
    for issue in issues:
        print(f"{issue.level}: {issue.code}: {issue.message}")
    failed = any(issue.level == "error" or (strict and issue.level == "warning") for issue in issues)
    if not issues:
        print("brief validation: passed" + (" (review complete)" if reviewed else ""))
        if reviewed and diagram_spec is not None:
            print(f"reviewed spec sha256 (canonical JSON): {canonical_sha256(diagram_spec)}")
    return int(failed)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a DiagramSpec Brief")
    parser.add_argument("input", type=Path)
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    parser.add_argument("--reviewed", action="store_true", help="Require every quality question to have passing evidence")
    parser.add_argument("--spec", type=Path, help="Require diagram_type and composition to match this DiagramSpec source")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    return command_validate(args.input, args.strict, args.reviewed, args.spec)


if __name__ == "__main__":
    raise SystemExit(main())
