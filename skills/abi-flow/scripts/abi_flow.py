#!/usr/bin/env python3
"""VisualSpec: deterministic, dependency-free diagram renderer."""

from __future__ import annotations

import argparse
import html
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.parse import urlparse


NODE_TYPES = {"process", "decision", "input", "document", "database", "agent", "external"}
EDGE_KINDS = {"primary", "control", "feedback", "async", "success", "error"}
THEMES = {"paper", "notion", "spectrum", "blueprint", "terminal"}
DIRECTIONS = {"LR", "TB"}
BRAND_COLOR_FIELDS = {"primary", "accent", "page", "surface", "ink", "muted", "hair", "group", "group_stroke"}
DIAGRAM_TYPES = {
    "system-architecture": "系统架构图 / System Architecture",
    "agent-workflow": "Agent 工作流 / Agent Workflow",
    "data-flow": "数据流图 / Data Flow",
    "capability-map": "产品能力地图 / Capability Map",
    "user-flow": "用户流程图 / User Flow",
    "system-topology": "系统拓扑图 / System Topology",
    "decision-tree": "决策图 / Decision Tree",
    "roadmap": "Roadmap / Delivery Roadmap",
    "strategy-map": "战略图 / Strategy Map",
    "process-flow": "流程图 / Process Flow",
}
ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?$")
ALLOWED_LINK_SCHEMES = {"http", "https", "mailto"}
TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"

EDGE_LABELS = {
    "primary": "Primary flow",
    "control": "Control / trigger",
    "feedback": "Feedback / iteration",
    "async": "Async / event",
    "success": "Success branch",
    "error": "Error branch",
}

def visual_tokens(surface: str, hair: str, group: str) -> Dict[str, str]:
    tokens: Dict[str, str] = {}
    for node_type in NODE_TYPES:
        tokens[f"node-{node_type}"] = surface
        tokens[f"node-{node_type}-stroke"] = hair
    for index in range(6):
        tokens[f"group-tone-{index}"] = group
    return tokens


THEME_TOKENS = {
    "paper": {
        "page": "#f8f7f3", "surface": "#fffefa", "ink": "#111827",
        "muted": "#667085", "hair": "#dddcd4", "group": "#eef6ff",
        "group_stroke": "#93c5fd", "shadow": "#0f172a18",
        **visual_tokens("#fffefa", "#dddcd4", "#eef6ff"),
    },
    "notion": {
        "page": "#ffffff", "surface": "#ffffff", "ink": "#191919",
        "muted": "#6b6b6b", "hair": "#dedede", "group": "#f7f7f5",
        "group_stroke": "#b8b8b3", "shadow": "#0f172a12",
        **visual_tokens("#ffffff", "#dedede", "#f7f7f5"),
    },
    "spectrum": {
        "page": "#ffffff", "surface": "#ffffff", "ink": "#172033",
        "muted": "#526071", "hair": "#d7e0ea", "group": "#f8fafc",
        "group_stroke": "#c7d2e0", "shadow": "#31537a18",
        **visual_tokens("#ffffff", "#d7e0ea", "#f8fafc"),
        "node-process": "#eff6ff", "node-process-stroke": "#60a5fa",
        "node-decision": "#fff7ed", "node-decision-stroke": "#fb923c",
        "node-input": "#fdf4ff", "node-input-stroke": "#d946ef",
        "node-document": "#f0fdf4", "node-document-stroke": "#4ade80",
        "node-database": "#ecfeff", "node-database-stroke": "#22d3ee",
        "node-agent": "#f5f3ff", "node-agent-stroke": "#8b5cf6",
        "node-external": "#f8fafc", "node-external-stroke": "#94a3b8",
        "group-tone-0": "#eff6ff", "group-tone-1": "#ecfeff",
        "group-tone-2": "#f5f3ff", "group-tone-3": "#fff7ed",
        "group-tone-4": "#f0fdf4", "group-tone-5": "#fff1f2",
    },
    "blueprint": {
        "page": "#0b1930", "surface": "#102544", "ink": "#f4f8ff",
        "muted": "#a9bdd8", "hair": "#32547f", "group": "#122d52",
        "group_stroke": "#4f83bd", "shadow": "#00000042",
        **visual_tokens("#102544", "#32547f", "#122d52"),
    },
    "terminal": {
        "page": "#0c1117", "surface": "#141b22", "ink": "#f0f6fc",
        "muted": "#9da7b3", "hair": "#303a45", "group": "#111f1b",
        "group_stroke": "#2d6a57", "shadow": "#0000004f",
        **visual_tokens("#141b22", "#303a45", "#111f1b"),
    },
}

DARK_TOKENS = {
    "page": "#0c1117", "surface": "#151b23", "ink": "#f8fafc",
    "muted": "#a8b3c2", "hair": "#334155", "group": "#16253a",
    "group_stroke": "#42648f", "shadow": "#00000055",
    **visual_tokens("#151b23", "#334155", "#16253a"),
}

EDGE_COLORS = {
    "primary": "#2563eb", "control": "#ea580c", "feedback": "#7c3aed",
    "async": "#64748b", "success": "#059669", "error": "#dc2626",
}

BOARD_LAYOUT = "board"
BOARD_TONES = {
    "blue": {"bg": "#F4F8FF", "panel": "#FFFFFF", "stroke": "#7FB2F5", "ink": "#0B4F93", "icon": "#246BCE"},
    "purple": {"bg": "#FAF7FF", "panel": "#FFFFFF", "stroke": "#B69AE9", "ink": "#5226A5", "icon": "#6D3BC3"},
    "green": {"bg": "#F5FBF5", "panel": "#FFFFFF", "stroke": "#86C98A", "ink": "#176A31", "icon": "#23863B"},
    "orange": {"bg": "#FFF9F3", "panel": "#FFFFFF", "stroke": "#F2B36F", "ink": "#783A05", "icon": "#A94F08"},
    "teal": {"bg": "#F2FBFA", "panel": "#FFFFFF", "stroke": "#73C7BA", "ink": "#0D665C", "icon": "#128579"},
    "slate": {"bg": "#F7F8FA", "panel": "#FFFFFF", "stroke": "#B8C1CC", "ink": "#354052", "icon": "#536174"},
    "amber": {"bg": "#FFFBF0", "panel": "#FFFFFF", "stroke": "#E8C46D", "ink": "#8A5A08", "icon": "#A86F0A"},
}
BOARD_BLOCK_KINDS = {"grid", "banner", "list"}
BOARD_ICON_NAMES = {
    "agent", "api", "archive", "brain", "calendar", "chat", "check", "cloud", "code",
    "database", "desktop", "document", "folder", "gateway", "graph", "image", "laptop",
    "layers", "lock", "mail", "metrics", "model", "note", "phone", "prompt", "robot",
    "schema", "search", "shield", "spark", "stream", "sync", "terminal", "test", "user",
}


def resolve_visual_tokens(spec: Dict[str, Any]) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Resolve a preset plus a small, injection-safe brand-token override."""
    tokens = dict(THEME_TOKENS[spec.get("theme", "paper")])
    edges = dict(EDGE_COLORS)
    brand = spec.get("brand", {})
    if not isinstance(brand, dict):
        return tokens, edges
    for field in BRAND_COLOR_FIELDS:
        value = brand.get(field)
        if not isinstance(value, str) or not HEX_COLOR_RE.fullmatch(value):
            continue
        if field == "primary":
            edges["primary"] = value
            tokens["node-agent-stroke"] = value
        elif field == "accent":
            tokens["group_stroke"] = value
        else:
            tokens[field] = value
            if field == "surface":
                for node_type in NODE_TYPES:
                    tokens[f"node-{node_type}"] = value
            elif field == "hair":
                for node_type in NODE_TYPES:
                    tokens[f"node-{node_type}-stroke"] = value
    return tokens, edges


@dataclass
class Issue:
    level: str
    code: str
    message: str

    def as_dict(self) -> Dict[str, str]:
        return {"level": self.level, "code": self.code, "message": self.message}


@dataclass
class Box:
    node_id: str
    x: float
    y: float
    w: float
    h: float
    rank: int
    lines: List[str]

    @property
    def left(self) -> float:
        return self.x

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def top(self) -> float:
        return self.y

    @property
    def bottom(self) -> float:
        return self.y + self.h

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2


Point = Tuple[float, float]


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def display_units(text: str) -> int:
    units = 0
    for char in text:
        units += 2 if unicodedata.east_asian_width(char) in {"W", "F", "A"} else 1
    return units


def wrap_text(text: str, max_units: int) -> List[str]:
    text = " ".join(str(text).split())
    if not text:
        return []
    lines: List[str] = []
    current = ""
    current_units = 0
    for char in text:
        char_units = display_units(char)
        if current and current_units + char_units > max_units:
            break_at = current.rfind(" ")
            if break_at > max(3, len(current) // 2):
                carry = current[break_at + 1:] + char
                current = current[:break_at]
                lines.append(current.rstrip())
                current = carry.lstrip()
                current_units = display_units(current)
            else:
                lines.append(current.rstrip())
                current = char.lstrip()
                current_units = display_units(current)
        else:
            current += char
            current_units += char_units
    if current:
        lines.append(current.rstrip())
    return lines


def safe_link(link: str) -> bool:
    if link.startswith("#"):
        return bool(link[1:])
    parsed = urlparse(link)
    scheme = parsed.scheme.lower()
    if scheme in {"http", "https"}:
        return bool(parsed.netloc)
    if scheme == "mailto":
        return bool(parsed.path)
    return False


def load_spec(path: Path) -> Tuple[Dict[str, Any], List[Issue]]:
    issues: List[Issue] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}, [Issue("error", "file-not-found", f"Input file not found: {path}")]
    except json.JSONDecodeError as exc:
        return {}, [Issue("error", "invalid-json", f"JSON parse error at line {exc.lineno}: {exc.msg}")]
    if not isinstance(data, dict):
        return {}, [Issue("error", "invalid-root", "Specification root must be an object")]
    issues.extend(validate_spec(data))
    return data, issues


def load_json_object(path: Path) -> Tuple[Dict[str, Any], List[Issue]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}, [Issue("error", "file-not-found", f"Input file not found: {path}")]
    except json.JSONDecodeError as exc:
        return {}, [Issue("error", "invalid-json", f"JSON parse error at line {exc.lineno}: {exc.msg}")]
    if not isinstance(data, dict):
        return {}, [Issue("error", "invalid-root", "JSON root must be an object")]
    return data, []


def validate_workspace(workspace: Dict[str, Any]) -> List[Issue]:
    issues: List[Issue] = []
    allowed = {"$schema", "schema_version", "title", "entry_view", "views"}
    for key in sorted(set(workspace) - allowed):
        issues.append(Issue("warning", "unknown-workspace-field", f"Unknown workspace field: {key}"))
    if workspace.get("schema_version") != "3.0":
        issues.append(Issue("error", "invalid-workspace-version", "schema_version must be 3.0"))
    if not isinstance(workspace.get("title"), str) or not workspace.get("title", "").strip():
        issues.append(Issue("error", "missing-workspace-title", "workspace title must be non-empty"))
    views = workspace.get("views")
    if not isinstance(views, list) or not views:
        return issues + [Issue("error", "missing-views", "views must be a non-empty array")]
    view_ids: List[str] = []
    for index, view in enumerate(views):
        if not isinstance(view, dict):
            issues.append(Issue("error", "invalid-view", f"views[{index}] must be an object"))
            continue
        view_id = view.get("id")
        if not isinstance(view_id, str) or not ID_RE.fullmatch(view_id):
            issues.append(Issue("error", "invalid-view-id", f"views[{index}].id is invalid"))
        elif view_id in view_ids:
            issues.append(Issue("error", "duplicate-view-id", f"Duplicate view id: {view_id}"))
        else:
            view_ids.append(view_id)
    if workspace.get("entry_view") not in view_ids:
        issues.append(Issue("error", "unknown-entry-view", "entry_view must reference an existing view"))
    for index, view in enumerate(views):
        if not isinstance(view, dict):
            continue
        view_id = view.get("id", f"views[{index}]")
        view_format = view.get("format")
        if view_format == "visualspec":
            diagram = {key: value for key, value in view.items() if key not in {"id", "format", "layout_mode"}}
            diagram["nodes"] = [
                {key: value for key, value in node.items() if key != "position"}
                if isinstance(node, dict) else node
                for node in diagram.get("nodes", [])
            ]
            for issue in validate_spec(diagram):
                issues.append(Issue(issue.level, issue.code, f"View {view_id!r}: {issue.message}"))
            for node in view.get("nodes", []):
                if not isinstance(node, dict):
                    continue
                child_view = node.get("child_view")
                if child_view is not None and child_view not in view_ids:
                    issues.append(Issue("error", "unknown-child-view", f"View {view_id!r} node {node.get('id')!r} references unknown child view {child_view!r}"))
        elif view_format == "mermaid":
            if not isinstance(view.get("title"), str) or not view.get("title", "").strip():
                issues.append(Issue("error", "missing-view-title", f"Mermaid view {view_id!r} title must be non-empty"))
            if not isinstance(view.get("source"), str) or not view.get("source", "").strip():
                issues.append(Issue("error", "missing-mermaid-source", f"Mermaid view {view_id!r} source must be non-empty"))
        else:
            issues.append(Issue("error", "invalid-view-format", f"View {view_id!r} format must be visualspec or mermaid"))
    return issues


def validate_board_spec(spec: Dict[str, Any]) -> List[Issue]:
    """Validate the high-density enterprise infographic composition."""
    issues: List[Issue] = []
    allowed_top = {
        "title", "subtitle", "diagram_type", "layout", "theme", "brand", "sections",
        "connections", "flow", "principles",
    }
    for key in sorted(set(spec) - allowed_top):
        issues.append(Issue("warning", "unknown-field", f"Unknown board field: {key}"))
    if not isinstance(spec.get("title"), str) or not spec.get("title", "").strip():
        issues.append(Issue("error", "missing-title", "title must be a non-empty string"))
    if "subtitle" in spec and not isinstance(spec["subtitle"], str):
        issues.append(Issue("error", "invalid-subtitle", "subtitle must be a string"))
    if spec.get("layout") != BOARD_LAYOUT:
        issues.append(Issue("error", "invalid-board-layout", "board specifications must use layout: board"))
    if spec.get("diagram_type", "system-architecture") not in DIAGRAM_TYPES:
        issues.append(Issue("error", "invalid-diagram-type", f"diagram_type must be one of: {', '.join(sorted(DIAGRAM_TYPES))}"))
    if spec.get("theme", "paper") not in THEMES:
        issues.append(Issue("error", "invalid-theme", f"theme must be one of: {', '.join(sorted(THEMES))}"))

    brand = spec.get("brand")
    if brand is not None:
        if not isinstance(brand, dict):
            issues.append(Issue("error", "invalid-brand", "brand must be an object"))
        else:
            unknown_brand = sorted(set(brand) - ({"name"} | BRAND_COLOR_FIELDS))
            for field in unknown_brand:
                issues.append(Issue("warning", "unknown-brand-field", f"Unknown brand field: {field}"))
            if "name" in brand and (not isinstance(brand["name"], str) or not brand["name"].strip()):
                issues.append(Issue("error", "invalid-brand-name", "brand.name must be a non-empty string"))
            for field in BRAND_COLOR_FIELDS:
                if field in brand and (not isinstance(brand[field], str) or not HEX_COLOR_RE.fullmatch(brand[field])):
                    issues.append(Issue("error", "invalid-brand-color", f"brand.{field} must be a six- or eight-digit hex color"))

    sections = spec.get("sections")
    if not isinstance(sections, list) or not sections:
        return issues + [Issue("error", "missing-sections", "board sections must be a non-empty array")]
    if len(sections) > 9:
        issues.append(Issue("warning", "too-many-sections", "A board should contain at most nine scan bands"))

    ids: List[str] = []
    for section_index, section in enumerate(sections):
        if not isinstance(section, dict):
            issues.append(Issue("error", "invalid-section", f"sections[{section_index}] must be an object"))
            continue
        section_id = section.get("id")
        if not isinstance(section_id, str) or not ID_RE.fullmatch(section_id):
            issues.append(Issue("error", "invalid-section-id", f"sections[{section_index}].id is invalid"))
        elif section_id in ids:
            issues.append(Issue("error", "duplicate-board-id", f"Duplicate board id: {section_id}"))
        else:
            ids.append(section_id)
        if not isinstance(section.get("label"), str) or not section.get("label", "").strip():
            issues.append(Issue("error", "missing-section-label", f"sections[{section_index}].label must be non-empty"))
        elif display_units(section["label"]) > 32:
            issues.append(Issue("warning", "long-section-label", f"sections[{section_index}].label is too long for the label rail"))
        if "subtitle" in section and not isinstance(section["subtitle"], str):
            issues.append(Issue("error", "invalid-section-subtitle", f"sections[{section_index}].subtitle must be a string"))
        if section.get("tone", "blue") not in BOARD_TONES:
            issues.append(Issue("error", "invalid-section-tone", f"sections[{section_index}].tone is unsupported"))
        blocks = section.get("blocks")
        if not isinstance(blocks, list) or not blocks:
            issues.append(Issue("error", "missing-blocks", f"sections[{section_index}].blocks must be a non-empty array"))
            continue
        if len(blocks) > 4:
            issues.append(Issue("warning", "too-many-blocks", f"Section {section_id!r} has more than four horizontal blocks"))
        for block_index, block in enumerate(blocks):
            location = f"sections[{section_index}].blocks[{block_index}]"
            if not isinstance(block, dict):
                issues.append(Issue("error", "invalid-block", f"{location} must be an object"))
                continue
            block_id = block.get("id")
            if not isinstance(block_id, str) or not ID_RE.fullmatch(block_id):
                issues.append(Issue("error", "invalid-block-id", f"{location}.id is invalid"))
            elif block_id in ids:
                issues.append(Issue("error", "duplicate-board-id", f"Duplicate board id: {block_id}"))
            else:
                ids.append(block_id)
            kind = block.get("kind", "grid")
            if kind not in BOARD_BLOCK_KINDS:
                issues.append(Issue("error", "invalid-block-kind", f"{location}.kind must be grid, banner, or list"))
            block_icon = block.get("icon")
            if block_icon is not None and block_icon not in BOARD_ICON_NAMES:
                issues.append(Issue("error", "invalid-block-icon", f"{location}.icon is unsupported"))
            span = block.get("span", 1)
            if not isinstance(span, int) or isinstance(span, bool) or not 1 <= span <= 8:
                issues.append(Issue("error", "invalid-block-span", f"{location}.span must be an integer from 1 to 8"))
            if kind in {"grid", "banner"} and (not isinstance(block.get("title"), str) or not block.get("title", "").strip()):
                issues.append(Issue("error", "missing-block-title", f"{location}.title must be non-empty"))
            elif isinstance(block.get("title"), str) and display_units(block["title"]) > 52:
                issues.append(Issue("warning", "long-block-title", f"{location}.title is too long for a single-line block heading"))
            for field in ("subtitle", "footer"):
                if field in block and not isinstance(block[field], str):
                    issues.append(Issue("error", f"invalid-block-{field}", f"{location}.{field} must be a string"))
            if kind == "grid":
                columns = block.get("columns", 3)
                if not isinstance(columns, int) or isinstance(columns, bool) or not 1 <= columns <= 7:
                    issues.append(Issue("error", "invalid-grid-columns", f"{location}.columns must be an integer from 1 to 7"))
                cards = block.get("cards")
                if not isinstance(cards, list) or not cards:
                    issues.append(Issue("error", "missing-grid-cards", f"{location}.cards must be a non-empty array"))
                    continue
                for card_index, card in enumerate(cards):
                    card_location = f"{location}.cards[{card_index}]"
                    if not isinstance(card, dict):
                        issues.append(Issue("error", "invalid-card", f"{card_location} must be an object"))
                        continue
                    card_id = card.get("id")
                    if not isinstance(card_id, str) or not ID_RE.fullmatch(card_id):
                        issues.append(Issue("error", "invalid-card-id", f"{card_location}.id is invalid"))
                    elif card_id in ids:
                        issues.append(Issue("error", "duplicate-board-id", f"Duplicate board id: {card_id}"))
                    else:
                        ids.append(card_id)
                    if not isinstance(card.get("label"), str) or not card.get("label", "").strip():
                        issues.append(Issue("error", "missing-card-label", f"{card_location}.label must be non-empty"))
                    elif display_units(card["label"]) > 28:
                        issues.append(Issue("warning", "long-card-label", f"{card_location}.label is too long; use subtitle or split the card"))
                    if "subtitle" in card and not isinstance(card["subtitle"], str):
                        issues.append(Issue("error", "invalid-card-subtitle", f"{card_location}.subtitle must be a string"))
                    elif display_units(card.get("subtitle", "")) > 34:
                        issues.append(Issue("warning", "long-card-subtitle", f"{card_location}.subtitle is too long for one line"))
                    icon = card.get("icon", "layers")
                    if icon not in BOARD_ICON_NAMES:
                        issues.append(Issue("error", "invalid-card-icon", f"{card_location}.icon is unsupported"))
            elif kind == "list":
                if not isinstance(block.get("title"), str) or not block.get("title", "").strip():
                    issues.append(Issue("error", "missing-block-title", f"{location}.title must be non-empty"))
                items = block.get("items")
                if not isinstance(items, list) or not items or any(not isinstance(item, str) or not item.strip() for item in items):
                    issues.append(Issue("error", "invalid-list-items", f"{location}.items must be a non-empty array of strings"))
                elif any(display_units(item) > 40 for item in items):
                    issues.append(Issue("warning", "long-list-item", f"{location}.items contains text too long for the side list"))

    connections = spec.get("connections", [])
    if not isinstance(connections, list):
        issues.append(Issue("error", "invalid-connections", "connections must be an array"))
        connections = []
    for index, connection in enumerate(connections):
        if not isinstance(connection, dict):
            issues.append(Issue("error", "invalid-connection", f"connections[{index}] must be an object"))
            continue
        source, target = connection.get("source"), connection.get("target")
        if source not in ids:
            issues.append(Issue("error", "unknown-board-source", f"connections[{index}] references unknown source {source!r}"))
        if target not in ids:
            issues.append(Issue("error", "unknown-board-target", f"connections[{index}] references unknown target {target!r}"))
        if connection.get("kind", "primary") not in EDGE_KINDS:
            issues.append(Issue("error", "invalid-edge-kind", f"connections[{index}].kind is unsupported"))
        if "label" in connection and not isinstance(connection["label"], str):
            issues.append(Issue("error", "invalid-connection-label", f"connections[{index}].label must be a string"))
        elif display_units(connection.get("label", "")) > 24:
            issues.append(Issue("warning", "long-connection-label", f"connections[{index}].label is too long for an edge label"))
        if "bidirectional" in connection and not isinstance(connection["bidirectional"], bool):
            issues.append(Issue("error", "invalid-bidirectional", f"connections[{index}].bidirectional must be boolean"))

    flow = spec.get("flow")
    if flow is not None:
        if not isinstance(flow, dict) or not isinstance(flow.get("steps"), list) or len(flow.get("steps", [])) < 2:
            issues.append(Issue("error", "invalid-board-flow", "flow must contain at least two steps"))
        else:
            if not isinstance(flow.get("label"), str) or not flow.get("label", "").strip():
                issues.append(Issue("error", "invalid-flow-label", "flow.label must be a non-empty string"))
            if flow.get("tone", "amber") not in BOARD_TONES:
                issues.append(Issue("error", "invalid-flow-tone", "flow.tone is unsupported"))
            for index, step in enumerate(flow["steps"]):
                if not isinstance(step, dict) or not isinstance(step.get("label"), str) or not step.get("label", "").strip():
                    issues.append(Issue("error", "invalid-flow-step", f"flow.steps[{index}] must contain a label"))
                    continue
                if display_units(step["label"]) > 24:
                    issues.append(Issue("warning", "long-flow-label", f"flow.steps[{index}].label is too long"))
                if "subtitle" in step and not isinstance(step["subtitle"], str):
                    issues.append(Issue("error", "invalid-flow-subtitle", f"flow.steps[{index}].subtitle must be a string"))
                elif display_units(step.get("subtitle", "")) > 32:
                    issues.append(Issue("warning", "long-flow-subtitle", f"flow.steps[{index}].subtitle is too long"))
                if step.get("icon", "check") not in BOARD_ICON_NAMES:
                    issues.append(Issue("error", "invalid-flow-icon", f"flow.steps[{index}].icon is unsupported"))
    principles = spec.get("principles")
    if principles is not None:
        if not isinstance(principles, list) or not principles:
            issues.append(Issue("error", "invalid-principles", "principles must be a non-empty array"))
        else:
            for index, principle in enumerate(principles):
                if not isinstance(principle, dict) or not isinstance(principle.get("label"), str) or not principle.get("label", "").strip():
                    issues.append(Issue("error", "invalid-principle", f"principles[{index}] must contain a label"))
                    continue
                if display_units(principle["label"]) > 24:
                    issues.append(Issue("warning", "long-principle-label", f"principles[{index}].label is too long"))
                if "subtitle" in principle and not isinstance(principle["subtitle"], str):
                    issues.append(Issue("error", "invalid-principle-subtitle", f"principles[{index}].subtitle must be a string"))
                elif display_units(principle.get("subtitle", "")) > 32:
                    issues.append(Issue("warning", "long-principle-subtitle", f"principles[{index}].subtitle is too long"))
                if principle.get("icon", "check") not in BOARD_ICON_NAMES:
                    issues.append(Issue("error", "invalid-principle-icon", f"principles[{index}].icon is unsupported"))
    return issues


def validate_spec(spec: Dict[str, Any]) -> List[Issue]:
    if spec.get("layout") == BOARD_LAYOUT:
        return validate_board_spec(spec)
    issues: List[Issue] = []
    allowed_top = {"title", "subtitle", "diagram_type", "direction", "layout", "theme", "brand", "nodes", "edges", "groups", "lanes", "legend"}
    for key in sorted(set(spec) - allowed_top):
        issues.append(Issue("warning", "unknown-field", f"Unknown top-level field: {key}"))
    if not isinstance(spec.get("title"), str) or not spec.get("title", "").strip():
        issues.append(Issue("error", "missing-title", "title must be a non-empty string"))
    if spec.get("direction", "LR") not in DIRECTIONS:
        issues.append(Issue("error", "invalid-direction", "direction must be LR or TB"))
    if spec.get("layout", "graph") != "graph":
        issues.append(Issue("error", "invalid-layout", "layout must be graph or board"))
    if spec.get("theme", "paper") not in THEMES:
        issues.append(Issue("error", "invalid-theme", f"theme must be one of: {', '.join(sorted(THEMES))}"))
    if spec.get("diagram_type", "process-flow") not in DIAGRAM_TYPES:
        issues.append(Issue("error", "invalid-diagram-type", f"diagram_type must be one of: {', '.join(sorted(DIAGRAM_TYPES))}"))
    brand = spec.get("brand")
    if brand is not None:
        if not isinstance(brand, dict):
            issues.append(Issue("error", "invalid-brand", "brand must be an object"))
        else:
            unknown_brand = sorted(set(brand) - ({"name"} | BRAND_COLOR_FIELDS))
            for field in unknown_brand:
                issues.append(Issue("warning", "unknown-brand-field", f"Unknown brand field: {field}"))
            if "name" in brand and (not isinstance(brand["name"], str) or not brand["name"].strip()):
                issues.append(Issue("error", "invalid-brand-name", "brand.name must be a non-empty string"))
            for field in BRAND_COLOR_FIELDS:
                if field in brand and (not isinstance(brand[field], str) or not HEX_COLOR_RE.fullmatch(brand[field])):
                    issues.append(Issue("error", "invalid-brand-color", f"brand.{field} must be a six- or eight-digit hex color"))

    nodes = spec.get("nodes")
    edges = spec.get("edges")
    groups = spec.get("groups", [])
    lanes = spec.get("lanes", [])
    if not isinstance(nodes, list) or not nodes:
        issues.append(Issue("error", "missing-nodes", "nodes must be a non-empty array"))
        nodes = []
    if not isinstance(edges, list):
        issues.append(Issue("error", "missing-edges", "edges must be an array"))
        edges = []
    if not isinstance(groups, list):
        issues.append(Issue("error", "invalid-groups", "groups must be an array"))
        groups = []
    if not isinstance(lanes, list):
        issues.append(Issue("error", "invalid-lanes", "lanes must be an array"))
        lanes = []

    node_ids: List[str] = []
    group_ids: List[str] = []
    lane_ids: List[str] = []
    for index, group in enumerate(groups):
        if not isinstance(group, dict):
            issues.append(Issue("error", "invalid-group", f"groups[{index}] must be an object"))
            continue
        group_id = group.get("id")
        if not isinstance(group_id, str) or not ID_RE.fullmatch(group_id):
            issues.append(Issue("error", "invalid-group-id", f"groups[{index}].id is invalid"))
        elif group_id in group_ids:
            issues.append(Issue("error", "duplicate-group-id", f"Duplicate group id: {group_id}"))
        else:
            group_ids.append(group_id)
        if not isinstance(group.get("label"), str) or not group.get("label", "").strip():
            issues.append(Issue("error", "missing-group-label", f"groups[{index}].label must be non-empty"))

    lane_orders = set()
    for index, lane in enumerate(lanes):
        if not isinstance(lane, dict):
            issues.append(Issue("error", "invalid-lane", f"lanes[{index}] must be an object"))
            continue
        lane_id = lane.get("id")
        if not isinstance(lane_id, str) or not ID_RE.fullmatch(lane_id):
            issues.append(Issue("error", "invalid-lane-id", f"lanes[{index}].id is invalid"))
        elif lane_id in lane_ids:
            issues.append(Issue("error", "duplicate-lane-id", f"Duplicate lane id: {lane_id}"))
        else:
            lane_ids.append(lane_id)
        if not isinstance(lane.get("label"), str) or not lane.get("label", "").strip():
            issues.append(Issue("error", "missing-lane-label", f"lanes[{index}].label must be non-empty"))
        order = lane.get("order", index)
        if not isinstance(order, int) or isinstance(order, bool) or order < 0:
            issues.append(Issue("error", "invalid-lane-order", f"lanes[{index}].order must be a non-negative integer"))
        elif order in lane_orders:
            issues.append(Issue("warning", "duplicate-lane-order", f"Multiple lanes use order {order}"))
        lane_orders.add(order)

    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            issues.append(Issue("error", "invalid-node", f"nodes[{index}] must be an object"))
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or not ID_RE.fullmatch(node_id):
            issues.append(Issue("error", "invalid-node-id", f"nodes[{index}].id is invalid"))
        elif node_id in node_ids:
            issues.append(Issue("error", "duplicate-node-id", f"Duplicate node id: {node_id}"))
        else:
            node_ids.append(node_id)
        if not isinstance(node.get("label"), str) or not node.get("label", "").strip():
            issues.append(Issue("error", "missing-node-label", f"nodes[{index}].label must be non-empty"))
        node_type = node.get("type", "process")
        if node_type not in NODE_TYPES:
            issues.append(Issue("error", "invalid-node-type", f"Node {node_id!r} has unsupported type {node_type!r}"))
        group_id = node.get("group")
        if group_id is not None and group_id not in group_ids:
            issues.append(Issue("error", "unknown-group", f"Node {node_id!r} references unknown group {group_id!r}"))
        lane_id = node.get("lane")
        if lane_id is not None and lane_id not in lane_ids:
            issues.append(Issue("error", "unknown-lane", f"Node {node_id!r} references unknown lane {lane_id!r}"))
        if lane_ids and lane_id is None:
            issues.append(Issue("error", "missing-lane", f"Node {node_id!r} is not assigned to a swimlane"))
        rank = node.get("rank")
        if rank is not None and (not isinstance(rank, int) or isinstance(rank, bool) or rank < 0):
            issues.append(Issue("error", "invalid-rank", f"Node {node_id!r} rank must be a non-negative integer"))
        child_view = node.get("child_view")
        if child_view is not None and (not isinstance(child_view, str) or not ID_RE.fullmatch(child_view)):
            issues.append(Issue("error", "invalid-child-view", f"Node {node_id!r} child_view must be a valid id"))
        link = node.get("link")
        if link is not None and (not isinstance(link, str) or not safe_link(link)):
            issues.append(Issue("error", "unsafe-link", f"Node {node_id!r} has a disallowed or malformed link"))
        if display_units(str(node.get("label", ""))) > 52:
            issues.append(Issue("warning", "long-label", f"Node {node_id!r} label is unusually long; use subtitle or split the node"))

    used_groups = {node.get("group") for node in nodes if isinstance(node, dict) and node.get("group")}
    for group_id in group_ids:
        if group_id not in used_groups:
            issues.append(Issue("error", "empty-group", f"Group {group_id!r} has no nodes"))
    used_lanes = {node.get("lane") for node in nodes if isinstance(node, dict) and node.get("lane")}
    for lane_id in lane_ids:
        if lane_id not in used_lanes:
            issues.append(Issue("error", "empty-lane", f"Lane {lane_id!r} has no nodes"))

    seen_edges = set()
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            issues.append(Issue("error", "invalid-edge", f"edges[{index}] must be an object"))
            continue
        source, target = edge.get("source"), edge.get("target")
        if source not in node_ids:
            issues.append(Issue("error", "unknown-source", f"edges[{index}] references unknown source {source!r}"))
        if target not in node_ids:
            issues.append(Issue("error", "unknown-target", f"edges[{index}] references unknown target {target!r}"))
        kind = edge.get("kind", "primary")
        if kind not in EDGE_KINDS:
            issues.append(Issue("error", "invalid-edge-kind", f"edges[{index}] has unsupported kind {kind!r}"))
        signature = (source, target, kind, edge.get("label", ""))
        if signature in seen_edges:
            issues.append(Issue("warning", "duplicate-edge", f"Duplicate edge: {source!r} -> {target!r}"))
        seen_edges.add(signature)
        if display_units(str(edge.get("label", ""))) > 28:
            issues.append(Issue("warning", "long-edge-label", f"Edge {source!r} -> {target!r} label is too long"))

    if node_ids and not any(issue.level == "error" for issue in issues):
        _, cycle_nodes = calculate_ranks(nodes, edges)
        if cycle_nodes:
            issues.append(Issue("error", "unmarked-cycle", "Non-feedback edges contain a cycle involving: " + ", ".join(cycle_nodes)))
    return issues


def calculate_ranks(nodes: Sequence[Dict[str, Any]], edges: Sequence[Dict[str, Any]]) -> Tuple[Dict[str, int], List[str]]:
    ids = [node["id"] for node in nodes]
    order = {node_id: index for index, node_id in enumerate(ids)}
    outgoing: Dict[str, List[str]] = {node_id: [] for node_id in ids}
    indegree = {node_id: 0 for node_id in ids}
    for edge in edges:
        if edge.get("kind", "primary") == "feedback":
            continue
        source, target = edge["source"], edge["target"]
        outgoing[source].append(target)
        indegree[target] += 1
    queue = sorted([node_id for node_id in ids if indegree[node_id] == 0], key=order.get)
    ranks = {node_id: 0 for node_id in ids}
    visited: List[str] = []
    while queue:
        node_id = queue.pop(0)
        visited.append(node_id)
        for target in sorted(outgoing[node_id], key=order.get):
            ranks[target] = max(ranks[target], ranks[node_id] + 1)
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
                queue.sort(key=order.get)
    cycle_nodes = [node_id for node_id in ids if node_id not in visited]
    for node in nodes:
        if isinstance(node.get("rank"), int) and not isinstance(node.get("rank"), bool):
            ranks[node["id"]] = node["rank"]
    return ranks, cycle_nodes


def measure_node(node: Dict[str, Any]) -> Tuple[float, float, List[str]]:
    label_units = display_units(node.get("label", ""))
    subtitle_lines = wrap_text(node.get("subtitle", ""), 34)
    subtitle_units = max([display_units(line) for line in subtitle_lines] or [0])
    width = max(188, min(292, 52 + max(label_units * 8.2, subtitle_units * 6.2)))
    node_type = node.get("type", "process")
    if node_type == "decision":
        width = max(width, 210)
    height = 78 + max(0, len(subtitle_lines) - 1) * 16
    if node_type == "decision":
        height = max(height, 112)
    elif node_type == "database":
        height += 10
    return round(width, 1), round(height, 1), subtitle_lines


def ordered_lanes(spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    indexed = list(enumerate(spec.get("lanes", [])))
    indexed.sort(key=lambda item: (item[1].get("order", item[0]), item[0]))
    return [lane for _, lane in indexed]


def layout_graph(spec: Dict[str, Any]) -> Tuple[Dict[str, Box], Dict[str, float], Dict[str, int]]:
    nodes = spec["nodes"]
    ranks, _ = calculate_ranks(nodes, spec["edges"])
    by_rank: Dict[int, List[Dict[str, Any]]] = {}
    for node in nodes:
        by_rank.setdefault(ranks[node["id"]], []).append(node)
    measured = {node["id"]: measure_node(node) for node in nodes}
    direction = spec.get("direction", "LR")
    title_h = 118
    margin = 72
    rank_gap = 118
    node_gap = 44
    feedback_count = sum(1 for edge in spec["edges"] if edge.get("kind", "primary") == "feedback")
    kinds = {edge.get("kind", "primary") for edge in spec["edges"]}
    legend = spec.get("legend", len(kinds) > 1)
    feedback_space = 64 + max(0, feedback_count - 1) * 22 if feedback_count else 24
    legend_space = 66 if legend else 20
    boxes: Dict[str, Box] = {}
    lanes = ordered_lanes(spec)
    lane_frames: List[Dict[str, Any]] = []

    if lanes and direction == "LR":
        rank_ids = sorted(by_rank)
        widths = {rank: max(measured[node["id"]][0] for node in by_rank[rank]) for rank in rank_ids}
        content_w = sum(widths[rank] for rank in rank_ids) + rank_gap * max(0, len(rank_ids) - 1)
        canvas_w = max(1040, margin * 2 + content_w + 28)
        rank_x: Dict[int, float] = {}
        x = (canvas_w - content_w) / 2
        for rank in rank_ids:
            rank_x[rank] = x
            x += widths[rank] + rank_gap
        lane_heights: Dict[str, float] = {}
        for lane in lanes:
            lane_nodes = [node for node in nodes if node.get("lane") == lane["id"]]
            max_cell_h = 0.0
            for rank in rank_ids:
                cell = [node for node in lane_nodes if ranks[node["id"]] == rank]
                cell_h = sum(measured[node["id"]][1] for node in cell) + node_gap * max(0, len(cell) - 1)
                max_cell_h = max(max_cell_h, cell_h)
            lane_heights[lane["id"]] = max(164.0, 62 + max_cell_h + 28)
        lane_gap = 14
        content_h = sum(lane_heights.values()) + lane_gap * max(0, len(lanes) - 1)
        canvas_h = max(700, title_h + content_h + feedback_space + legend_space + margin)
        y = title_h
        for lane in lanes:
            lane_h = lane_heights[lane["id"]]
            lane_frames.append({"id": lane["id"], "label": lane["label"], "x": margin - 22, "y": y, "w": canvas_w - (margin - 22) * 2, "h": lane_h, "orientation": "horizontal"})
            lane_nodes = [node for node in nodes if node.get("lane") == lane["id"]]
            for rank in rank_ids:
                cell = [node for node in lane_nodes if ranks[node["id"]] == rank]
                cell_h = sum(measured[node["id"]][1] for node in cell) + node_gap * max(0, len(cell) - 1)
                node_y = y + 54 + max(0, (lane_h - 54 - cell_h) / 2)
                for node in cell:
                    w, h, lines = measured[node["id"]]
                    boxes[node["id"]] = Box(node["id"], rank_x[rank] + (widths[rank] - w) / 2, node_y, w, h, rank, lines)
                    node_y += h + node_gap
            y += lane_h + lane_gap
    elif lanes and direction == "TB":
        rank_ids = sorted(by_rank)
        heights = {rank: max(measured[node["id"]][1] for node in by_rank[rank]) for rank in rank_ids}
        content_h = sum(heights[rank] for rank in rank_ids) + rank_gap * max(0, len(rank_ids) - 1)
        rank_y: Dict[int, float] = {}
        y = title_h + 42
        for rank in rank_ids:
            rank_y[rank] = y
            y += heights[rank] + rank_gap
        lane_widths: Dict[str, float] = {}
        for lane in lanes:
            lane_nodes = [node for node in nodes if node.get("lane") == lane["id"]]
            max_cell_w = 0.0
            for rank in rank_ids:
                cell = [node for node in lane_nodes if ranks[node["id"]] == rank]
                cell_w = sum(measured[node["id"]][0] for node in cell) + node_gap * max(0, len(cell) - 1)
                max_cell_w = max(max_cell_w, cell_w)
            lane_widths[lane["id"]] = max(280.0, max_cell_w + 52)
        lane_gap = 14
        content_w = sum(lane_widths.values()) + lane_gap * max(0, len(lanes) - 1)
        canvas_w = max(1040, margin * 2 + content_w + feedback_space)
        canvas_h = max(760, title_h + 42 + content_h + legend_space + margin)
        x = (canvas_w - content_w) / 2
        for lane in lanes:
            lane_w = lane_widths[lane["id"]]
            lane_frames.append({"id": lane["id"], "label": lane["label"], "x": x, "y": title_h, "w": lane_w, "h": content_h + 78, "orientation": "vertical"})
            lane_nodes = [node for node in nodes if node.get("lane") == lane["id"]]
            for rank in rank_ids:
                cell = [node for node in lane_nodes if ranks[node["id"]] == rank]
                cell_w = sum(measured[node["id"]][0] for node in cell) + node_gap * max(0, len(cell) - 1)
                node_x = x + (lane_w - cell_w) / 2
                for node in cell:
                    w, h, lines = measured[node["id"]]
                    boxes[node["id"]] = Box(node["id"], node_x, rank_y[rank] + (heights[rank] - h) / 2, w, h, rank, lines)
                    node_x += w + node_gap
            x += lane_w + lane_gap
    elif direction == "LR":
        widths = {rank: max(measured[node["id"]][0] for node in rank_nodes) for rank, rank_nodes in by_rank.items()}
        heights = {
            rank: sum(measured[node["id"]][1] for node in rank_nodes) + node_gap * max(0, len(rank_nodes) - 1)
            for rank, rank_nodes in by_rank.items()
        }
        content_h = max(heights.values())
        content_w = sum(widths[rank] for rank in sorted(by_rank)) + rank_gap * max(0, len(by_rank) - 1)
        canvas_w = max(960, margin * 2 + content_w)
        canvas_h = max(620, title_h + content_h + feedback_space + legend_space + margin)
        x = (canvas_w - content_w) / 2
        for rank in sorted(by_rank):
            column_h = heights[rank]
            y = title_h + (content_h - column_h) / 2
            for node in by_rank[rank]:
                w, h, lines = measured[node["id"]]
                boxes[node["id"]] = Box(node["id"], x + (widths[rank] - w) / 2, y, w, h, rank, lines)
                y += h + node_gap
            x += widths[rank] + rank_gap
    else:
        row_widths = {
            rank: sum(measured[node["id"]][0] for node in rank_nodes) + node_gap * max(0, len(rank_nodes) - 1)
            for rank, rank_nodes in by_rank.items()
        }
        row_heights = {rank: max(measured[node["id"]][1] for node in rank_nodes) for rank, rank_nodes in by_rank.items()}
        content_w = max(row_widths.values())
        content_h = sum(row_heights[rank] for rank in sorted(by_rank)) + rank_gap * max(0, len(by_rank) - 1)
        canvas_w = max(960, margin * 2 + content_w + feedback_space)
        canvas_h = max(700, title_h + content_h + legend_space + margin)
        y = title_h
        for rank in sorted(by_rank):
            row_w = row_widths[rank]
            x = (canvas_w - row_w) / 2
            for node in by_rank[rank]:
                w, h, lines = measured[node["id"]]
                boxes[node["id"]] = Box(node["id"], x, y + (row_heights[rank] - h) / 2, w, h, rank, lines)
                x += w + node_gap
            y += row_heights[rank] + rank_gap

    canvas = {
        "width": round(canvas_w, 1), "height": round(canvas_h, 1),
        "title_h": title_h, "margin": margin,
        "content_bottom": max(box.bottom for box in boxes.values()),
        "content_right": max(box.right for box in boxes.values()),
        "legend": 1 if legend else 0,
        "lanes": lane_frames,
    }
    return boxes, canvas, ranks


def route_edges(spec: Dict[str, Any], boxes: Dict[str, Box], canvas: Dict[str, float]) -> List[Dict[str, Any]]:
    direction = spec.get("direction", "LR")
    routes: List[Dict[str, Any]] = []
    feedback_index = 0
    long_index = 0
    for index, edge in enumerate(spec["edges"]):
        source = boxes[edge["source"]]
        target = boxes[edge["target"]]
        kind = edge.get("kind", "primary")
        if source.node_id == target.node_id:
            points = [
                (source.right, source.cy), (source.right + 34, source.cy),
                (source.right + 34, source.top - 28), (source.cx, source.top - 28),
                (source.cx, source.top),
            ]
        elif direction == "LR" and kind == "feedback":
            lane = canvas["content_bottom"] + 38 + feedback_index * 22
            outer_x = canvas["content_right"] + 28 + feedback_index * 10
            target_lane = target.left - 28 - feedback_index * 8
            feedback_index += 1
            points = [
                (source.right, source.cy), (outer_x, source.cy),
                (outer_x, lane), (target_lane, lane),
                (target_lane, target.cy), (target.left, target.cy),
            ]
        elif direction == "TB" and kind == "feedback":
            lane = canvas["content_right"] + 38 + feedback_index * 22
            outer_y = canvas["content_bottom"] + 28 + feedback_index * 10
            target_lane = target.top - 28 - feedback_index * 8
            feedback_index += 1
            points = [
                (source.cx, source.bottom), (source.cx, outer_y),
                (lane, outer_y), (lane, target_lane),
                (target.cx, target_lane), (target.cx, target.top),
            ]
        elif direction == "LR":
            start, end = (source.right, source.cy), (target.left, target.cy)
            if target.rank == source.rank + 1:
                corridor = (start[0] + end[0]) / 2
                points = [start, (corridor, start[1]), (corridor, end[1]), end]
            else:
                lane = canvas["title_h"] - 22 - long_index * 15
                long_index += 1
                points = [start, (start[0] + 24, start[1]), (start[0] + 24, lane), (end[0] - 24, lane), (end[0] - 24, end[1]), end]
        else:
            start, end = (source.cx, source.bottom), (target.cx, target.top)
            if target.rank == source.rank + 1:
                corridor = (start[1] + end[1]) / 2
                points = [start, (start[0], corridor), (end[0], corridor), end]
            else:
                lane = 42 + long_index * 18
                long_index += 1
                points = [start, (start[0], start[1] + 24), (lane, start[1] + 24), (lane, end[1] - 24), (end[0], end[1] - 24), end]
        routes.append({"index": index, "edge": edge, "points": dedupe_points(points)})
    return routes


def dedupe_points(points: Sequence[Point]) -> List[Point]:
    result: List[Point] = []
    for point in points:
        rounded = (round(point[0], 1), round(point[1], 1))
        if not result or rounded != result[-1]:
            result.append(rounded)
    return result


def segments(points: Sequence[Point]) -> Iterable[Tuple[Point, Point]]:
    for index in range(len(points) - 1):
        yield points[index], points[index + 1]


def segment_hits_box(a: Point, b: Point, box: Box, inset: float = 2.0) -> bool:
    left, right = box.left + inset, box.right - inset
    top, bottom = box.top + inset, box.bottom - inset
    if math.isclose(a[0], b[0]):
        x = a[0]
        low, high = sorted((a[1], b[1]))
        return left < x < right and max(low, top) < min(high, bottom)
    if math.isclose(a[1], b[1]):
        y = a[1]
        low, high = sorted((a[0], b[0]))
        return top < y < bottom and max(low, left) < min(high, right)
    return False


def crossing(a1: Point, a2: Point, b1: Point, b2: Point) -> Optional[Point]:
    a_vert = math.isclose(a1[0], a2[0])
    b_vert = math.isclose(b1[0], b2[0])
    if a_vert == b_vert:
        return None
    vertical = (a1, a2) if a_vert else (b1, b2)
    horizontal = (b1, b2) if a_vert else (a1, a2)
    x = vertical[0][0]
    y = horizontal[0][1]
    if min(vertical[0][1], vertical[1][1]) < y < max(vertical[0][1], vertical[1][1]) and min(horizontal[0][0], horizontal[1][0]) < x < max(horizontal[0][0], horizontal[1][0]):
        return (x, y)
    return None


def geometry_issues(routes: Sequence[Dict[str, Any]], boxes: Dict[str, Box]) -> List[Issue]:
    issues: List[Issue] = []
    for route in routes:
        edge = route["edge"]
        excluded = {edge["source"], edge["target"]}
        for node_id, box in boxes.items():
            if node_id in excluded:
                continue
            if any(segment_hits_box(a, b, box) for a, b in segments(route["points"])):
                issues.append(Issue("error", "edge-node-collision", f"Edge {edge['source']} -> {edge['target']} crosses node {node_id}"))
    for left_index, left in enumerate(routes):
        for right in routes[left_index + 1:]:
            left_edge, right_edge = left["edge"], right["edge"]
            if {left_edge["source"], left_edge["target"]} & {right_edge["source"], right_edge["target"]}:
                continue
            found = False
            for a1, a2 in segments(left["points"]):
                for b1, b2 in segments(right["points"]):
                    if crossing(a1, a2, b1, b2):
                        found = True
                        break
                if found:
                    break
            if found:
                issues.append(Issue("warning", "edge-crossing", f"Edges {left_edge['source']} -> {left_edge['target']} and {right_edge['source']} -> {right_edge['target']} cross"))
    return issues


def path_data(points: Sequence[Point]) -> str:
    commands = [f"M {points[0][0]:g} {points[0][1]:g}"]
    for x, y in points[1:]:
        commands.append(f"L {x:g} {y:g}")
    return " ".join(commands)


def label_position(points: Sequence[Point]) -> Tuple[float, float]:
    candidates = []
    for a, b in segments(points):
        length = abs(a[0] - b[0]) + abs(a[1] - b[1])
        candidates.append((length, (a[0] + b[0]) / 2, (a[1] + b[1]) / 2, math.isclose(a[1], b[1])))
    _, x, y, horizontal = max(candidates)
    return x, y - 8 if horizontal else y


def group_boxes(spec: Dict[str, Any], boxes: Dict[str, Box]) -> List[Dict[str, Any]]:
    results = []
    for group in spec.get("groups", []):
        members = [boxes[node["id"]] for node in spec["nodes"] if node.get("group") == group["id"]]
        pad_x, pad_top, pad_bottom = 24, 38, 24
        results.append({
            "id": group["id"], "label": group["label"],
            "x": min(box.left for box in members) - pad_x,
            "y": min(box.top for box in members) - pad_top,
            "w": max(box.right for box in members) - min(box.left for box in members) + pad_x * 2,
            "h": max(box.bottom for box in members) - min(box.top for box in members) + pad_top + pad_bottom,
        })
    return results


def group_geometry_issues(spec: Dict[str, Any], boxes: Dict[str, Box]) -> List[Issue]:
    issues: List[Issue] = []
    groups = group_boxes(spec, boxes)
    members = {
        group["id"]: {node["id"] for node in spec["nodes"] if node.get("group") == group["id"]}
        for group in spec.get("groups", [])
    }
    for index, left in enumerate(groups):
        for right in groups[index + 1:]:
            if max(left["x"], right["x"]) < min(left["x"] + left["w"], right["x"] + right["w"]) and max(left["y"], right["y"]) < min(left["y"] + left["h"], right["y"] + right["h"]):
                issues.append(Issue("error", "group-overlap", f"Groups {left['id']!r} and {right['id']!r} overlap"))
    for group in groups:
        for node_id, box in boxes.items():
            if node_id in members[group["id"]]:
                continue
            if group["x"] < box.cx < group["x"] + group["w"] and group["y"] < box.cy < group["y"] + group["h"]:
                issues.append(Issue("error", "group-intrusion", f"Node {node_id!r} appears inside unrelated group {group['id']!r}"))
    return issues


def node_shape(node: Dict[str, Any], box: Box) -> str:
    x, y, w, h = box.x, box.y, box.w, box.h
    node_type = node.get("type", "process")
    common = f'class="node-shape {node_type}"'
    if node_type == "decision":
        return f'<path {common} d="M {box.cx:g} {y:g} L {box.right:g} {box.cy:g} L {box.cx:g} {box.bottom:g} L {x:g} {box.cy:g} Z"/>'
    if node_type == "input":
        skew = 18
        return f'<path {common} d="M {x + skew:g} {y:g} H {box.right:g} L {box.right - skew:g} {box.bottom:g} H {x:g} Z"/>'
    if node_type == "document":
        fold = 18
        return (
            f'<path {common} d="M {x:g} {y:g} H {box.right - fold:g} L {box.right:g} {y + fold:g} '
            f'V {box.bottom - 9:g} Q {box.cx:g} {box.bottom + 7:g} {x:g} {box.bottom - 9:g} Z"/>'
            f'<path class="node-detail" d="M {box.right - fold:g} {y:g} V {y + fold:g} H {box.right:g}"/>'
        )
    if node_type == "database":
        ry = 12
        return (
            f'<path {common} d="M {x:g} {y + ry:g} C {x:g} {y - 2:g} {box.right:g} {y - 2:g} {box.right:g} {y + ry:g} '
            f'V {box.bottom - ry:g} C {box.right:g} {box.bottom + 2:g} {x:g} {box.bottom + 2:g} {x:g} {box.bottom - ry:g} Z"/>'
            f'<ellipse class="node-detail" cx="{box.cx:g}" cy="{y + ry:g}" rx="{w / 2:g}" ry="{ry:g}"/>'
        )
    outer = f'<rect {common} x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="13"/>'
    if node_type == "agent":
        outer += f'<rect class="agent-inner" x="{x + 5:g}" y="{y + 5:g}" width="{w - 10:g}" height="{h - 10:g}" rx="9"/>'
    return outer


def render_node(node: Dict[str, Any], box: Box) -> str:
    label_y = box.cy - (10 if box.lines else 0)
    if node.get("type") == "database":
        label_y += 3
    text = [f'<g class="node" id="node-{esc(node["id"])}">', node_shape(node, box)]
    text.append(f'<text class="node-title" x="{box.cx:g}" y="{label_y:g}">{esc(node["label"])}</text>')
    for index, line in enumerate(box.lines):
        text.append(f'<text class="node-subtitle" x="{box.cx:g}" y="{label_y + 22 + index * 16:g}">{esc(line)}</text>')
    text.append('</g>')
    body = "".join(text)
    link = node.get("link")
    if link:
        return f'<a class="node-link" href="{esc(link)}" target="_blank" rel="noopener noreferrer" aria-label="Open {esc(node["label"])}">{body}</a>'
    return body


def css_variables(tokens: Dict[str, str]) -> str:
    return ";".join(f"--{key}:{value}" for key, value in tokens.items())


def render_svg(spec: Dict[str, Any], boxes: Dict[str, Box], canvas: Dict[str, float], routes: Sequence[Dict[str, Any]]) -> str:
    width, height = canvas["width"], canvas["height"]
    theme = spec.get("theme", "paper")
    visual_tokens, edge_colors = resolve_visual_tokens(spec)
    default_mode = "dark" if theme in {"blueprint", "terminal"} else "light"
    kinds = []
    for edge in spec["edges"]:
        kind = edge.get("kind", "primary")
        if kind not in kinds:
            kinds.append(kind)
    title = esc(spec["title"])
    subtitle = esc(spec.get("subtitle", ""))
    diagram_type = spec.get("diagram_type", "process-flow")
    type_label = esc(DIAGRAM_TYPES[diagram_type])
    desc = esc(f"{DIAGRAM_TYPES[diagram_type]} with {len(spec['nodes'])} nodes and {len(spec['edges'])} edges")
    lines: List[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" class="abi-flow" data-theme="{default_mode}" viewBox="0 0 {width:g} {height:g}" role="img" aria-labelledby="abi-title abi-desc">',
        f'<title id="abi-title">{title}</title><desc id="abi-desc">{desc}</desc>',
        '<defs>',
        '<filter id="shadow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="var(--shadow)"/></filter>',
    ]
    for kind in EDGE_KINDS:
        lines.append(f'<marker id="arrow-{kind}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="var(--edge-{kind})"/></marker>')
    lines.extend(['</defs>', '<style>'])
    lines.append(f'.abi-flow{{{css_variables(visual_tokens)};' + ";".join(f"--edge-{kind}:{color}" for kind, color in edge_colors.items()) + ';font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;background:var(--page)}}')
    lines.append(f'.abi-flow[data-theme="dark"]{{{css_variables(DARK_TOKENS)}}}')
    lines.append('text{fill:var(--ink)}.page-bg{fill:var(--page)}.title{font-size:25px;font-weight:800}.subtitle{font-size:12.5px;fill:var(--muted)}.type-badge{font-size:10px;font-weight:800;fill:var(--muted);letter-spacing:.4px}.type-badge-bg{fill:var(--surface);stroke:var(--hair)}')
    lines.append('.lane-box{fill:var(--surface);stroke:var(--hair);stroke-width:1.1}.lane:nth-child(even) .lane-box{fill:var(--group)}.lane-title{font-size:12px;font-weight:850;fill:var(--muted);letter-spacing:.45px}.group-box{fill:var(--group);stroke:var(--group-stroke);stroke-width:1.2}.group.tone-0 .group-box{fill:var(--group-tone-0)}.group.tone-1 .group-box{fill:var(--group-tone-1)}.group.tone-2 .group-box{fill:var(--group-tone-2)}.group.tone-3 .group-box{fill:var(--group-tone-3)}.group.tone-4 .group-box{fill:var(--group-tone-4)}.group.tone-5 .group-box{fill:var(--group-tone-5)}.group-title{font-size:12px;font-weight:800;fill:var(--muted);letter-spacing:.5px}')
    lines.append('.node-shape{stroke-width:1.25;filter:url(#shadow)}.node-shape.process{fill:var(--node-process);stroke:var(--node-process-stroke)}.node-shape.decision{fill:var(--node-decision);stroke:var(--node-decision-stroke)}.node-shape.input{fill:var(--node-input);stroke:var(--node-input-stroke)}.node-shape.document{fill:var(--node-document);stroke:var(--node-document-stroke)}.node-shape.database{fill:var(--node-database);stroke:var(--node-database-stroke)}.node-shape.agent{fill:var(--node-agent);stroke:var(--node-agent-stroke);stroke-width:1.7}.node-shape.external{fill:var(--node-external);stroke:var(--node-external-stroke);stroke-dasharray:6 4}.agent-inner{fill:none;stroke:var(--node-agent-stroke);stroke-width:.8;opacity:.55}.node-detail{fill:none;stroke:var(--hair);stroke-width:1.1}')
    lines.append('.node-title{font-size:14.5px;font-weight:750;text-anchor:middle;dominant-baseline:middle}.node-subtitle{font-size:11.5px;fill:var(--muted);text-anchor:middle;dominant-baseline:middle}')
    lines.append('.edge{fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}.edge.async,.edge.error{stroke-dasharray:6 5}.edge.feedback{stroke-width:2.2}.edge-label-bg{fill:var(--page);stroke:var(--hair);stroke-width:.7;opacity:.97}.edge-label{font-size:10.8px;font-weight:650;text-anchor:middle;dominant-baseline:middle;fill:var(--muted)}')
    lines.append('.legend-bg{fill:var(--surface);stroke:var(--hair)}.legend-text{font-size:10.5px;fill:var(--muted)}.node-link{cursor:pointer}.node-link:focus .node-shape,.node-link:hover .node-shape{stroke:var(--edge-primary);stroke-width:2.4}.node-link:focus{outline:none}')
    lines.append('</style>')
    lines.append(f'<rect class="page-bg" width="{width:g}" height="{height:g}"/>')
    lines.append(f'<text class="title" x="{canvas["margin"]:g}" y="48">{title}</text>')
    if subtitle:
        lines.append(f'<text class="subtitle" x="{canvas["margin"]:g}" y="75">{subtitle}</text>')
    badge_w = display_units(DIAGRAM_TYPES[diagram_type]) * 5.6 + 24
    lines.append(f'<g class="diagram-type"><rect class="type-badge-bg" x="{width - canvas["margin"] - badge_w:g}" y="31" width="{badge_w:g}" height="25" rx="12.5"/><text class="type-badge" x="{width - canvas["margin"] - badge_w / 2:g}" y="47" text-anchor="middle">{type_label}</text></g>')

    for lane in canvas.get("lanes", []):
        title_x = lane["x"] + 15
        title_y = lane["y"] + 25
        lines.append(f'<g class="lane"><rect class="lane-box" x="{lane["x"]:g}" y="{lane["y"]:g}" width="{lane["w"]:g}" height="{lane["h"]:g}" rx="14"/><text class="lane-title" x="{title_x:g}" y="{title_y:g}">{esc(lane["label"])}</text></g>')

    for index, group in enumerate(group_boxes(spec, boxes)):
        lines.append(f'<g class="group tone-{index % 6}"><rect class="group-box" x="{group["x"]:g}" y="{group["y"]:g}" width="{group["w"]:g}" height="{group["h"]:g}" rx="16"/><text class="group-title" x="{group["x"] + 14:g}" y="{group["y"] + 21:g}">{esc(group["label"])}</text></g>')

    for route in routes:
        edge = route["edge"]
        kind = edge.get("kind", "primary")
        lines.append(f'<path class="edge {kind}" style="stroke:var(--edge-{kind})" d="{path_data(route["points"])}" marker-end="url(#arrow-{kind})"/>')

    node_map = {node["id"]: node for node in spec["nodes"]}
    for node_id in [node["id"] for node in spec["nodes"]]:
        lines.append(render_node(node_map[node_id], boxes[node_id]))

    for route in routes:
        label = str(route["edge"].get("label", "")).strip()
        if not label:
            continue
        x, y = label_position(route["points"])
        label_w = max(36, display_units(label) * 6.3 + 14)
        lines.append(f'<g class="edge-label-group"><rect class="edge-label-bg" x="{x - label_w / 2:g}" y="{y - 10:g}" width="{label_w:g}" height="20" rx="7"/><text class="edge-label" x="{x:g}" y="{y:g}">{esc(label)}</text></g>')

    if canvas["legend"]:
        item_w = 148
        legend_w = min(width - canvas["margin"] * 2, item_w * len(kinds) + 24)
        start_x = (width - legend_w) / 2
        y = height - 48
        lines.append(f'<g class="legend"><rect class="legend-bg" x="{start_x:g}" y="{y - 18:g}" width="{legend_w:g}" height="36" rx="12"/>')
        for index, kind in enumerate(kinds):
            x = start_x + 18 + index * item_w
            dash = ' stroke-dasharray="6 5"' if kind in {"async", "error"} else ''
            lines.append(f'<path d="M {x:g} {y:g} H {x + 24:g}" stroke="var(--edge-{kind})" stroke-width="2"{dash}/><text class="legend-text" x="{x + 32:g}" y="{y + 4:g}">{esc(EDGE_LABELS[kind])}</text>')
        lines.append('</g>')
    lines.append('</svg>')
    return "\n".join(lines)


def board_block_height(block: Dict[str, Any]) -> float:
    kind = block.get("kind", "grid")
    if kind == "banner":
        return 72.0
    if kind == "list":
        return 48.0 + len(block.get("items", [])) * 22.0 + 16.0
    columns = max(1, int(block.get("columns", 3)))
    rows = max(1, math.ceil(len(block.get("cards", [])) / columns))
    header = 38.0 if str(block.get("title", "")).strip() else 0.0
    footer = 31.0 if str(block.get("footer", "")).strip() else 0.0
    return 24.0 + header + rows * 54.0 + max(0, rows - 1) * 8.0 + footer


def layout_board(spec: Dict[str, Any]) -> Tuple[Dict[str, Box], Dict[str, Any], List[Dict[str, Any]]]:
    width = 1800.0
    outer_x, outer_w = 20.0, width - 40.0
    rail_w, gap = 184.0, 12.0
    content_x = outer_x + rail_w + 12.0
    content_w = outer_w - rail_w - 24.0
    y = 96.0
    section_gap = 12.0
    anchors: Dict[str, Box] = {}
    leaf_boxes: Dict[str, Box] = {}
    section_frames: List[Dict[str, Any]] = []

    for section_index, section in enumerate(spec.get("sections", [])):
        blocks = section["blocks"]
        measured = [board_block_height(block) for block in blocks]
        inner_h = max(measured)
        section_h = inner_h + 24.0
        frame = {
            "spec": section, "x": outer_x, "y": y, "w": outer_w, "h": section_h,
            "content_x": content_x, "content_w": content_w, "blocks": [],
        }
        anchors[section["id"]] = Box(section["id"], outer_x, y, outer_w, section_h, section_index, [])
        spans = [block.get("span", 1) for block in blocks]
        usable_w = content_w - gap * max(0, len(blocks) - 1)
        cursor_x = content_x
        allocated = 0.0
        for block_index, (block, span) in enumerate(zip(blocks, spans)):
            if block_index == len(blocks) - 1:
                block_w = content_x + content_w - cursor_x
            else:
                block_w = usable_w * span / sum(spans)
                allocated += block_w
            block_y = y + 12.0 + max(0.0, (inner_h - measured[block_index]) / 2.0)
            block_h = measured[block_index]
            block_frame = {"spec": block, "x": cursor_x, "y": block_y, "w": block_w, "h": block_h, "cards": []}
            frame["blocks"].append(block_frame)
            anchors[block["id"]] = Box(block["id"], cursor_x, block_y, block_w, block_h, section_index, [])

            if block.get("kind", "grid") == "grid":
                cards = block.get("cards", [])
                columns = min(max(1, int(block.get("columns", 3))), max(1, len(cards)))
                header = 38.0 if str(block.get("title", "")).strip() else 0.0
                card_gap = 8.0
                card_w = (block_w - 24.0 - card_gap * max(0, columns - 1)) / columns
                card_y = block_y + 12.0 + header
                for card_index, card in enumerate(cards):
                    row, column = divmod(card_index, columns)
                    card_x = cursor_x + 12.0 + column * (card_w + card_gap)
                    current_y = card_y + row * 62.0
                    box = Box(card["id"], card_x, current_y, card_w, 54.0, section_index, [])
                    leaf_boxes[card["id"]] = box
                    anchors[card["id"]] = box
                    block_frame["cards"].append({"spec": card, "box": box})
            cursor_x += block_w + gap
        section_frames.append(frame)
        y += section_h + section_gap

    flow_frame = None
    flow = spec.get("flow")
    if isinstance(flow, dict) and flow.get("steps"):
        flow_frame = {"spec": flow, "x": outer_x, "y": y, "w": outer_w, "h": 98.0, "steps": []}
        step_gap = 10.0
        steps = flow["steps"]
        step_w = (content_w - step_gap * max(0, len(steps) - 1)) / len(steps)
        for index, step in enumerate(steps):
            box = Box(f"flow-{index}", content_x + index * (step_w + step_gap), y + 15.0, step_w, 68.0, index, [])
            flow_frame["steps"].append({"spec": step, "box": box})
            leaf_boxes[box.node_id] = box
        y += 98.0 + section_gap

    principles_frame = None
    principles = spec.get("principles")
    if isinstance(principles, list) and principles:
        principles_frame = {"items": principles, "x": outer_x, "y": y, "w": outer_w, "h": 108.0, "cards": []}
        card_gap = 10.0
        card_w = (content_w - card_gap * max(0, len(principles) - 1)) / len(principles)
        for index, principle in enumerate(principles):
            box = Box(f"principle-{index}", content_x + index * (card_w + card_gap), y + 15.0, card_w, 78.0, index, [])
            principles_frame["cards"].append({"spec": principle, "box": box})
            leaf_boxes[box.node_id] = box
        y += 108.0

    canvas = {
        "width": width, "height": round(y + 22.0, 1), "margin": 42.0, "title_h": 96.0,
        "sections": section_frames, "flow": flow_frame, "principles": principles_frame,
        "rail_w": rail_w, "content_x": content_x, "content_w": content_w, "anchors": anchors,
        "legend": 0, "content_bottom": y, "content_right": width - 20.0,
    }
    routes = route_board_connections(spec, anchors)
    return leaf_boxes, canvas, routes


def route_board_connections(spec: Dict[str, Any], anchors: Dict[str, Box]) -> List[Dict[str, Any]]:
    routes: List[Dict[str, Any]] = []
    for index, connection in enumerate(spec.get("connections", [])):
        source = anchors[connection["source"]]
        target = anchors[connection["target"]]
        if target.top >= source.bottom:
            start_x = min(max(source.cx, target.left + 14.0), target.right - 14.0)
            start = (start_x, source.bottom)
            end = (start_x, target.top)
            points = [start, end]
        elif source.top >= target.bottom:
            start_x = min(max(source.cx, target.left + 14.0), target.right - 14.0)
            start = (start_x, source.top)
            end = (start_x, target.bottom)
            points = [start, end]
        elif target.left >= source.right:
            start, end = (source.right, source.cy), (target.left, target.cy)
            corridor = (start[0] + end[0]) / 2.0
            points = [start, (corridor, start[1]), (corridor, end[1]), end]
        else:
            start, end = (source.left, source.cy), (target.right, target.cy)
            corridor = (start[0] + end[0]) / 2.0
            points = [start, (corridor, start[1]), (corridor, end[1]), end]
        edge = {
            "source": connection["source"], "target": connection["target"],
            "kind": connection.get("kind", "primary"), "label": connection.get("label", ""),
            "bidirectional": bool(connection.get("bidirectional", False)),
        }
        routes.append({"index": index, "edge": edge, "points": dedupe_points(points)})
    return routes


def board_icon(name: str, x: float, y: float, size: float, color: str) -> str:
    scale = size / 24.0
    common = f'fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"'
    icons = {
        "phone": '<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/>',
        "laptop": '<rect x="4" y="4" width="16" height="13" rx="1.5"/><path d="M2 20h20M8 20h8"/>',
        "desktop": '<rect x="3" y="3" width="18" height="13" rx="1.5"/><path d="M12 16v5M8 21h8"/>',
        "terminal": '<rect x="3" y="4" width="18" height="16" rx="3"/><path d="m7 9 3 3-3 3M13 15h4"/>',
        "gateway": '<path d="M9 18H6a4 4 0 0 1 0-8h1M15 6h3a4 4 0 0 1 0 8h-1M8 12h8"/>',
        "api": '<path d="M4 8h16M4 16h16M8 4v16M16 4v16"/>',
        "note": '<path d="M5 3h11l3 3v15H5zM16 3v4h4M8 11h8M8 15h6"/>',
        "document": '<path d="M6 2h9l4 4v16H6zM15 2v5h5M9 12h7M9 16h7"/>',
        "search": '<circle cx="10" cy="10" r="6"/><path d="m15 15 6 6M7 10h6M10 7v6"/>',
        "graph": '<circle cx="5" cy="12" r="2"/><circle cx="18" cy="5" r="2"/><circle cx="19" cy="18" r="2"/><path d="m7 11 9-5M7 13l10 4M18 7v9"/>',
        "brain": '<path d="M9 4a3 3 0 0 0-5 2 3 3 0 0 0 0 5 3 3 0 0 0 2 5 3 3 0 0 0 3 4M15 4a3 3 0 0 1 5 2 3 3 0 0 1 0 5 3 3 0 0 1-2 5 3 3 0 0 1-3 4M9 4v16M15 4v16M9 8h3M12 12h3M9 16h3"/>',
        "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 2v6M17 2v6M3 10h18M7 14h3M14 14h3M7 18h3"/>',
        "chat": '<path d="M4 4h16v12H9l-5 4zM8 9h8M8 13h5"/>',
        "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m4 7 8 6 8-6"/>',
        "folder": '<path d="M3 6h7l2 3h9v11H3z"/>',
        "database": '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
        "code": '<path d="m9 7-5 5 5 5M15 7l5 5-5 5M13 4l-2 16"/>',
        "prompt": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="m7 9 3 3-3 3M12 15h5"/>',
        "test": '<path d="M9 3h6M10 3v5l-5 9a3 3 0 0 0 3 4h8a3 3 0 0 0 3-4l-5-9V3M8 15h8"/>',
        "archive": '<rect x="3" y="5" width="18" height="4" rx="1"/><path d="M5 9v11h14V9M9 13h6"/>',
        "lock": '<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3M12 14v3"/>',
        "cloud": '<path d="M7 19h11a4 4 0 0 0 .4-8 7 7 0 0 0-13.3-1.7A5 5 0 0 0 7 19z"/>',
        "sync": '<path d="M20 7v5h-5M4 17v-5h5M18 12a7 7 0 0 0-12-4l-2 2M6 12a7 7 0 0 0 12 4l2-2"/>',
        "shield": '<path d="M12 2 20 5v6c0 5-3.5 9-8 11-4.5-2-8-6-8-11V5zM8 12l3 3 5-6"/>',
        "check": '<circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 6-7"/>',
        "robot": '<rect x="4" y="7" width="16" height="13" rx="3"/><path d="M12 3v4M9 12h.1M15 12h.1M8 16h8M2 11h2M20 11h2"/>',
        "agent": '<circle cx="12" cy="9" r="4"/><path d="M4 21a8 8 0 0 1 16 0M18 4l1 1 2-2"/>',
        "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
        "schema": '<rect x="3" y="3" width="7" height="6" rx="1"/><rect x="14" y="15" width="7" height="6" rx="1"/><path d="M10 6h5a3 3 0 0 1 3 3v6M7 9v6a3 3 0 0 0 3 3h4"/>',
        "stream": '<path d="M3 7h12a3 3 0 1 0-3-3M3 12h16a3 3 0 1 1-3 3M3 17h8"/>',
        "metrics": '<path d="M4 20V10M10 20V4M16 20v-7M22 20V7M2 20h21"/>',
        "model": '<path d="m12 2 8 5-8 5-8-5zM4 12l8 5 8-5M4 17l8 5 8-5"/>',
        "spark": '<path d="m12 2 1.7 5.3L19 9l-5.3 1.7L12 16l-1.7-5.3L5 9l5.3-1.7zM19 16l.8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8z"/>',
        "layers": '<path d="m12 3 9 5-9 5-9-5zM3 13l9 5 9-5M3 18l9 5 9-5"/>',
        "image": '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m4 17 5-5 4 4 3-3 4 4"/>',
    }
    body = icons.get(name, icons["layers"])
    body = body.replace("<path ", '<path fill="none" ').replace("<rect ", '<rect fill="none" ').replace("<circle ", '<circle fill="none" ').replace("<ellipse ", '<ellipse fill="none" ')
    return f'<g transform="translate({x:g} {y:g}) scale({scale:g})" {common}>{body}</g>'


def render_board_svg(spec: Dict[str, Any], canvas: Dict[str, Any], routes: Sequence[Dict[str, Any]]) -> str:
    width, height = canvas["width"], canvas["height"]
    _, edge_colors = resolve_visual_tokens(spec)
    primary = spec.get("brand", {}).get("primary", "#246BCE") if isinstance(spec.get("brand"), dict) else "#246BCE"
    title = esc(spec["title"])
    subtitle = esc(spec.get("subtitle", ""))
    desc = esc(f"High-density {DIAGRAM_TYPES[spec.get('diagram_type', 'system-architecture')]} with {len(spec.get('sections', []))} sections")
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" class="abi-flow board" data-theme="light" viewBox="0 0 {width:g} {height:g}" role="img" aria-labelledby="abi-title abi-desc">',
        f'<title id="abi-title">{title}</title><desc id="abi-desc">{desc}</desc>',
        '<defs>',
    ]
    for kind in EDGE_KINDS:
        color = edge_colors[kind]
        lines.append(f'<marker id="arrow-{kind}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker>')
    lines.extend([
        '</defs>',
        '<style>',
        '.board{font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;background:#fff}.board text{fill:#192132}.board-title{font-size:28px;font-weight:700;text-anchor:middle}.board-subtitle{font-size:12px;fill:#667085;text-anchor:middle;letter-spacing:.2px}.section-label{font-size:16px;font-weight:700}.section-subtitle{font-size:11px;font-weight:500}.block-title{font-size:15px;font-weight:700;text-anchor:middle}.block-subtitle{font-size:10.5px;fill:#667085;text-anchor:middle}.card-title{font-size:12.2px;font-weight:650}.card-subtitle{font-size:9.6px;fill:#536174}.list-title{font-size:13px;font-weight:700}.list-item{font-size:10.6px}.footer-text{font-size:10.5px;font-weight:650;text-anchor:middle}.flow-title,.principles-title{font-size:15px;font-weight:700}.step-title{font-size:11.4px;font-weight:650}.step-subtitle{font-size:9.2px;fill:#667085}.connection{fill:none;stroke-width:1.55;stroke-linecap:round;stroke-linejoin:round}.connection-label{font-size:9.5px;font-weight:650;text-anchor:middle;fill:#536174}',
        '</style>',
        f'<rect width="{width:g}" height="{height:g}" fill="#FFFFFF"/>',
        f'<rect x="0" y="0" width="{width:g}" height="84" fill="#FBFCFE"/>',
        f'<rect x="{width / 2 - 34:g}" y="77" width="68" height="3" rx="1.5" fill="{primary}"/>',
        f'<text class="board-title" x="{width / 2:g}" y="39">{title}</text>',
    ])
    if subtitle:
        lines.append(f'<text class="board-subtitle" x="{width / 2:g}" y="64">{subtitle}</text>')

    for frame in canvas["sections"]:
        section = frame["spec"]
        tone = BOARD_TONES[section.get("tone", "blue")]
        lines.append(f'<g class="board-section"><rect x="{frame["x"]:g}" y="{frame["y"]:g}" width="{frame["w"]:g}" height="{frame["h"]:g}" rx="12" fill="{tone["bg"]}" stroke="{tone["stroke"]}" stroke-width="1"/>')
        label_lines = wrap_text(section["label"], 19)[:2]
        label_y = frame["y"] + frame["h"] / 2 - (8 if len(label_lines) > 1 else 0)
        for index, label_line in enumerate(label_lines):
            lines.append(f'<text class="section-label" x="{frame["x"] + 20:g}" y="{label_y + index * 20:g}" fill="{tone["ink"]}">{esc(label_line)}</text>')
        section_subtitle = str(section.get("subtitle", "")).strip()
        if section_subtitle:
            lines.append(f'<text class="section-subtitle" x="{frame["x"] + 20:g}" y="{label_y + len(label_lines) * 20 + 3:g}" fill="{tone["ink"]}">{esc(section_subtitle)}</text>')
        lines.append(f'<path d="M {frame["content_x"] - 10:g} {frame["y"] + 12:g} V {frame["y"] + frame["h"] - 12:g}" fill="none" stroke="{tone["stroke"]}" stroke-width=".8"/>')

        for block_frame in frame["blocks"]:
            block = block_frame["spec"]
            kind = block.get("kind", "grid")
            x, y, w, h = block_frame["x"], block_frame["y"], block_frame["w"], block_frame["h"]
            dash = ' stroke-dasharray="5 4"' if kind == "list" else ""
            lines.append(f'<g class="board-block"><rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="11" fill="{tone["panel"]}" stroke="{tone["stroke"]}" stroke-width="1"{dash}/>')
            if kind == "banner":
                icon = block.get("icon", "gateway")
                icon_x = x + w / 2 - 122.0
                icon_y = y + h / 2 - 14.0
                lines.append(board_icon(icon, icon_x, icon_y, 28.0, tone["icon"]))
                lines.append(f'<text class="block-title" x="{x + w / 2 + 8:g}" y="{y + h / 2 - 4:g}" fill="{tone["ink"]}">{esc(block["title"])}</text>')
                if block.get("subtitle"):
                    lines.append(f'<text class="block-subtitle" x="{x + w / 2 + 8:g}" y="{y + h / 2 + 17:g}">{esc(block["subtitle"])}</text>')
            elif kind == "list":
                lines.append(f'<text class="list-title" x="{x + 14:g}" y="{y + 24:g}" fill="{tone["ink"]}">{esc(block["title"])}</text>')
                for index, item in enumerate(block.get("items", [])):
                    item_y = y + 48.0 + index * 22.0
                    lines.append(board_icon("check", x + 13.0, item_y - 12.0, 13.0, tone["icon"]))
                    lines.append(f'<text class="list-item" x="{x + 34:g}" y="{item_y:g}" fill="{tone["ink"]}">{esc(item)}</text>')
            else:
                header = 38.0 if str(block.get("title", "")).strip() else 0.0
                if header:
                    lines.append(f'<text class="block-title" x="{x + w / 2:g}" y="{y + 25:g}" fill="{tone["ink"]}">{esc(block["title"])}</text>')
                for card_frame in block_frame["cards"]:
                    card, box = card_frame["spec"], card_frame["box"]
                    lines.append(f'<g class="board-card"><rect x="{box.x:g}" y="{box.y:g}" width="{box.w:g}" height="{box.h:g}" rx="8" fill="#FFFFFF" stroke="{tone["stroke"]}" stroke-width=".8"/>')
                    lines.append(board_icon(card.get("icon", "layers"), box.x + 11.0, box.y + 15.0, 23.0, tone["icon"]))
                    text_x = box.x + 42.0
                    lines.append(f'<text class="card-title" x="{text_x:g}" y="{box.y + 22:g}" fill="{tone["ink"]}">{esc(card["label"])}</text>')
                    if card.get("subtitle"):
                        lines.append(f'<text class="card-subtitle" x="{text_x:g}" y="{box.y + 40:g}">{esc(card["subtitle"])}</text>')
                    lines.append('</g>')
                footer = str(block.get("footer", "")).strip()
                if footer:
                    footer_y = y + h - 28.0
                    lines.append(f'<rect x="{x + 12:g}" y="{footer_y:g}" width="{w - 24:g}" height="19" rx="5" fill="{tone["bg"]}" stroke="{tone["stroke"]}" stroke-width=".5"/>')
                    lines.append(f'<text class="footer-text" x="{x + w / 2:g}" y="{footer_y + 13:g}" fill="{tone["ink"]}">{esc(footer)}</text>')
            lines.append('</g>')
        lines.append('</g>')

    flow_frame = canvas.get("flow")
    if flow_frame:
        flow = flow_frame["spec"]
        tone = BOARD_TONES[flow.get("tone", "amber")]
        lines.append(f'<g class="board-flow"><rect x="{flow_frame["x"]:g}" y="{flow_frame["y"]:g}" width="{flow_frame["w"]:g}" height="{flow_frame["h"]:g}" rx="12" fill="{tone["bg"]}" stroke="{tone["stroke"]}"/>')
        lines.append(f'<text class="flow-title" x="{flow_frame["x"] + 20:g}" y="{flow_frame["y"] + 54:g}" fill="{tone["ink"]}">{esc(flow.get("label", "核心数据流"))}</text>')
        for index, step_frame in enumerate(flow_frame["steps"]):
            step, box = step_frame["spec"], step_frame["box"]
            lines.append(f'<rect x="{box.x:g}" y="{box.y:g}" width="{box.w:g}" height="{box.h:g}" rx="9" fill="#FFFFFF" stroke="{tone["stroke"]}" stroke-width=".7"/>')
            lines.append(board_icon(step.get("icon", "check"), box.x + 10.0, box.y + 21.0, 24.0, tone["icon"]))
            lines.append(f'<text class="step-title" x="{box.x + 41:g}" y="{box.y + 27:g}" fill="{tone["ink"]}">{index + 1}. {esc(step["label"])}</text>')
            if step.get("subtitle"):
                lines.append(f'<text class="step-subtitle" x="{box.x + 41:g}" y="{box.y + 46:g}">{esc(step["subtitle"])}</text>')
            if index + 1 < len(flow_frame["steps"]):
                next_box = flow_frame["steps"][index + 1]["box"]
                arrow_y = box.cy
                lines.append(f'<path d="M {box.right + 2:g} {arrow_y:g} H {next_box.left - 3:g}" fill="none" stroke="{tone["icon"]}" stroke-width="1.4" marker-end="url(#arrow-control)"/>')
        lines.append('</g>')

    principles_frame = canvas.get("principles")
    if principles_frame:
        tone = BOARD_TONES["slate"]
        lines.append(f'<g class="board-principles"><rect x="{principles_frame["x"]:g}" y="{principles_frame["y"]:g}" width="{principles_frame["w"]:g}" height="{principles_frame["h"]:g}" rx="12" fill="{tone["bg"]}" stroke="{tone["stroke"]}"/>')
        lines.append(f'<text class="principles-title" x="{principles_frame["x"] + 20:g}" y="{principles_frame["y"] + 58:g}" fill="{tone["ink"]}">核心原则</text>')
        for card_frame in principles_frame["cards"]:
            principle, box = card_frame["spec"], card_frame["box"]
            lines.append(f'<rect x="{box.x:g}" y="{box.y:g}" width="{box.w:g}" height="{box.h:g}" rx="9" fill="#FFFFFF" stroke="{tone["stroke"]}" stroke-width=".7"/>')
            lines.append(board_icon(principle.get("icon", "check"), box.x + 13.0, box.y + 25.0, 25.0, tone["icon"]))
            lines.append(f'<text class="step-title" x="{box.x + 48:g}" y="{box.y + 31:g}" fill="{tone["ink"]}">{esc(principle["label"])}</text>')
            if principle.get("subtitle"):
                lines.append(f'<text class="step-subtitle" x="{box.x + 48:g}" y="{box.y + 51:g}">{esc(principle["subtitle"])}</text>')
        lines.append('</g>')

    for route in routes:
        edge = route["edge"]
        kind = edge.get("kind", "primary")
        marker_start = f' marker-start="url(#arrow-{kind})"' if edge.get("bidirectional") else ""
        lines.append(f'<path class="connection" d="{path_data(route["points"])}" fill="none" stroke="{edge_colors[kind]}" marker-end="url(#arrow-{kind})"{marker_start}/>')
        label = str(edge.get("label", "")).strip()
        if label:
            x, y = label_position(route["points"])
            lines.append(f'<text class="connection-label" x="{x:g}" y="{y - 4:g}">{esc(label)}</text>')
    lines.append('</svg>')
    return "\n".join(lines)


HTML_STYLE = """
:root{color-scheme:light dark;--shell:#f3f4f6;--panel:#fff;--text:#111827;--muted:#667085;--border:#d0d5dd}
:root[data-ui-theme="dark"]{--shell:#080d14;--panel:#111821;--text:#f8fafc;--muted:#a8b3c2;--border:#334155}
*{box-sizing:border-box}body{margin:0;background:var(--shell);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI","PingFang SC",sans-serif}
.shell{max-width:1480px;margin:0 auto;padding:20px}.toolbar{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:12px}.brand{font-weight:800;margin-right:auto}.hint{font-size:12px;color:var(--muted)}button{font:inherit;font-size:12px;font-weight:700;color:var(--text);background:var(--panel);border:1px solid var(--border);border-radius:9px;padding:7px 11px;cursor:pointer}button:hover,button:focus-visible{border-color:#2563eb;outline:2px solid transparent}.viewport{overflow:hidden;border:1px solid var(--border);border-radius:16px;background:var(--panel);box-shadow:0 8px 28px #0f172a14;touch-action:none}.viewport svg{display:block;width:100%;height:auto;min-height:520px;user-select:none}.viewport.dragging{cursor:grabbing}@media(max-width:720px){.shell{padding:8px}.hint{display:none}.viewport svg{min-height:72vh}}@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
""".strip()

HTML_SCRIPT = r"""
(() => {
  const root = document.documentElement;
  const svg = document.querySelector('.abi-flow');
  const viewport = document.querySelector('.viewport');
  const original = svg.viewBox.baseVal;
  const base = {x: original.x, y: original.y, w: original.width, h: original.height};
  let view = {...base}; let dragging = false; let last = null;
  const applyView = () => svg.setAttribute('viewBox', `${view.x} ${view.y} ${view.w} ${view.h}`);
  const zoom = (factor, cx = view.x + view.w / 2, cy = view.y + view.h / 2) => {
    const nextW = Math.max(base.w * .25, Math.min(base.w * 4, view.w * factor));
    const nextH = nextW * base.h / base.w;
    const rx = (cx - view.x) / view.w, ry = (cy - view.y) / view.h;
    view = {x: cx - nextW * rx, y: cy - nextH * ry, w: nextW, h: nextH}; applyView();
  };
  document.getElementById('zoomIn').onclick = () => zoom(.82);
  document.getElementById('zoomOut').onclick = () => zoom(1.22);
  document.getElementById('reset').onclick = () => { view = {...base}; applyView(); };
  const themeButton = document.getElementById('theme');
  if (themeButton) themeButton.onclick = () => {
    const dark = root.dataset.uiTheme !== 'dark';
    root.dataset.uiTheme = dark ? 'dark' : 'light'; svg.dataset.theme = dark ? 'dark' : 'light';
  };
  viewport.addEventListener('wheel', event => {
    event.preventDefault(); const rect = svg.getBoundingClientRect();
    const cx = view.x + (event.clientX - rect.left) / rect.width * view.w;
    const cy = view.y + (event.clientY - rect.top) / rect.height * view.h;
    zoom(event.deltaY > 0 ? 1.12 : .89, cx, cy);
  }, {passive:false});
  viewport.addEventListener('pointerdown', event => { if (event.target.closest('a')) return; dragging = true; last = event; viewport.classList.add('dragging'); viewport.setPointerCapture(event.pointerId); });
  viewport.addEventListener('pointermove', event => { if (!dragging) return; const rect = svg.getBoundingClientRect(); view.x -= (event.clientX-last.clientX)/rect.width*view.w; view.y -= (event.clientY-last.clientY)/rect.height*view.h; last=event; applyView(); });
  const endDrag = () => { dragging=false; viewport.classList.remove('dragging'); };
  viewport.addEventListener('pointerup', endDrag); viewport.addEventListener('pointercancel', endDrag);
  const basename = () => document.title.replace(/[^a-z0-9_-]+/gi,'-').replace(/^-+|-+$/g,'').toLowerCase() || 'diagram';
  const download = (blob, filename) => { const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download=filename; a.click(); setTimeout(()=>URL.revokeObjectURL(url), 1000); };
  document.getElementById('svgDownload').onclick = () => download(new Blob([new XMLSerializer().serializeToString(svg)], {type:'image/svg+xml'}), basename()+'.svg');
  document.getElementById('pngDownload').onclick = () => {
    const source = new XMLSerializer().serializeToString(svg), blob = new Blob([source], {type:'image/svg+xml'}), url=URL.createObjectURL(blob), image=new Image();
    image.onload=()=>{const scale=2, canvas=document.createElement('canvas'); canvas.width=base.w*scale; canvas.height=base.h*scale; const ctx=canvas.getContext('2d'); ctx.drawImage(image,0,0,canvas.width,canvas.height); URL.revokeObjectURL(url); canvas.toBlob(png=>download(png,basename()+'.png'),'image/png');}; image.onerror=()=>URL.revokeObjectURL(url); image.src=url;
  };
})();
""".strip()


def render_html(spec: Dict[str, Any], svg: str) -> str:
    title = esc(spec["title"])
    initial = "dark" if spec.get("layout") != BOARD_LAYOUT and spec.get("theme") in {"blueprint", "terminal"} else "light"
    theme_button = "" if spec.get("layout") == BOARD_LAYOUT else '<button id="theme" type="button">Light / dark</button>'
    return f"""<!doctype html>
<html lang="en" data-ui-theme="{initial}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src blob: data:; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'"><title>{title}</title><style>{HTML_STYLE}</style></head>
<body><main class="shell"><div class="toolbar" role="toolbar" aria-label="Diagram controls"><span class="brand">VisualSpec</span><span class="hint">Drag to pan · wheel to zoom</span><button id="zoomIn" type="button" aria-label="Zoom in">＋</button><button id="zoomOut" type="button" aria-label="Zoom out">－</button><button id="reset" type="button">Reset</button>{theme_button}<button id="svgDownload" type="button">Download SVG</button><button id="pngDownload" type="button">Download PNG</button></div><div class="viewport" tabindex="0" aria-label="Interactive diagram viewport">{svg}</div></main><script>{HTML_SCRIPT}</script></body></html>"""


def validate_svg(svg: str) -> List[Issue]:
    issues: List[Issue] = []
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as exc:
        return [Issue("error", "invalid-svg-xml", f"SVG XML parse error: {exc}")]
    marker_ids = {element.attrib.get("id") for element in root.iter() if element.tag.endswith("marker")}
    for element in root.iter():
        marker_end = element.attrib.get("marker-end", "")
        if marker_end.startswith("url(#") and marker_end.endswith(")"):
            marker_id = marker_end[5:-1]
            if marker_id not in marker_ids:
                issues.append(Issue("error", "missing-marker", f"Missing SVG marker: {marker_id}"))
    titles = [element for element in root.iter() if element.tag.endswith("title")]
    descs = [element for element in root.iter() if element.tag.endswith("desc")]
    if not titles or not descs:
        issues.append(Issue("error", "missing-accessible-name", "SVG must contain title and desc elements"))
    return issues


def build(spec: Dict[str, Any], initial_issues: Sequence[Issue]) -> Tuple[str, str, Dict[str, Any], List[Issue]]:
    issues = list(initial_issues)
    if any(issue.level == "error" for issue in issues):
        return "", "", {}, issues
    if spec.get("layout") == BOARD_LAYOUT:
        boxes, canvas, routes = layout_board(spec)
        issues.extend(geometry_issues(routes, boxes))
        svg = render_board_svg(spec, canvas, routes)
    else:
        boxes, canvas, _ = layout_graph(spec)
        routes = route_edges(spec, boxes, canvas)
        issues.extend(geometry_issues(routes, boxes))
        issues.extend(group_geometry_issues(spec, boxes))
        svg = render_svg(spec, boxes, canvas, routes)
    issues.extend(validate_svg(svg))
    quality = quality_report(spec, boxes, canvas, routes, issues)
    return svg, render_html(spec, svg), quality, issues


def quality_report(spec: Dict[str, Any], boxes: Dict[str, Box], canvas: Dict[str, float], routes: Sequence[Dict[str, Any]], issues: Sequence[Issue]) -> Dict[str, Any]:
    is_board = spec.get("layout") == BOARD_LAYOUT
    return {
        "schema_version": 2,
        "status": "passed" if not any(issue.level == "error" for issue in issues) else "failed",
        "diagram": {"title": spec.get("title"), "type": spec.get("diagram_type", "process-flow"), "layout": spec.get("layout", "graph"), "nodes": len(boxes) if is_board else len(spec.get("nodes", [])), "edges": len(spec.get("connections", [])) if is_board else len(spec.get("edges", [])), "groups": len(spec.get("sections", [])) if is_board else len(spec.get("groups", [])), "lanes": 0 if is_board else len(spec.get("lanes", [])), "direction": "TB" if is_board else spec.get("direction", "LR"), "theme": spec.get("theme", "paper"), "brand": spec.get("brand", {}).get("name") if isinstance(spec.get("brand"), dict) else None},
        "canvas": {"width": canvas.get("width"), "height": canvas.get("height")},
        "geometry": {
            "node_overlap_count": count_node_overlaps(list(boxes.values())),
            "edge_node_collision_count": sum(issue.code == "edge-node-collision" for issue in issues),
            "edge_crossing_count": sum(issue.code == "edge-crossing" for issue in issues),
            "group_overlap_count": sum(issue.code == "group-overlap" for issue in issues),
            "group_intrusion_count": sum(issue.code == "group-intrusion" for issue in issues),
            "route_segment_count": sum(len(route["points"]) - 1 for route in routes),
        },
        "issues": [issue.as_dict() for issue in issues],
        "visual_review": "pending",
    }


def count_node_overlaps(boxes: Sequence[Box]) -> int:
    count = 0
    for index, left in enumerate(boxes):
        for right in boxes[index + 1:]:
            if max(left.left, right.left) < min(left.right, right.right) and max(left.top, right.top) < min(left.bottom, right.bottom):
                count += 1
    return count


def print_issues(issues: Sequence[Issue]) -> None:
    if not issues:
        print("validation: passed")
        return
    for issue in issues:
        print(f"{issue.level}: {issue.code}: {issue.message}")
    errors = sum(issue.level == "error" for issue in issues)
    warnings = sum(issue.level == "warning" for issue in issues)
    print(f"validation: {'failed' if errors else 'passed-with-warnings'} ({errors} errors, {warnings} warnings)")


def strict_failed(issues: Sequence[Issue], strict: bool) -> bool:
    return any(issue.level == "error" or (strict and issue.level == "warning") for issue in issues)


def render_png(svg_path: Path, png_path: Path, spec: Dict[str, Any]) -> Optional[str]:
    renderer = shutil.which("rsvg-convert")
    if not renderer:
        return "rsvg-convert is unavailable; PNG export skipped"
    tokens, edge_colors = resolve_visual_tokens(spec)
    if spec.get("theme", "paper") in {"blueprint", "terminal"}:
        tokens.update(DARK_TOKENS)
    tokens.update({f"edge-{kind}": color for kind, color in edge_colors.items()})
    source = svg_path.read_text(encoding="utf-8")
    source = re.sub(r"var\(--([a-z-]+)\)", lambda match: tokens.get(match.group(1), match.group(0)), source)
    with tempfile.NamedTemporaryFile("w", suffix=".svg", encoding="utf-8", delete=False) as handle:
        handle.write(source)
        raster_svg = Path(handle.name)
    try:
        result = subprocess.run([renderer, "-w", "1920", str(raster_svg), "-o", str(png_path)], text=True, capture_output=True)
    finally:
        raster_svg.unlink(missing_ok=True)
    if result.returncode:
        return f"PNG renderer failed: {result.stderr.strip() or result.stdout.strip()}"
    return None


def command_validate(args: argparse.Namespace) -> int:
    spec, issues = load_spec(args.input)
    _, _, quality, issues = build(spec, issues)
    print_issues(issues)
    if quality:
        print(json.dumps(quality, ensure_ascii=False, indent=2))
    return 1 if strict_failed(issues, args.strict) else 0


def command_workspace_validate(args: argparse.Namespace) -> int:
    workspace, issues = load_json_object(args.input)
    if not issues:
        issues.extend(validate_workspace(workspace))
    print_issues(issues)
    if not issues:
        print(f"workspace: {workspace.get('title')} ({len(workspace.get('views', []))} views)")
    return 1 if strict_failed(issues, args.strict) else 0


def command_render(args: argparse.Namespace) -> int:
    spec, initial_issues = load_spec(args.input)
    svg, page, quality, issues = build(spec, initial_issues)
    print_issues(issues)
    if strict_failed(issues, args.strict) or not svg:
        return 1
    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    name = args.name or re.sub(r"[^a-z0-9]+", "-", str(spec["title"]).lower()).strip("-") or "diagram"
    svg_path = output_dir / f"{name}.svg"
    html_path = output_dir / f"{name}.html"
    quality_path = output_dir / f"{name}.quality.json"
    svg_path.write_text(svg + "\n", encoding="utf-8")
    html_path.write_text(page + "\n", encoding="utf-8")
    png_warning = None
    png_path = output_dir / f"{name}.png"
    if args.png:
        png_warning = render_png(svg_path, png_path, spec)
        if png_warning:
            quality["visual_review"] = "skipped: PNG renderer unavailable or failed"
            quality["issues"].append(Issue("warning", "png-export-skipped", png_warning).as_dict())
        else:
            quality["visual_review"] = "pending: inspect generated PNG"
    quality_path.write_text(json.dumps(quality, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"svg: {svg_path}")
    print(f"html: {html_path}")
    print(f"quality: {quality_path}")
    if args.png and not png_warning:
        print(f"png: {png_path}")
    if png_warning:
        print(f"warning: {png_warning}")
    return 1 if args.strict and png_warning else 0


def command_types(_: argparse.Namespace) -> int:
    for slug, label in DIAGRAM_TYPES.items():
        available = "yes" if (TEMPLATE_DIR / f"{slug}.json").exists() else "no"
        print(f"{slug:20} {label}  template={available}")
    return 0


def command_new(args: argparse.Namespace) -> int:
    template_path = TEMPLATE_DIR / f"{args.diagram_type}.json"
    if not template_path.exists():
        print(f"error: template not found for {args.diagram_type}: {template_path}", file=sys.stderr)
        return 1
    output: Path = args.output
    if output.exists() and not args.force:
        print(f"error: output already exists: {output} (pass --force to replace it)", file=sys.stderr)
        return 1
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(template_path, output)
    print(f"created: {output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="VisualSpec: render polished, validated diagrams from JSON")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate", help="Validate structure and computed geometry")
    validate.add_argument("input", type=Path)
    validate.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    validate.set_defaults(func=command_validate)
    workspace_validate = subparsers.add_parser("workspace-validate", help="Validate a multi-view browser workspace")
    workspace_validate.add_argument("input", type=Path)
    workspace_validate.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    workspace_validate.set_defaults(func=command_workspace_validate)
    render = subparsers.add_parser("render", help="Render SVG, HTML, quality JSON, and optional PNG")
    render.add_argument("input", type=Path)
    render.add_argument("--output-dir", type=Path, required=True)
    render.add_argument("--name", help="Output basename")
    render.add_argument("--png", action="store_true", help="Export a 1920 px PNG with rsvg-convert")
    render.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    render.set_defaults(func=command_render)
    types = subparsers.add_parser("types", help="List supported diagram types and starter templates")
    types.set_defaults(func=command_types)
    new = subparsers.add_parser("new", help="Create a source specification from a diagram template")
    new.add_argument("diagram_type", choices=sorted(DIAGRAM_TYPES))
    new.add_argument("--output", type=Path, required=True)
    new.add_argument("--force", action="store_true", help="Replace an existing output file")
    new.set_defaults(func=command_new)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
