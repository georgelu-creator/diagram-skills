import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "abi-flow" / "scripts" / "abi_flow.py"
SPEC = importlib.util.spec_from_file_location("abi_flow", MODULE_PATH)
abi_flow = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
sys.modules[SPEC.name] = abi_flow
SPEC.loader.exec_module(abi_flow)


class AbiFlowTests(unittest.TestCase):
    def sample(self):
        return json.loads((ROOT / "examples" / "aurora-resilience-network.json").read_text(encoding="utf-8"))

    def test_example_passes_strict_validation(self):
        spec = self.sample()
        svg, page, report, issues = abi_flow.build(spec, abi_flow.validate_spec(spec))
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn("Interactive diagram viewport", page)
        self.assertEqual([], issues)
        self.assertEqual("passed", report["status"])
        self.assertEqual(0, report["geometry"]["node_overlap_count"])
        self.assertEqual(0, report["geometry"]["group_overlap_count"])
        self.assertEqual(0, report["geometry"]["group_intrusion_count"])

    def test_unmarked_cycle_fails(self):
        spec = {
            "title": "Cycle",
            "nodes": [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}],
            "edges": [
                {"source": "a", "target": "b", "kind": "primary"},
                {"source": "b", "target": "a", "kind": "primary"},
            ],
        }
        self.assertIn("unmarked-cycle", {issue.code for issue in abi_flow.validate_spec(spec)})

    def test_feedback_cycle_passes(self):
        spec = {
            "title": "Cycle",
            "nodes": [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}],
            "edges": [
                {"source": "a", "target": "b", "kind": "primary"},
                {"source": "b", "target": "a", "kind": "feedback"},
            ],
        }
        self.assertEqual([], abi_flow.validate_spec(spec))

    def test_rejects_executable_links(self):
        spec = {
            "title": "Unsafe",
            "nodes": [{"id": "a", "label": "A", "link": "javascript:alert(1)"}],
            "edges": [],
        }
        self.assertIn("unsafe-link", {issue.code for issue in abi_flow.validate_spec(spec)})

    def test_rejects_malformed_http_links(self):
        self.assertFalse(abi_flow.safe_link("https:example.com/no-host"))
        self.assertTrue(abi_flow.safe_link("https://example.com/path"))
        self.assertTrue(abi_flow.safe_link("#details"))

    def test_group_overlap_is_a_failure(self):
        spec = {
            "title": "Groups",
            "groups": [{"id": "g1", "label": "One"}, {"id": "g2", "label": "Two"}],
            "nodes": [
                {"id": "a", "label": "A", "group": "g1"},
                {"id": "b", "label": "B", "group": "g2"},
                {"id": "c", "label": "C", "group": "g1"}
            ],
            "edges": [
                {"source": "a", "target": "c", "kind": "primary"},
                {"source": "b", "target": "c", "kind": "primary"}
            ]
        }
        boxes, _, _ = abi_flow.layout_graph(spec)
        codes = {issue.code for issue in abi_flow.group_geometry_issues(spec, boxes)}
        self.assertTrue(codes & {"group-overlap", "group-intrusion"})

    def test_top_to_bottom_dark_theme_renders(self):
        spec = {
            "title": "Approval",
            "direction": "TB",
            "theme": "terminal",
            "nodes": [
                {"id": "request", "label": "Request", "type": "input"},
                {"id": "review", "label": "Review", "type": "decision"},
                {"id": "ship", "label": "Ship", "type": "process"}
            ],
            "edges": [
                {"source": "request", "target": "review", "kind": "primary"},
                {"source": "review", "target": "ship", "label": "yes", "kind": "success"},
                {"source": "ship", "target": "request", "label": "next", "kind": "feedback"}
            ]
        }
        svg, page, report, issues = abi_flow.build(spec, abi_flow.validate_spec(spec))
        self.assertEqual([], issues)
        self.assertIn('data-theme="dark"', svg)
        self.assertIn("Content-Security-Policy", page)
        self.assertEqual("TB", report["diagram"]["direction"])

    def test_spectrum_theme_uses_semantic_color_tokens(self):
        spec = self.sample()
        self.assertEqual("spectrum", spec["theme"])
        svg, _, _, issues = abi_flow.build(spec, abi_flow.validate_spec(spec))
        self.assertEqual([], issues)
        self.assertIn("--node-agent:#f5f3ff", svg)
        self.assertIn("--node-database:#ecfeff", svg)
        self.assertIn('class="group tone-5"', svg)

    def test_schema_is_valid_json(self):
        schema = json.loads((ROOT / "skills" / "abi-flow" / "references" / "spec.schema.json").read_text(encoding="utf-8"))
        self.assertEqual("object", schema["type"])

    def test_enterprise_board_renders_high_density_infographic(self):
        spec = json.loads((ROOT / "examples" / "enterprise-agent-office.json").read_text(encoding="utf-8"))
        svg, page, report, issues = abi_flow.build(spec, abi_flow.validate_spec(spec))
        self.assertEqual([], issues)
        self.assertEqual("board", report["diagram"]["layout"])
        self.assertEqual(5, report["diagram"]["groups"])
        self.assertGreaterEqual(report["diagram"]["nodes"], 35)
        self.assertEqual(0, report["geometry"]["node_overlap_count"])
        self.assertIn("Memory MCP / API 网关", svg)
        self.assertIn("数据流向说明", svg)
        self.assertIn("Interactive diagram viewport", page)

    def test_enterprise_board_rejects_unknown_references_and_icons(self):
        spec = {
            "title": "Invalid board",
            "diagram_type": "system-architecture",
            "layout": "board",
            "sections": [{
                "id": "entry", "label": "Entry", "tone": "blue",
                "blocks": [{
                    "id": "grid", "kind": "grid", "title": "Grid", "columns": 1, "icon": "unknown-icon",
                    "cards": [{"id": "card", "label": "Card", "icon": "unknown-icon"}],
                }],
            }],
            "connections": [{"source": "card", "target": "missing"}],
        }
        codes = {issue.code for issue in abi_flow.validate_spec(spec)}
        self.assertIn("invalid-block-icon", codes)
        self.assertIn("invalid-card-icon", codes)
        self.assertIn("unknown-board-target", codes)

    def test_swimlanes_manual_ranks_and_brand_tokens_render(self):
        spec = {
            "title": "泳道发布流程",
            "diagram_type": "process-flow",
            "direction": "LR",
            "theme": "paper",
            "brand": {"name": "Acme", "primary": "#1D4ED8", "accent": "#0F766E"},
            "lanes": [
                {"id": "product", "label": "产品", "order": 0},
                {"id": "engineering", "label": "研发", "order": 1},
            ],
            "nodes": [
                {"id": "brief", "label": "需求", "type": "input", "lane": "product", "rank": 0},
                {"id": "review", "label": "评审", "type": "decision", "lane": "product", "rank": 1},
                {"id": "build", "label": "开发", "lane": "engineering", "rank": 2},
                {"id": "ship", "label": "发布", "lane": "engineering", "rank": 3},
            ],
            "edges": [
                {"source": "brief", "target": "review", "kind": "primary"},
                {"source": "review", "target": "build", "kind": "control"},
                {"source": "build", "target": "ship", "kind": "success"},
            ],
        }
        svg, _, report, issues = abi_flow.build(spec, abi_flow.validate_spec(spec))
        self.assertEqual([], issues)
        self.assertEqual(2, report["diagram"]["lanes"])
        self.assertEqual("Acme", report["diagram"]["brand"])
        self.assertIn('class="lane"', svg)
        self.assertIn("--edge-primary:#1D4ED8", svg)

    def test_lane_assignment_and_brand_colors_are_validated(self):
        spec = {
            "title": "Invalid lane",
            "brand": {"primary": "blue"},
            "lanes": [{"id": "ops", "label": "Ops"}],
            "nodes": [{"id": "a", "label": "A"}],
            "edges": [],
        }
        codes = {issue.code for issue in abi_flow.validate_spec(spec)}
        self.assertIn("invalid-brand-color", codes)
        self.assertIn("missing-lane", codes)
        self.assertIn("empty-lane", codes)

    def test_multi_view_workspace_validates(self):
        workspace = json.loads((ROOT / "examples" / "enterprise-ai-workspace.json").read_text(encoding="utf-8"))
        self.assertEqual([], abi_flow.validate_workspace(workspace))

    def test_every_diagram_type_has_a_strict_template(self):
        template_dir = ROOT / "skills" / "abi-flow" / "templates"
        self.assertEqual(set(abi_flow.DIAGRAM_TYPES), {path.stem for path in template_dir.glob("*.json")})
        for diagram_type in abi_flow.DIAGRAM_TYPES:
            spec = json.loads((template_dir / f"{diagram_type}.json").read_text(encoding="utf-8"))
            _, _, report, issues = abi_flow.build(spec, abi_flow.validate_spec(spec))
            self.assertEqual([], issues, diagram_type)
            self.assertEqual("passed", report["status"], diagram_type)
            self.assertEqual(diagram_type, report["diagram"]["type"])

    def test_rejects_unknown_diagram_type(self):
        spec = {
            "title": "Unknown",
            "diagram_type": "mind-map",
            "nodes": [{"id": "a", "label": "A"}],
            "edges": [],
        }
        self.assertIn("invalid-diagram-type", {issue.code for issue in abi_flow.validate_spec(spec)})

    def test_cli_new_creates_a_valid_template_without_overwriting(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "architecture.json"
            self.assertEqual(0, abi_flow.main(["new", "system-architecture", "--output", str(output)]))
            spec = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual("system-architecture", spec["diagram_type"])
            self.assertEqual(1, abi_flow.main(["new", "system-architecture", "--output", str(output)]))

    def test_escapes_svg_text(self):
        spec = {
            "title": "A < B",
            "nodes": [{"id": "a", "label": "<script>alert(1)</script>"}],
            "edges": [],
        }
        svg, _, _, issues = abi_flow.build(spec, abi_flow.validate_spec(spec))
        self.assertFalse([issue for issue in issues if issue.level == "error"])
        self.assertNotIn("<script>", svg)
        self.assertIn("&lt;script&gt;", svg)
        abi_flow.ET.fromstring(svg)

    def test_cli_renders_all_primary_artifacts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            code = abi_flow.main([
                "render", str(ROOT / "examples" / "aurora-resilience-network.json"),
                "--output-dir", temp_dir, "--name", "sample", "--strict",
            ])
            self.assertEqual(0, code)
            for suffix in ("svg", "html", "quality.json"):
                self.assertTrue((Path(temp_dir) / f"sample.{suffix}").exists())


if __name__ == "__main__":
    unittest.main()
