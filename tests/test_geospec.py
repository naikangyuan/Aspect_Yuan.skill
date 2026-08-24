import builtins
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest import mock

from aspect_yuan.cli import main
from aspect_yuan.config import load_config
from aspect_yuan.geospec import create_case_from_geospec, default_geospec, explain_geospec, geospec_to_model_config, init_geospec, validate_geospec
from aspect_yuan.prm import validate_prm


class GeoSpecTests(unittest.TestCase):
    def test_default_subduction_geospec_validates(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "geology.yaml"
            init_geospec("subduction", path)
            issues = validate_geospec(path)
            self.assertFalse(any(issue["level"] == "ERROR" for issue in issues))
            explanation = explain_geospec(path)
            self.assertIn("Subduction intent", explanation)

    def test_example_geospec_loads_without_pyyaml(self):
        root = Path(__file__).resolve().parents[1]
        path = root / "examples" / "geospec" / "subduction_geology.yaml"
        with _without_pyyaml():
            data = load_config(path)
        self.assertEqual(data["model_family"], "subduction")
        self.assertEqual(data["subduction"]["convergence_rate_cm_per_yr"], 5.0)

    def test_geospec_to_model_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "geology.yaml"
            init_geospec("mantle_convection", path)
            config = geospec_to_model_config(path)
            self.assertEqual(config["model"]["type"], "mantle_convection")
            self.assertIn("geospec", config)

    def test_create_case_from_geospec_uses_existing_model_generator(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "geology.yaml"
            case_dir = Path(tmp) / "case"
            init_geospec("subduction", path)
            created = create_case_from_geospec(path, case_dir)
            self.assertTrue((created / "case.prm").exists())
            self.assertTrue((created / "GEOSPEC_EXPLANATION.md").exists())
            self.assertFalse(any(issue["level"] == "ERROR" for issue in validate_prm(created / "case.prm")))

    def test_invalid_geospec_reports_missing_geological_question(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "geology.yaml"
            data = default_geospec("rift")
            data["scientific_question"] = ""
            path.write_text("{}\n", encoding="utf-8")
            from aspect_yuan.config import dump_config

            dump_config(data, path)
            issues = validate_geospec(path)
            self.assertTrue(any(issue["item"] == "scientific_question" for issue in issues))

    def test_cli_geospec_init_validate_create(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "geology.yaml"
            case_dir = Path(tmp) / "case"
            with mock.patch("sys.stdout", new_callable=StringIO):
                self.assertEqual(main(["geospec", "init", "subduction", "--output", str(path)]), 0)
            with mock.patch("sys.stdout", new_callable=StringIO) as output:
                self.assertEqual(main(["geospec", "validate", str(path)]), 0)
            self.assertIn("PASS", output.getvalue())
            with mock.patch("sys.stdout", new_callable=StringIO):
                self.assertEqual(main(["geospec", "create-case", str(path), "--output-dir", str(case_dir)]), 0)
            self.assertTrue((case_dir / "case.prm").exists())


def _without_pyyaml():
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "yaml":
            raise ImportError("simulated missing PyYAML")
        return real_import(name, *args, **kwargs)

    return mock.patch("builtins.__import__", side_effect=fake_import)


if __name__ == "__main__":
    unittest.main()
