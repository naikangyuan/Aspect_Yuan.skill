import tempfile
import unittest
from pathlib import Path

from aspect_yuan.models import create_model, list_models
from aspect_yuan.prm import validate_prm


class ModelGeneratorTests(unittest.TestCase):
    def test_create_mantle_convection_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            case = create_model({"model": {"type": "mantle_convection", "case_name": "mc"}}, Path(tmp) / "mc")
            self.assertTrue((case / "case.prm").exists())
            self.assertTrue((case / "run.sh").exists())
            self.assertTrue((case / "README.md").exists())
            self.assertIn("Output directory = output", (case / "case.prm").read_text(encoding="utf-8"))
            self.assertFalse(any(i["level"] == "ERROR" for i in validate_prm(case / "case.prm")))

    def test_list_contains_p0_models(self):
        names = {item["type"] for item in list_models()}
        self.assertGreaterEqual(names, {"mantle_convection", "subduction", "rift"})


if __name__ == "__main__":
    unittest.main()

