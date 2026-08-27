import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "gallery" / "manifest.json"


class GalleryManifestTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.items = self.manifest["items"]

    def test_launch_gallery_has_six_unique_complete_items(self):
        self.assertEqual(self.manifest["schema_version"], "1.0")
        self.assertEqual(len(self.items), 6)

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
            if brief := item.get("brief"):
                self.assertTrue((ROOT / brief).is_file(), f"{item['slug']}:brief")

            source = json.loads((ROOT / item["source"]).read_text(encoding="utf-8"))
            self.assertEqual(source["diagram_type"], item["diagram_type"], item["slug"])
            self.assertEqual(source["theme"], item["theme"], item["slug"])


if __name__ == "__main__":
    unittest.main()
