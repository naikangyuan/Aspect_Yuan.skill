import tempfile
import unittest
from pathlib import Path

from aspect_yuan.output_scan import scan_output


class OutputScannerTests(unittest.TestCase):
    def test_scan_synthetic_pvd_and_vtu(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "solution.pvd").write_text(
                '<VTKFile><Collection><DataSet timestep="0" file="solution/solution-00000.vtu"/></Collection></VTKFile>',
                encoding="utf-8",
            )
            sol = root / "solution"
            sol.mkdir()
            (sol / "solution-00000.vtu").write_text(
                '<VTKFile><DataArray Name="temperature"/><DataArray Name="viscosity"/></VTKFile>',
                encoding="utf-8",
            )
            (root / "statistics").write_text("# 1: Time (years)\n0\n", encoding="utf-8")
            result = scan_output(root)
            self.assertEqual(result["counts"]["pvd"], 1)
            self.assertEqual(result["num_timesteps"], 1)
            self.assertIn("temperature", result["variables"])
            self.assertIn("viscosity", result["common_geodynamics_variables"])

    def test_aspect_temperature_alias(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "solution-00000.vtu").write_text(
                '<VTKFile><DataArray Name="T"/><DataArray Name="p"/></VTKFile>',
                encoding="utf-8",
            )
            result = scan_output(root)
            self.assertIn("temperature", result["common_geodynamics_variables"])
            self.assertEqual(result["variable_aliases"]["T"], "temperature")


if __name__ == "__main__":
    unittest.main()
