import tempfile
import unittest
from pathlib import Path
from unittest import mock

from aspect_yuan.reproduce import init_profile_project, init_project, inspect_code, list_paper_profiles, reproduction_status, scan_code_path


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
            with mock.patch(
                "aspect_yuan.reproduce.fingerprint_aspect",
                return_value={"aspect_version": "3.0.0", "support_tier": "primary-supported", "detection_evidence": []},
            ):
                result = inspect_code(code, project, "auto")
            self.assertTrue((project / "reproduction.yaml").exists())
            self.assertTrue((project / "REPRODUCTION_REPORT.md").exists())
            self.assertTrue((project / "parameter_inventory.csv").exists())
            self.assertTrue((project / "SMOKE_TEST_PLAN.md").exists())
            self.assertTrue((project / "VERSION_PLAN.md").exists())
            self.assertTrue((project / "PAPER_REPRODUCTION_CHECKLIST.md").exists())
            self.assertIn("Level 1", result["reproduction_level"])
            report = (project / "REPRODUCTION_REPORT.md").read_text(encoding="utf-8")
            self.assertIn("model.prm", report)
            self.assertIn("Smoke Test Plan", report)
            self.assertIn("ASPECT Version Awareness", report)
            self.assertIn("Reproduce first using 2.5.0", report)
            inventory = (project / "parameter_inventory.csv").read_text(encoding="utf-8")
            self.assertIn("Dimension", inventory)
            status = reproduction_status(project)
            self.assertTrue(status["has_prm"])
            self.assertTrue(status["has_version_evidence"])
            self.assertEqual(status["local_aspect_version"], "3.0.0")
            self.assertTrue(status["version_mismatch"])

    def test_profile_catalog_contains_real_project_archetypes(self):
        keys = {profile["key"] for profile in list_paper_profiles()}
        self.assertGreaterEqual(keys, {"kaili-rift", "oneill-hadean-mixing", "gernon-craton-breakup"})

    def test_template_initializes_profile_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "kaili-template"
            result = init_profile_project("kaili-rift", project)
            self.assertEqual(result["profile"], "kaili-rift")
            self.assertTrue((project / "reproduction_profile.yaml").exists())
            self.assertTrue((project / "SMOKE_TEST_PLAN.md").exists())
            self.assertTrue((project / "VERSION_PLAN.md").exists())
            self.assertTrue((project / "PAPER_REPRODUCTION_CHECKLIST.md").exists())
            config = (project / "reproduction.yaml").read_text(encoding="utf-8")
            self.assertIn("kaili-rift", config)

    def test_auto_profile_detects_kaili_style_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code = root / "aspect-fast_kaili"
            prm = code / "The_impact_of_orgenic_inheritance_on_rifted_margin formation" / "inputfiles_outputs" / "Model_S5" / "continental_extension.prm"
            prm.parent.mkdir(parents=True)
            prm.write_text("set Dimension = 2\n", encoding="utf-8")
            plugin = code / "The_impact_of_orgenic_inheritance_on_rifted_margin formation" / "plugins_Aspect" / "initial_temperature" / "lithosphere_rift.cc"
            plugin.parent.mkdir(parents=True)
            plugin.write_text("// plugin\n", encoding="utf-8")
            (code / "README.md").write_text("ASPECT version 2.4.0-pre with FastScape.\n", encoding="utf-8")
            project = root / "repro"
            with mock.patch("aspect_yuan.reproduce.fingerprint_aspect", return_value={"aspect_version": "3.1.0-pre"}):
                result = inspect_code(code, project, "auto")
            self.assertEqual(result["profile"], "kaili-rift")
            report = (project / "REPRODUCTION_REPORT.md").read_text(encoding="utf-8")
            self.assertIn("kaili-rift", report)
            self.assertIn("continental_extension.prm", (project / "SMOKE_TEST_PLAN.md").read_text(encoding="utf-8"))

    def test_auto_profile_detects_oneill_style_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code = root / "ONeill"
            code.mkdir()
            (code / "mixing_100km.prm").write_text("set Dimension = 2\n", encoding="utf-8")
            (code / "README.md").write_text("Hadean lateral mixing model.\n", encoding="utf-8")
            project = root / "repro"
            with mock.patch("aspect_yuan.reproduce.fingerprint_aspect", return_value={"aspect_version": None}):
                result = inspect_code(code, project, "auto")
            self.assertEqual(result["profile"], "oneill-hadean-mixing")

    def test_auto_profile_detects_gernon_style_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code = root / "paper-Gernon-Co-evolution-of-craton-margins-and-interiors-during-continental-breakup-main"
            code.mkdir()
            (code / "model.prm").write_text("set Dimension = 2\n", encoding="utf-8")
            (code / "README.md").write_text("craton margins and continental-breakup ASPECT model.\n", encoding="utf-8")
            project = root / "repro"
            with mock.patch("aspect_yuan.reproduce.fingerprint_aspect", return_value={"aspect_version": None}):
                result = inspect_code(code, project, "auto")
            self.assertEqual(result["profile"], "gernon-craton-breakup")

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
