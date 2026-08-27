import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "gallery" / "manifest.json"
RENDERER = ROOT / "skills" / "diagram-skills" / "scripts" / "diagram_skills.py"
CHECKED_IN_RENDERS = {
    "agent-workflow": "skills/diagram-skills/templates/agent-workflow.json",
    "aurora-resilience-network": "examples/aurora-resilience-network.json",
    "capability-map": "skills/diagram-skills/templates/capability-map.json",
    "data-flow": "skills/diagram-skills/templates/data-flow.json",
    "enterprise-agent-office": "examples/enterprise-agent-office.json",
    "multi-agent-delivery-control-plane": "examples/multi-agent-delivery-control-plane.json",
    "realtime-ai-data-platform": "examples/realtime-ai-data-platform.json",
    "swimlane-release": "examples/swimlane-release.json",
    "system-architecture": "skills/diagram-skills/templates/system-architecture.json",
    "system-topology": "skills/diagram-skills/templates/system-topology.json",
    "user-flow": "skills/diagram-skills/templates/user-flow.json",
}


class GalleryManifestTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.items = self.manifest["items"]

    def test_launch_gallery_has_seven_unique_complete_items(self):
        self.assertEqual(self.manifest["schema_version"], "1.0")
        self.assertEqual(len(self.items), 7)

        required = {
            "slug",
            "title",
            "title_zh",
            "alt",
            "diagram_type",
            "theme",
            "status",
            "audience",
            "goal",
            "copy_prompt",
            "source",
            "brief",
            "svg",
            "html",
            "png",
            "quality",
        }
        for item in self.items:
            self.assertFalse(required - item.keys(), item["slug"])
            for key in required:
                self.assertTrue(str(item[key]).strip(), f"{item['slug']}:{key}")

        for key in ("slug", "title", "title_zh", "alt"):
            values = [item[key] for item in self.items]
            self.assertEqual(len(values), len(set(values)), key)

    def test_manifest_artifacts_exist_and_match_the_source(self):
        artifact_keys = ("source", "svg", "html", "png", "quality")
        for item in self.items:
            for key in artifact_keys:
                self.assertTrue((ROOT / item[key]).is_file(), f"{item['slug']}:{key}")
            self.assertTrue((ROOT / item["brief"]).is_file(), f"{item['slug']}:brief")

            source = json.loads((ROOT / item["source"]).read_text(encoding="utf-8"))
            self.assertEqual(source["diagram_type"], item["diagram_type"], item["slug"])
            self.assertEqual(source["theme"], item["theme"], item["slug"])

    def test_launch_receipts_bind_current_source_brief_and_artifacts(self):
        for item in self.items:
            quality = json.loads((ROOT / item["quality"]).read_text(encoding="utf-8"))
            self.assertEqual(3, quality["schema_version"], item["slug"])
            self.assertEqual("passed", quality["structural_status"], item["slug"])
            self.assertEqual("passed", quality["status"], item["slug"])
            self.assertEqual("passed", quality["visual_review"]["status"], item["slug"])
            self.assertEqual(item["diagram_type"], quality["diagram"]["type"], item["slug"])

            expected = {
                "source": item["source"],
                "brief": item["brief"],
                "svg": item["svg"],
                "html": item["html"],
                "png": item["png"],
            }
            for kind, relative_path in expected.items():
                digest = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
                self.assertEqual(digest, quality["artifacts"][kind]["sha256"], f"{item['slug']}:{kind}")
                if kind in {"svg", "html", "png"}:
                    self.assertEqual(Path(relative_path).name, quality["artifacts"][kind]["path"], f"{item['slug']}:{kind}:path")

            reviewed_kind = quality["visual_review"]["artifact"]
            self.assertIn(reviewed_kind, {"svg", "png"}, item["slug"])
            self.assertEqual(
                quality["artifacts"][reviewed_kind]["sha256"],
                quality["visual_review"]["artifact_sha256"],
                item["slug"],
            )
            self.assertEqual(
                quality["artifacts"]["source"]["sha256"],
                quality["visual_review"]["source_sha256"],
                item["slug"],
            )
            self.assertEqual(
                quality["artifacts"]["brief"]["sha256"],
                quality["visual_review"]["brief_sha256"],
                item["slug"],
            )

    def test_all_checked_in_svg_html_match_the_current_renderer(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            for name, source in CHECKED_IN_RENDERS.items():
                result = subprocess.run(
                    [sys.executable, str(RENDERER), "render", str(ROOT / source), "--output-dir", str(output_dir), "--name", name, "--strict"],
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(0, result.returncode, f"{name}: {result.stdout}{result.stderr}")
                for suffix in ("svg", "html"):
                    self.assertEqual(
                        (ROOT / "examples" / "generated" / f"{name}.{suffix}").read_bytes(),
                        (output_dir / f"{name}.{suffix}").read_bytes(),
                        f"{name}.{suffix} drifted from the current renderer",
                    )


if __name__ == "__main__":
    unittest.main()
