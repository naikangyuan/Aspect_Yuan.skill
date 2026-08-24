import tempfile
import unittest
from pathlib import Path

from aspect_yuan.reproduce import init_project, inspect_code, reproduction_status, scan_code_path


class ReproductionPlaceholderTests(unittest.TestCase):
    def test_existing_detector_script_is_present(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "scripts" / "detect_aspect_reproduction_context.py").exists())

    def test_reproduction_mvp_inspects_paper_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code = root / "paper_code"
            code.mkdir()
            (code / "README.md").write_text(
                "Run with ASPECT version 2.5.0, branch paper-model, commit 0123456789abcdef0123456789abcdef01234567.\n",
                encoding="utf-8",
            )
            (code / "Dockerfile").write_text("FROM ubuntu:22.04\n", encoding="utf-8")
            (code / "CMakeLists.txt").write_text("add_library(plugin SHARED material_model.cc)\n", encoding="utf-8")
            (code / "material_model.cc").write_text("// material model plugin\n", encoding="utf-8")
            prm = code / "model.prm"
            prm.write_text(
                "set Dimension = 2\n"
                "subsection Geometry model\n"
                "  set Model name = box\n"
                "end\n",
                encoding="utf-8",
            )
            project = root / "repro"
            init_project(project)
            result = inspect_code(code, project)
            self.assertTrue((project / "reproduction.yaml").exists())
            self.assertTrue((project / "REPRODUCTION_REPORT.md").exists())
            self.assertTrue((project / "parameter_inventory.csv").exists())
            self.assertIn("Level 1", result["reproduction_level"])
            report = (project / "REPRODUCTION_REPORT.md").read_text(encoding="utf-8")
            self.assertIn("model.prm", report)
            self.assertIn("Smoke Test Plan", report)
            inventory = (project / "parameter_inventory.csv").read_text(encoding="utf-8")
            self.assertIn("Dimension", inventory)
            status = reproduction_status(project)
            self.assertTrue(status["has_prm"])
            self.assertTrue(status["has_version_evidence"])

    def test_embedded_aspect_source_prms_are_not_primary_paper_prms(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paper_prm = root / "inputfiles_outputs" / "Model_S5" / "continental_extension.prm"
            paper_prm.parent.mkdir(parents=True)
            paper_prm.write_text("set Dimension = 2\n", encoding="utf-8")
            source_prm = root / "src_Aspect" / "aspect" / "benchmarks" / "blankenbach" / "base_case1a.prm"
            source_prm.parent.mkdir(parents=True)
            source_prm.write_text("set Dimension = 2\n", encoding="utf-8")
            scan = scan_code_path(root)
            self.assertIn(paper_prm, scan.prm_files)
            self.assertNotIn(source_prm, scan.prm_files)


if __name__ == "__main__":
    unittest.main()
