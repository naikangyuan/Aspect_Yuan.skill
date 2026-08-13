import tempfile
import unittest
from pathlib import Path

from aspect_yuan.beginner import run_beginner


class BeginnerWorkflowTests(unittest.TestCase):
    def test_beginner_subduction_generates_report_without_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            case = Path(tmp) / "subduction"
            result = run_beginner("subduction", case, run=False, aspect_bin=None)
            self.assertEqual(result["model"], "subduction")
            self.assertTrue((case / "case.prm").exists())
            self.assertTrue((case / "run.sh").exists())
            self.assertTrue((case / "README.md").exists())
            self.assertTrue((case / "beginner_report.md").exists())
            self.assertTrue((case / "beginner_figure.yaml").exists())
            self.assertFalse(any(i["level"] == "ERROR" for i in result["validation"]))

    def test_beginner_models_supported(self):
        for model in ["subduction", "mantle_convection", "rift"]:
            with tempfile.TemporaryDirectory() as tmp:
                result = run_beginner(model, Path(tmp) / model, run=False, aspect_bin=None)
                self.assertEqual(result["model"], model)


if __name__ == "__main__":
    unittest.main()
