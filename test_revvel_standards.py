import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class TestRevvelStandardsArtifacts(unittest.TestCase):
    def test_required_revvel_docs_exist(self):
        required = [
            "README.md",
            "CHANGELOG.md",
            "DEPLOYMENT_GUIDE.md",
            "GO_TO_MARKET.md",
            "BRAND_GUIDELINES.md",
            "SECURITY.md",
        ]
        for name in required:
            with self.subTest(name=name):
                self.assertTrue((ROOT / name).exists())

    def test_website_surface_exists(self):
        index = ROOT / "website" / "index.html"
        self.assertTrue(index.exists())
        text = index.read_text(encoding="utf-8").lower()
        self.assertIn("s2m website in test", text)
        self.assertIn("assets", text)
        self.assertIn("artifacts", text)
        self.assertIn("research", text)

    def test_package_baseline_scripts_defined(self):
        package = ROOT / "package.json"
        self.assertTrue(package.exists())
        parsed = json.loads(package.read_text(encoding="utf-8"))
        scripts = parsed.get("scripts", {})
        self.assertIn("test", scripts)
        self.assertIn("build", scripts)

    def test_baseline_script_files_exist(self):
        self.assertTrue((ROOT / "scripts" / "test-baseline.sh").exists())
        self.assertTrue((ROOT / "scripts" / "build-baseline.sh").exists())


if __name__ == "__main__":
    unittest.main()
