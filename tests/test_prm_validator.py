import tempfile
import unittest
from pathlib import Path

from aspect_yuan.prm import validate_prm


class PrmValidatorTests(unittest.TestCase):
    def test_missing_dimension_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            prm = Path(tmp) / "bad.prm"
            prm.write_text("set Output directory = output\n", encoding="utf-8")
            issues = validate_prm(prm)
            self.assertTrue(any(i["level"] == "ERROR" and i["item"] == "Dimension" for i in issues))


if __name__ == "__main__":
    unittest.main()

