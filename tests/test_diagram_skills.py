import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "diagram-skills" / "scripts" / "diagram_skills.py"
SPEC = importlib.util.spec_from_file_location("diagram_skills", MODULE_PATH)
diagram_skills = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
sys.modules[SPEC.name] = diagram_skills
SPEC.loader.exec_module(diagram_skills)


class DiagramSkillsTests(unittest.TestCase):
    def sample(self):
        return json.loads((ROOT / "examples" / "aurora-resilience-network.json").read_text(encoding="utf-8"))

    def test_example_passes_strict_validation(self):
        spec = self.sample()
        svg, page, report, issues = diagram_skills.build(spec, diagram_skills.validate_spec(spec))
        self.assertTrue(svg.startswith("<svg"))
        self.assertIn("Interactive diagram viewport", page)
        self.assertEqual([], issues)
        self.assertEqual("pending-review", report["status"])
        self.assertEqual("passed", report["structural_status"])
        self.assertEqual("pending", report["visual_review"]["status"])
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
        self.assertIn("unmarked-cycle", {issue.code for issue in diagram_skills.validate_spec(spec)})

    def test_feedback_cycle_passes(self):
        spec = {
            "title": "Cycle",
            "nodes": [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}],
            "edges": [
                {"source": "a", "target": "b", "kind": "primary"},
                {"source": "b", "target": "a", "kind": "feedback"},
            ],
        }
        self.assertEqual([], diagram_skills.validate_spec(spec))

    def test_rejects_executable_links(self):
        spec = {
            "title": "Unsafe",
            "nodes": [{"id": "a", "label": "A", "link": "javascript:alert(1)"}],
            "edges": [],
        }
        self.assertIn("unsafe-link", {issue.code for issue in diagram_skills.validate_spec(spec)})

    def test_rejects_malformed_http_links(self):
        self.assertFalse(diagram_skills.safe_link("https:example.com/no-host"))
        self.assertTrue(diagram_skills.safe_link("https://example.com/path"))
        self.assertTrue(diagram_skills.safe_link("#details"))

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
        boxes, _, _ = diagram_skills.layout_graph(spec)
        codes = {issue.code for issue in diagram_skills.group_geometry_issues(spec, boxes)}
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
        svg, page, report, issues = diagram_skills.build(spec, diagram_skills.validate_spec(spec))
        self.assertEqual([], issues)
        self.assertIn('data-theme="dark"', svg)
        self.assertIn("Content-Security-Policy", page)
        self.assertEqual("TB", report["diagram"]["direction"])

    def test_spectrum_theme_uses_semantic_color_tokens(self):
        spec = self.sample()
        self.assertEqual("spectrum", spec["theme"])
        svg, _, _, issues = diagram_skills.build(spec, diagram_skills.validate_spec(spec))
        self.assertEqual([], issues)
        self.assertIn("--node-agent:#f5f3ff", svg)
        self.assertIn("--node-database:#ecfeff", svg)
        self.assertIn('class="group tone-5"', svg)

    def test_schema_is_valid_json(self):
        schema = json.loads((ROOT / "skills" / "diagram-skills" / "references" / "spec.schema.json").read_text(encoding="utf-8"))
        self.assertEqual("object", schema["type"])

    def test_enterprise_board_renders_high_density_infographic(self):
        spec = json.loads((ROOT / "examples" / "enterprise-agent-office.json").read_text(encoding="utf-8"))
        svg, page, report, issues = diagram_skills.build(spec, diagram_skills.validate_spec(spec))
        self.assertEqual([], issues)
        self.assertEqual("board", report["diagram"]["layout"])
        self.assertEqual(5, report["diagram"]["groups"])
        self.assertGreaterEqual(report["diagram"]["nodes"], 35)
        self.assertEqual(0, report["geometry"]["node_overlap_count"])
        self.assertIn("客户端 Bootstrap 与能力路由", svg)
        self.assertIn("正式 Git main 主源", svg)
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
        codes = {issue.code for issue in diagram_skills.validate_spec(spec)}
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
        svg, _, report, issues = diagram_skills.build(spec, diagram_skills.validate_spec(spec))
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
        codes = {issue.code for issue in diagram_skills.validate_spec(spec)}
        self.assertIn("invalid-brand-color", codes)
        self.assertIn("missing-lane", codes)
        self.assertIn("empty-lane", codes)

    def test_multi_view_workspace_validates(self):
        workspace = json.loads((ROOT / "examples" / "enterprise-ai-workspace.json").read_text(encoding="utf-8"))
        self.assertEqual([], diagram_skills.validate_workspace(workspace))

    def test_every_diagram_type_has_a_strict_template(self):
        template_dir = ROOT / "skills" / "diagram-skills" / "templates"
        self.assertEqual(set(diagram_skills.DIAGRAM_TYPES), {path.stem for path in template_dir.glob("*.json")})
        for diagram_type in diagram_skills.DIAGRAM_TYPES:
            spec = json.loads((template_dir / f"{diagram_type}.json").read_text(encoding="utf-8"))
            _, _, report, issues = diagram_skills.build(spec, diagram_skills.validate_spec(spec))
            self.assertEqual([], issues, diagram_type)
            self.assertEqual("pending-review", report["status"], diagram_type)
            self.assertEqual("passed", report["structural_status"], diagram_type)
            self.assertEqual(diagram_type, report["diagram"]["type"])

    def test_rejects_unknown_diagram_type(self):
        spec = {
            "title": "Unknown",
            "diagram_type": "mind-map",
            "nodes": [{"id": "a", "label": "A"}],
            "edges": [],
        }
        self.assertIn("invalid-diagram-type", {issue.code for issue in diagram_skills.validate_spec(spec)})

    def test_cli_new_creates_a_valid_template_without_overwriting(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "architecture.json"
            self.assertEqual(0, diagram_skills.main(["new", "system-architecture", "--output", str(output)]))
            spec = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual("system-architecture", spec["diagram_type"])
            self.assertEqual(1, diagram_skills.main(["new", "system-architecture", "--output", str(output)]))

    def test_escapes_svg_text(self):
        spec = {
            "title": "A < B",
            "nodes": [
                {"id": "a", "label": "<script>alert(1)</script>"},
                {"id": "b", "label": "Safe"},
            ],
            "edges": [{"source": "a", "target": "b"}],
        }
        svg, _, _, issues = diagram_skills.build(spec, diagram_skills.validate_spec(spec))
        self.assertFalse([issue for issue in issues if issue.level == "error"])
        self.assertNotIn("<script>", svg)
        self.assertIn("&lt;script&gt;", svg)
        diagram_skills.ET.fromstring(svg)

    def test_cli_renders_all_primary_artifacts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            code = diagram_skills.main([
                "render", str(ROOT / "examples" / "aurora-resilience-network.json"),
                "--output-dir", temp_dir, "--name", "sample", "--strict",
            ])
            self.assertEqual(0, code)
            for suffix in ("svg", "html", "quality.json"):
                self.assertTrue((Path(temp_dir) / f"sample.{suffix}").exists())
            quality = json.loads((Path(temp_dir) / "sample.quality.json").read_text(encoding="utf-8"))
            self.assertEqual("pending-review", quality["status"])
            self.assertEqual("file-bytes", quality["artifacts"]["source"]["basis"])
            self.assertEqual(64, len(quality["artifacts"]["svg"]["sha256"]))

    def test_published_schema_rejects_types_and_additional_properties_without_crashing(self):
        invalid_specs = [
            {"title": "Bad", "direction": [], "nodes": [{"id": "a", "label": "A"}], "edges": []},
            {"title": "Bad", "theme": [], "nodes": [{"id": "a", "label": "A"}], "edges": []},
            {"title": "Bad", "nodes": [{"id": "a", "label": "A", "type": []}], "edges": []},
        ]
        for spec in invalid_specs:
            self.assertIn("schema-type", {issue.code for issue in diagram_skills.validate_spec(spec)})
        unknown = {"title": "Bad", "nodes": [{"id": "a", "label": "A", "invented": True}], "edges": []}
        self.assertIn("schema-additional-property", {issue.code for issue in diagram_skills.validate_spec(unknown)})

    def test_named_diagram_contracts_are_enforced(self):
        decision = {
            "title": "Not a tree", "diagram_type": "decision-tree", "direction": "LR",
            "nodes": [{"id": "a", "label": "A", "type": "process"}], "edges": [],
        }
        decision_codes = {issue.code for issue in diagram_skills.validate_spec(decision)}
        self.assertIn("contract-direction", decision_codes)
        self.assertIn("contract-node-types", decision_codes)
        roadmap = {
            "title": "One phase", "diagram_type": "roadmap", "direction": "LR",
            "groups": [{"id": "now", "label": "Now"}],
            "nodes": [{"id": "a", "label": "A", "group": "now"}], "edges": [],
        }
        self.assertIn("contract-groups", {issue.code for issue in diagram_skills.validate_spec(roadmap)})
        capability = json.loads((ROOT / "skills" / "diagram-skills" / "templates" / "capability-map.json").read_text(encoding="utf-8"))
        capability["edges"].append({"source": "speed", "target": "vision", "kind": "feedback"})
        self.assertIn("contract-capability-sequence", {issue.code for issue in diagram_skills.validate_spec(capability)})
        for diagram_type, direction in (("system-architecture", "TB"), ("process-flow", "LR")):
            trivial = {
                "title": "Not a grammar", "diagram_type": diagram_type, "direction": direction,
                "nodes": [{"id": "a", "label": "A", "type": "process"}], "edges": [],
            }
            codes = {issue.code for issue in diagram_skills.validate_spec(trivial)}
            self.assertIn("contract-node-count", codes, diagram_type)
            self.assertIn("contract-edge-count", codes, diagram_type)
        default_process = {"title": "Default is enforced", "nodes": [{"id": "a", "label": "A"}], "edges": []}
        default_codes = {issue.code for issue in diagram_skills.validate_spec(default_process)}
        self.assertIn("contract-node-count", default_codes)
        self.assertIn("contract-edge-count", default_codes)

    def test_dense_board_adapts_columns_checks_text_and_renders_semantic_legend(self):
        sections = []
        for section_index in range(2):
            blocks = []
            for block_index in range(4):
                prefix = f"s{section_index}b{block_index}"
                blocks.append({
                    "id": prefix, "kind": "grid", "title": f"Capability block {block_index}", "columns": 7,
                    "cards": [
                        {"id": f"{prefix}c{card_index}", "label": "Enterprise capability", "subtitle": "Semantic / Vector", "icon": "layers"}
                        for card_index in range(7)
                    ],
                })
            sections.append({"id": f"s{section_index}", "label": f"Layer {section_index}", "tone": "blue", "blocks": blocks})
        spec = {
            "title": "Dense", "diagram_type": "system-architecture", "layout": "board", "sections": sections,
            "connections": [
                {"source": "s0b0", "target": "s1b0", "kind": "primary"},
                {"source": "s0b1", "target": "s1b1", "kind": "async"},
            ],
        }
        self.assertEqual([], diagram_skills.validate_spec(spec))
        boxes, canvas, routes = diagram_skills.layout_board(spec)
        self.assertTrue(all(block["columns"] < 7 for section in canvas["sections"] for block in section["blocks"]))
        self.assertGreater(min(box.w for box in boxes.values()), 140)
        self.assertEqual([], diagram_skills.board_text_issues(canvas))
        svg = diagram_skills.render_board_svg(spec, canvas, routes)
        self.assertIn('stroke-dasharray="2 5"', svg)
        self.assertIn("Async / event", svg)

    def test_board_checks_every_single_line_text_region(self):
        spec = json.loads((ROOT / "examples" / "enterprise-agent-office.json").read_text(encoding="utf-8"))
        cases = [
            ("subtitle", None),
            ("section-subtitle", ("sections", 0, "subtitle")),
            ("banner-subtitle", ("sections", 1, "blocks", 0, "subtitle")),
            ("footer", ("sections", 2, "blocks", 0, "footer")),
        ]
        for name, path in cases:
            candidate = json.loads(json.dumps(spec))
            if path is None:
                candidate["subtitle"] = "过长" * 400
            else:
                target = candidate
                for part in path[:-1]:
                    target = target[part]
                target[path[-1]] = "过长" * 400
            _, _, _, issues = diagram_skills.build(candidate, diagram_skills.validate_spec(candidate))
            self.assertIn("board-text-overflow", {issue.code for issue in issues}, name)

    def test_graph_edge_kinds_have_non_color_styles_in_paths_and_legend(self):
        spec = json.loads((ROOT / "skills" / "diagram-skills" / "templates" / "agent-workflow.json").read_text(encoding="utf-8"))
        svg, _, _, issues = diagram_skills.build(spec, diagram_skills.validate_spec(spec))
        self.assertEqual([], issues)
        for kind in {edge.get("kind", "primary") for edge in spec["edges"]}:
            style = diagram_skills.EDGE_STYLES[kind]
            self.assertIn(f'class="edge {kind}"', svg)
            self.assertIn(f'stroke-width="{style["width"]:g}"', svg)
            if style["dash"]:
                self.assertIn(f'stroke-dasharray="{style["dash"]}"', svg)

    def test_board_themes_and_brand_tokens_change_rendered_output(self):
        spec = json.loads((ROOT / "skills" / "diagram-skills" / "templates" / "system-architecture.json").read_text(encoding="utf-8"))
        paper_boxes, paper_canvas, paper_routes = diagram_skills.layout_board(spec)
        paper = diagram_skills.render_board_svg(spec, paper_canvas, paper_routes)
        blueprint_spec = json.loads(json.dumps(spec))
        blueprint_spec["theme"] = "blueprint"
        _, blueprint_canvas, blueprint_routes = diagram_skills.layout_board(blueprint_spec)
        blueprint = diagram_skills.render_board_svg(blueprint_spec, blueprint_canvas, blueprint_routes)
        self.assertNotEqual(paper, blueprint)
        self.assertIn('data-theme="dark"', blueprint)

        branded = json.loads(json.dumps(spec))
        branded["brand"] = {
            "primary": "#112233", "accent": "#223344", "page": "#334455",
            "surface": "#445566", "ink": "#556677", "muted": "#667788",
            "hair": "#778899", "group": "#8899AA", "group_stroke": "#99AABB",
        }
        _, branded_canvas, branded_routes = diagram_skills.layout_board(branded)
        branded_svg = diagram_skills.render_board_svg(branded, branded_canvas, branded_routes)
        for expected in ("#112233", "#223344", "#334455", "#445566", "#556677", "#667788", "#778899", "#8899AA", "#99AABB"):
            self.assertIn(expected, branded_svg)
        self.assertEqual("#99AABB", diagram_skills.resolve_visual_tokens(branded)[0]["group_stroke"])

    def test_render_is_deterministic_across_python_hash_seeds(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            outputs = []
            for seed in ("1", "2", "3", "98765"):
                destination = Path(temp_dir) / seed
                env = dict(os.environ, PYTHONHASHSEED=seed)
                result = subprocess.run(
                    [sys.executable, str(MODULE_PATH), "render", str(ROOT / "examples" / "swimlane-release.json"), "--output-dir", str(destination), "--name", "same", "--strict"],
                    text=True, capture_output=True, env=env,
                )
                self.assertEqual(0, result.returncode, result.stderr or result.stdout)
                outputs.append(((destination / "same.svg").read_bytes(), (destination / "same.html").read_bytes()))
            self.assertTrue(all(output == outputs[0] for output in outputs[1:]))

    def test_png_failure_is_explicit_and_never_passes_quality(self):
        with tempfile.TemporaryDirectory() as temp_dir, mock.patch.object(diagram_skills.shutil, "which", return_value=None):
            source = ROOT / "skills" / "diagram-skills" / "templates" / "agent-workflow.json"
            code = diagram_skills.main([
                "render", str(source),
                "--output-dir", temp_dir, "--name", "no-png", "--png",
            ])
            self.assertEqual(1, code)
            quality = json.loads((Path(temp_dir) / "no-png.quality.json").read_text(encoding="utf-8"))
            self.assertEqual("failed", quality["status"])
            self.assertEqual("blocked", quality["visual_review"]["status"])
            self.assertEqual("png-export-failed", quality["issues"][-1]["code"])
            self.assertTrue((Path(temp_dir) / "no-png.svg").exists())
            self.assertEqual(1, diagram_skills.main([
                "review", str(source), "--quality", str(Path(temp_dir) / "no-png.quality.json"),
                "--brief", str(ROOT / "examples" / "briefs" / "agent-workflow.brief.json"),
                "--artifact", str(Path(temp_dir) / "no-png.svg"),
            ]))

    def test_review_finalizes_hash_bound_receipt_and_rejects_stale_artifact(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "agent-workflow.json"
            brief = Path(temp_dir) / "agent-workflow.brief.json"
            source_bytes = (ROOT / "skills" / "diagram-skills" / "templates" / "agent-workflow.json").read_bytes()
            brief_bytes = (ROOT / "examples" / "briefs" / "agent-workflow.brief.json").read_bytes()
            source.write_bytes(source_bytes)
            brief.write_bytes(brief_bytes)
            self.assertEqual(0, diagram_skills.main(["render", str(source), "--output-dir", temp_dir, "--name", "agent", "--strict"]))
            quality = Path(temp_dir) / "agent.quality.json"
            artifact = Path(temp_dir) / "agent.svg"
            html_artifact = Path(temp_dir) / "agent.html"
            blocked_receipt = json.loads(quality.read_text(encoding="utf-8"))
            blocked_receipt["visual_review"]["status"] = "blocked"
            quality.write_text(json.dumps(blocked_receipt), encoding="utf-8")
            self.assertEqual(1, diagram_skills.main(["review", str(source), "--quality", str(quality), "--brief", str(brief), "--artifact", str(artifact)]))
            blocked_receipt["visual_review"]["status"] = "pending"
            quality.write_text(json.dumps(blocked_receipt), encoding="utf-8")
            html_bytes = html_artifact.read_bytes()
            html_artifact.write_bytes(html_bytes + b"\n<!-- stale -->\n")
            self.assertEqual(1, diagram_skills.main(["review", str(source), "--quality", str(quality), "--brief", str(brief), "--artifact", str(artifact)]))
            html_artifact.write_bytes(html_bytes)

            sibling_png = Path(temp_dir) / "agent.png"
            sibling_png.write_bytes(b"\x89PNG\r\n\x1a\noriginal")
            receipt = json.loads(quality.read_text(encoding="utf-8"))
            receipt["artifacts"]["png"] = {"sha256": diagram_skills.sha256_file(sibling_png), "path": sibling_png.name}
            quality.write_text(json.dumps(receipt), encoding="utf-8")
            sibling_png.write_bytes(b"\x89PNG\r\n\x1a\nstale")
            self.assertEqual(1, diagram_skills.main(["review", str(source), "--quality", str(quality), "--brief", str(brief), "--artifact", str(artifact)]))
            sibling_png.unlink()
            receipt["artifacts"].pop("png")
            quality.write_text(json.dumps(receipt), encoding="utf-8")
            self.assertEqual(0, diagram_skills.main(["review", str(source), "--quality", str(quality), "--brief", str(brief), "--artifact", str(artifact)]))
            receipt = json.loads(quality.read_text(encoding="utf-8"))
            self.assertEqual("passed", receipt["status"])
            self.assertEqual("passed", receipt["visual_review"]["status"])
            brief.write_bytes(brief_bytes + b"\n")
            self.assertEqual(1, diagram_skills.main(["review", str(source), "--quality", str(quality), "--brief", str(brief), "--artifact", str(artifact)]))
            brief.write_bytes(brief_bytes)
            source.write_bytes(source_bytes + b"\n")
            self.assertEqual(1, diagram_skills.main(["review", str(source), "--quality", str(quality), "--brief", str(brief), "--artifact", str(artifact)]))
            source.write_bytes(source_bytes)
            artifact.write_text(artifact.read_text(encoding="utf-8") + "\n<!-- stale -->\n", encoding="utf-8")
            self.assertEqual(1, diagram_skills.main(["review", str(source), "--quality", str(quality), "--brief", str(brief), "--artifact", str(artifact)]))


if __name__ == "__main__":
    unittest.main()
