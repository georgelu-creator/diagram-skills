#!/usr/bin/env python3
"""Deterministic, dependency-free SVG and HTML flowchart renderer."""

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
ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
ALLOWED_LINK_SCHEMES = {"http", "https", "mailto"}

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


def validate_spec(spec: Dict[str, Any]) -> List[Issue]:
    issues: List[Issue] = []
    allowed_top = {"title", "subtitle", "direction", "theme", "nodes", "edges", "groups", "legend"}
    for key in sorted(set(spec) - allowed_top):
        issues.append(Issue("warning", "unknown-field", f"Unknown top-level field: {key}"))
    if not isinstance(spec.get("title"), str) or not spec.get("title", "").strip():
        issues.append(Issue("error", "missing-title", "title must be a non-empty string"))
    if spec.get("direction", "LR") not in DIRECTIONS:
        issues.append(Issue("error", "invalid-direction", "direction must be LR or TB"))
    if spec.get("theme", "paper") not in THEMES:
        issues.append(Issue("error", "invalid-theme", f"theme must be one of: {', '.join(sorted(THEMES))}"))

    nodes = spec.get("nodes")
    edges = spec.get("edges")
    groups = spec.get("groups", [])
    if not isinstance(nodes, list) or not nodes:
        issues.append(Issue("error", "missing-nodes", "nodes must be a non-empty array"))
        nodes = []
    if not isinstance(edges, list):
        issues.append(Issue("error", "missing-edges", "edges must be an array"))
        edges = []
    if not isinstance(groups, list):
        issues.append(Issue("error", "invalid-groups", "groups must be an array"))
        groups = []

    node_ids: List[str] = []
    group_ids: List[str] = []
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
        link = node.get("link")
        if link is not None and (not isinstance(link, str) or not safe_link(link)):
            issues.append(Issue("error", "unsafe-link", f"Node {node_id!r} has a disallowed or malformed link"))
        if display_units(str(node.get("label", ""))) > 52:
            issues.append(Issue("warning", "long-label", f"Node {node_id!r} label is unusually long; use subtitle or split the node"))

    used_groups = {node.get("group") for node in nodes if isinstance(node, dict) and node.get("group")}
    for group_id in group_ids:
        if group_id not in used_groups:
            issues.append(Issue("error", "empty-group", f"Group {group_id!r} has no nodes"))

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

    if direction == "LR":
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
    default_mode = "dark" if theme in {"blueprint", "terminal"} else "light"
    kinds = []
    for edge in spec["edges"]:
        kind = edge.get("kind", "primary")
        if kind not in kinds:
            kinds.append(kind)
    title = esc(spec["title"])
    subtitle = esc(spec.get("subtitle", ""))
    desc = esc(f"Flowchart with {len(spec['nodes'])} nodes and {len(spec['edges'])} edges")
    lines: List[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" class="abi-flow" data-theme="{default_mode}" viewBox="0 0 {width:g} {height:g}" role="img" aria-labelledby="abi-title abi-desc">',
        f'<title id="abi-title">{title}</title><desc id="abi-desc">{desc}</desc>',
        '<defs>',
        '<filter id="shadow" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="var(--shadow)"/></filter>',
    ]
    for kind in EDGE_KINDS:
        lines.append(f'<marker id="arrow-{kind}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="var(--edge-{kind})"/></marker>')
    lines.extend(['</defs>', '<style>'])
    lines.append(f'.abi-flow{{{css_variables(THEME_TOKENS[theme])};' + ";".join(f"--edge-{kind}:{color}" for kind, color in EDGE_COLORS.items()) + ';font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;background:var(--page)}}')
    lines.append(f'.abi-flow[data-theme="dark"]{{{css_variables(DARK_TOKENS)}}}')
    lines.append('text{fill:var(--ink)}.page-bg{fill:var(--page)}.title{font-size:25px;font-weight:800}.subtitle{font-size:12.5px;fill:var(--muted)}')
    lines.append('.group-box{fill:var(--group);stroke:var(--group-stroke);stroke-width:1.2}.group.tone-0 .group-box{fill:var(--group-tone-0)}.group.tone-1 .group-box{fill:var(--group-tone-1)}.group.tone-2 .group-box{fill:var(--group-tone-2)}.group.tone-3 .group-box{fill:var(--group-tone-3)}.group.tone-4 .group-box{fill:var(--group-tone-4)}.group.tone-5 .group-box{fill:var(--group-tone-5)}.group-title{font-size:12px;font-weight:800;fill:var(--muted);letter-spacing:.5px}')
    lines.append('.node-shape{stroke-width:1.25;filter:url(#shadow)}.node-shape.process{fill:var(--node-process);stroke:var(--node-process-stroke)}.node-shape.decision{fill:var(--node-decision);stroke:var(--node-decision-stroke)}.node-shape.input{fill:var(--node-input);stroke:var(--node-input-stroke)}.node-shape.document{fill:var(--node-document);stroke:var(--node-document-stroke)}.node-shape.database{fill:var(--node-database);stroke:var(--node-database-stroke)}.node-shape.agent{fill:var(--node-agent);stroke:var(--node-agent-stroke);stroke-width:1.7}.node-shape.external{fill:var(--node-external);stroke:var(--node-external-stroke);stroke-dasharray:6 4}.agent-inner{fill:none;stroke:var(--node-agent-stroke);stroke-width:.8;opacity:.55}.node-detail{fill:none;stroke:var(--hair);stroke-width:1.1}')
    lines.append('.node-title{font-size:14.5px;font-weight:750;text-anchor:middle;dominant-baseline:middle}.node-subtitle{font-size:11.5px;fill:var(--muted);text-anchor:middle;dominant-baseline:middle}')
    lines.append('.edge{fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}.edge.async,.edge.error{stroke-dasharray:6 5}.edge.feedback{stroke-width:2.2}.edge-label-bg{fill:var(--page);stroke:var(--hair);stroke-width:.7;opacity:.97}.edge-label{font-size:10.8px;font-weight:650;text-anchor:middle;dominant-baseline:middle;fill:var(--muted)}')
    lines.append('.legend-bg{fill:var(--surface);stroke:var(--hair)}.legend-text{font-size:10.5px;fill:var(--muted)}.node-link{cursor:pointer}.node-link:focus .node-shape,.node-link:hover .node-shape{stroke:var(--edge-primary);stroke-width:2.4}.node-link:focus{outline:none}')
    lines.append('</style>')
    lines.append(f'<rect class="page-bg" width="{width:g}" height="{height:g}"/>')
    lines.append(f'<text class="title" x="{canvas["margin"]:g}" y="48">{title}</text>')
    if subtitle:
        lines.append(f'<text class="subtitle" x="{canvas["margin"]:g}" y="75">{subtitle}</text>')

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
  document.getElementById('theme').onclick = () => {
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
    initial = "dark" if spec.get("theme") in {"blueprint", "terminal"} else "light"
    return f"""<!doctype html>
<html lang="en" data-ui-theme="{initial}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src blob: data:; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'"><title>{title}</title><style>{HTML_STYLE}</style></head>
<body><main class="shell"><div class="toolbar" role="toolbar" aria-label="Diagram controls"><span class="brand">ABI Flow</span><span class="hint">Drag to pan · wheel to zoom</span><button id="zoomIn" type="button" aria-label="Zoom in">＋</button><button id="zoomOut" type="button" aria-label="Zoom out">－</button><button id="reset" type="button">Reset</button><button id="theme" type="button">Light / dark</button><button id="svgDownload" type="button">Download SVG</button><button id="pngDownload" type="button">Download PNG</button></div><div class="viewport" tabindex="0" aria-label="Interactive diagram viewport">{svg}</div></main><script>{HTML_SCRIPT}</script></body></html>"""


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
    boxes, canvas, _ = layout_graph(spec)
    routes = route_edges(spec, boxes, canvas)
    issues.extend(geometry_issues(routes, boxes))
    issues.extend(group_geometry_issues(spec, boxes))
    svg = render_svg(spec, boxes, canvas, routes)
    issues.extend(validate_svg(svg))
    quality = quality_report(spec, boxes, canvas, routes, issues)
    return svg, render_html(spec, svg), quality, issues


def quality_report(spec: Dict[str, Any], boxes: Dict[str, Box], canvas: Dict[str, float], routes: Sequence[Dict[str, Any]], issues: Sequence[Issue]) -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "status": "passed" if not any(issue.level == "error" for issue in issues) else "failed",
        "diagram": {"title": spec.get("title"), "nodes": len(spec.get("nodes", [])), "edges": len(spec.get("edges", [])), "groups": len(spec.get("groups", [])), "direction": spec.get("direction", "LR"), "theme": spec.get("theme", "paper")},
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


def render_png(svg_path: Path, png_path: Path, theme: str) -> Optional[str]:
    renderer = shutil.which("rsvg-convert")
    if not renderer:
        return "rsvg-convert is unavailable; PNG export skipped"
    tokens = dict(THEME_TOKENS[theme])
    if theme in {"blueprint", "terminal"}:
        tokens.update(DARK_TOKENS)
    tokens.update({f"edge-{kind}": color for kind, color in EDGE_COLORS.items()})
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
        png_warning = render_png(svg_path, png_path, spec.get("theme", "paper"))
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render polished, validated flowcharts from JSON")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate", help="Validate structure and computed geometry")
    validate.add_argument("input", type=Path)
    validate.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    validate.set_defaults(func=command_validate)
    render = subparsers.add_parser("render", help="Render SVG, HTML, quality JSON, and optional PNG")
    render.add_argument("input", type=Path)
    render.add_argument("--output-dir", type=Path, required=True)
    render.add_argument("--name", help="Output basename")
    render.add_argument("--png", action="store_true", help="Export a 1920 px PNG with rsvg-convert")
    render.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    render.set_defaults(func=command_render)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
