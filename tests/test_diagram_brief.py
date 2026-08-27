import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "skills" / "diagram-skills" / "references" / "diagram-thinking-profiles.json"
TEMPLATE = ROOT / "skills" / "diagram-skills" / "templates" / "briefs" / "diagram-brief.json"
MODULE = ROOT / "skills" / "diagram-skills" / "scripts" / "diagram_brief.py"
EXAMPLES = ROOT / "examples" / "briefs"
EXPECTED_TYPES = {
    "system-architecture", "agent-workflow", "data-flow", "capability-map", "user-flow",
    "system-topology", "decision-tree", "roadmap", "strategy-map", "process-flow",
}
REQUIRED_PROFILE_FIELDS = {"question", "focus", "must_distinguish", "failure_modes", "quality_questions"}
REQUIRED_BRIEF_FIELDS = {
    "goal", "audience", "narrative", "scope", "diagram_type", "composition", "must_show",
    "emphasize", "deemphasize", "relationships", "uncertainties", "assumptions", "density",
    "content_risks", "quality_questions",
}


def load_validator():
    spec = importlib.util.spec_from_file_location("diagram_brief", MODULE)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class DiagramThinkingLayerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_validator()

    def test_all_diagram_types_have_complete_profiles(self):
        profiles = json.loads(PROFILES.read_text(encoding="utf-8"))
        self.assertEqual(EXPECTED_TYPES, set(profiles))
        for diagram_type, profile in profiles.items():
            self.assertTrue(REQUIRED_PROFILE_FIELDS.issubset(profile), diagram_type)
            self.assertGreaterEqual(len(profile["quality_questions"]), 3, diagram_type)
            self.assertGreaterEqual(len(profile["failure_modes"]), 2, diagram_type)
            self.assertEqual(diagram_type, self.validator.profile_for(diagram_type)["slug"])

    def test_brief_template_has_complete_contract(self):
        brief = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        self.assertTrue(REQUIRED_BRIEF_FIELDS.issubset(brief))
        self.assertEqual([], self.validator.validate_brief(brief))

    def test_validator_rejects_missing_narrative_unknown_type_and_composition(self):
        brief = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        brief["narrative"] = ""
        brief["diagram_type"] = "mind-map"
        brief["composition"] = "freehand"
        codes = {issue.code for issue in self.validator.validate_brief(brief)}
        self.assertIn("missing-narrative", codes)
        self.assertIn("unknown-diagram-type", codes)
        self.assertIn("invalid-composition", codes)

    def test_density_limits_respect_graph_and_board_compositions(self):
        brief = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        brief["must_show"] = [f"fact-{index}" for index in range(15)]
        brief["composition"] = "graph"
        self.assertIn("overloaded-must-show", {issue.code for issue in self.validator.validate_brief(brief)})
        brief["composition"] = "board"
        self.assertNotIn("overloaded-must-show", {issue.code for issue in self.validator.validate_brief(brief)})

    def test_review_gate_requires_matching_passing_evidence(self):
        brief = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        codes = {issue.code for issue in self.validator.validate_brief(brief, require_review=True)}
        self.assertIn("missing-review-answers", codes)
        brief["review_answers"] = [
            {
                "question": question,
                "status": "pass",
                "evidence": f"Visible check {index + 1}: the rendered layer label and its connected route provide concrete evidence for this question.",
            }
            for index, question in enumerate(brief["quality_questions"])
        ]
        self.assertEqual([], self.validator.validate_brief(brief, require_review=True))
        brief["review_answers"][0]["status"] = "fail"
        self.assertIn("content-review-not-passed", {issue.code for issue in self.validator.validate_brief(brief, require_review=True)})

    def test_brief_must_match_diagram_type_and_composition(self):
        brief = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        matching = {"title": "Example", "diagram_type": "system-architecture", "layout": "board", "sections": []}
        self.assertEqual([], self.validator.validate_spec_alignment(brief, matching))
        mismatched = {"title": "Example", "diagram_type": "agent-workflow", "nodes": [], "edges": []}
        codes = {issue.code for issue in self.validator.validate_spec_alignment(brief, mismatched)}
        self.assertIn("brief-type-mismatch", codes)
        self.assertIn("brief-composition-mismatch", codes)

    def test_checked_in_example_briefs_pass_completed_review(self):
        files = sorted(EXAMPLES.glob("*.brief.json"))
        self.assertGreaterEqual(len(files), 2)
        for path in files:
            brief = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual([], self.validator.validate_brief(brief, require_review=True), path.name)

    def test_quality_questions_must_be_unique_and_profile_grounded(self):
        brief = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        brief["quality_questions"] = ["Does it look nice?", "Does it look nice?", "Is the font attractive?"]
        codes = {issue.code for issue in self.validator.validate_brief(brief)}
        self.assertIn("duplicate-quality-question", codes)
        self.assertIn("profile-quality-gap", codes)

    def test_review_evidence_must_be_concrete_and_distinct(self):
        brief = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        brief["review_answers"] = [
            {"question": question, "status": "pass", "evidence": "Verified in the rendered PNG."}
            for question in brief["quality_questions"]
        ]
        codes = {issue.code for issue in self.validator.validate_brief(brief, require_review=True)}
        self.assertIn("weak-review-evidence", codes)
        self.assertIn("duplicate-review-evidence", codes)

    def test_reviewed_cli_requires_a_bound_spec(self):
        self.assertEqual(1, self.validator.main([str(TEMPLATE), "--reviewed"]))


if __name__ == "__main__":
    unittest.main()
