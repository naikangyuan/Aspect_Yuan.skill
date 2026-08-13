import unittest

from aspect_yuan.colormaps import get_preset


class ColormapTests(unittest.TestCase):
    def test_viscosity_uses_log_scale(self):
        preset = get_preset("geodynamics_viscosity")
        self.assertEqual(preset.scale, "log10")
        self.assertEqual(preset.kind, "sequential")

    def test_unknown_falls_back_to_temperature(self):
        self.assertEqual(get_preset("unknown").name, "temperature")


if __name__ == "__main__":
    unittest.main()

