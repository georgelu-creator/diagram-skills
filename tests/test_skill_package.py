import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "diagram-skills"
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


class StandaloneSkillPackageTests(unittest.TestCase):
    def test_relative_markdown_links_stay_inside_the_skill_package(self):
        for document in SKILL.rglob("*.md"):
            for target in MARKDOWN_LINK.findall(document.read_text(encoding="utf-8")):
                target = target.split("#", 1)[0]
                if not target or "://" in target or target.startswith("#"):
                    continue
                resolved = (document.parent / target).resolve()
                self.assertTrue(
                    resolved.is_relative_to(SKILL.resolve()),
                    f"{document.relative_to(SKILL)} escapes the install package: {target}",
                )
                self.assertTrue(
                    resolved.exists(),
                    f"{document.relative_to(SKILL)} has a missing link: {target}",
                )

    def test_copied_skill_can_scaffold_validate_and_render_without_repo_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            installed = Path(temp_dir) / "diagram-skills"
            shutil.copytree(SKILL, installed)
            source = Path(temp_dir) / "architecture.json"
            output = Path(temp_dir) / "output"
            commands = [
                [sys.executable, "scripts/diagram_skills.py", "types"],
                [sys.executable, "scripts/diagram_skills.py", "new", "system-architecture", "--output", str(source)],
                [sys.executable, "scripts/diagram_skills.py", "validate", str(source), "--strict"],
                [
                    sys.executable,
                    "scripts/diagram_skills.py",
                    "render",
                    str(source),
                    "--output-dir",
                    str(output),
                    "--name",
                    "architecture",
                    "--strict",
                ],
            ]
            for command in commands:
                result = subprocess.run(command, cwd=installed, text=True, capture_output=True)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)

            for suffix in ("svg", "html", "quality.json"):
                self.assertTrue((output / f"architecture.{suffix}").is_file(), suffix)


if __name__ == "__main__":
    unittest.main()
