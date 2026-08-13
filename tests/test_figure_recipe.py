import json
import tempfile
import unittest
from pathlib import Path

from aspect_yuan.recipe import write_recipe


class FigureRecipeTests(unittest.TestCase):
    def test_write_recipe_records_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "recipe.json"
            write_recipe({"variable": "temperature"}, path, Path(tmp))
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["variable"], "temperature")
            self.assertIn("aspect_yuan_skill_version", data)


if __name__ == "__main__":
    unittest.main()

