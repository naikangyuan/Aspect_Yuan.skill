import tempfile
import unittest
from pathlib import Path

from aspect_yuan.plotting import plot_from_config
from aspect_yuan.plotting import _resolve_variable


class PlotConfigTests(unittest.TestCase):
    def test_metadata_only_plot_writes_recipe(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / "output"
            out.mkdir()
            cfg = root / "figure.yaml"
            cfg.write_text(
                """
input: output
field:
  variable: temperature
output:
  prefix: test_figure
  metadata_only: true
""",
                encoding="utf-8",
            )
            old = Path.cwd()
            try:
                import os

                os.chdir(root)
                result = plot_from_config(cfg)
            finally:
                os.chdir(old)
            self.assertTrue(Path(result["recipe"]).exists())
            self.assertTrue(Path(result["metadata"]).exists())

    def test_temperature_alias_resolves_to_T(self):
        self.assertEqual(_resolve_variable("temperature", ["T", "velocity"]), "T")


if __name__ == "__main__":
    unittest.main()
