import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from aspect_yuan.env import discover_aspect, environment_check, resolve_aspect_binary


class EnvironmentDiscoveryTests(unittest.TestCase):
    def test_aspect_bin_environment_has_priority(self):
        with tempfile.TemporaryDirectory() as tmp:
            aspect = Path(tmp) / "aspect"
            aspect.write_text("#!/usr/bin/env bash\necho 'ASPECT test version'\n", encoding="utf-8")
            aspect.chmod(aspect.stat().st_mode | stat.S_IXUSR)
            with mock.patch.dict(os.environ, {"ASPECT_BIN": str(aspect)}, clear=False):
                candidates = discover_aspect(extra_roots=[], max_depth=0, include_defaults=False)
                self.assertEqual(candidates[0].path, aspect.resolve())
                self.assertEqual(resolve_aspect_binary(), str(aspect.resolve()))

    def test_search_root_finds_build_aspect(self):
        with tempfile.TemporaryDirectory() as tmp:
            aspect = Path(tmp) / "project" / "build" / "aspect"
            aspect.parent.mkdir(parents=True)
            aspect.write_text("#!/usr/bin/env bash\necho 'ASPECT test version'\n", encoding="utf-8")
            aspect.chmod(aspect.stat().st_mode | stat.S_IXUSR)
            with mock.patch.dict(os.environ, {"ASPECT_BIN": "", "ASPECT_ROOT": ""}, clear=False):
                candidates = discover_aspect(extra_roots=[Path(tmp)], max_depth=3, include_defaults=False)
                self.assertTrue(any(candidate.path == aspect.resolve() for candidate in candidates))

    def test_environment_check_reports_aspect_section(self):
        result = environment_check(extra_roots=[], include_defaults=False)
        self.assertIn("aspect", result)
        self.assertIn("tools", result)


if __name__ == "__main__":
    unittest.main()
