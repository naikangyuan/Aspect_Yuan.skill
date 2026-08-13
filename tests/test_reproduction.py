import tempfile
import unittest
from pathlib import Path


class ReproductionPlaceholderTests(unittest.TestCase):
    def test_existing_detector_script_is_present(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / "scripts" / "detect_aspect_reproduction_context.py").exists())


if __name__ == "__main__":
    unittest.main()

