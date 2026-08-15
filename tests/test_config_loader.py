import builtins
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from aspect_yuan.config import load_config


class ConfigLoaderTests(unittest.TestCase):
    def test_model_yaml_loads_without_pyyaml(self):
        root = Path(__file__).resolve().parents[1]
        config = root / "examples" / "models" / "subduction_basic.yaml"
        with _without_pyyaml():
            data = load_config(config)
        self.assertEqual(data["model"]["type"], "subduction")
        self.assertEqual(data["subduction"]["convergence_rate_cm_per_yr"], 5.0)

    def test_template_yaml_loads_without_pyyaml(self):
        root = Path(__file__).resolve().parents[1]
        for config in sorted((root / "templates" / "models").glob("*/config.yaml")):
            with _without_pyyaml():
                data = load_config(config)
            self.assertIn(data["model"]["type"], {"mantle_convection", "subduction", "rift"})

    def test_advanced_yaml_reports_pyyaml_need(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "advanced.yaml"
            config.write_text("items:\n  - one\n", encoding="utf-8")
            with _without_pyyaml():
                with self.assertRaisesRegex(ValueError, "Install PyYAML"):
                    load_config(config)


def _without_pyyaml():
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "yaml":
            raise ImportError("simulated missing PyYAML")
        return real_import(name, *args, **kwargs)

    return mock.patch("builtins.__import__", side_effect=fake_import)


if __name__ == "__main__":
    unittest.main()
