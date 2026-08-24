import json
import os
import stat
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest import mock

from aspect_yuan.cli import main
from aspect_yuan.compatibility import assess_compatibility, classify_version, inspect_prm_features, policy_matrix
from aspect_yuan.fingerprint import fingerprint_aspect


class VersionAwarenessTests(unittest.TestCase):
    def test_parse_aspect_300(self):
        result = classify_version("ASPECT version 3.0.0")
        self.assertEqual(result["version"], "3.0.0")
        self.assertEqual(result["support_tier"], "primary-supported")
        self.assertEqual(result["version_channel"], "stable")

    def test_parse_development_310_pre(self):
        result = classify_version("ASPECT 3.1.0-pre")
        self.assertEqual(result["version"], "3.1.0-pre")
        self.assertEqual(result["support_tier"], "experimental")
        self.assertEqual(result["version_channel"], "development")

    def test_parse_legacy_24(self):
        result = classify_version("ASPECT version 2.4.0")
        self.assertEqual(result["support_tier"], "legacy-supported")
        self.assertEqual(result["version_channel"], "legacy")

    def test_historical_classification(self):
        result = classify_version("ASPECT 2.3.1")
        self.assertEqual(result["support_tier"], "historical-reproduction")
        self.assertEqual(result["version_channel"], "historical")

    def test_unknown_classification(self):
        result = classify_version("not an aspect version")
        self.assertIsNone(result["version"])
        self.assertEqual(result["support_tier"], "unknown")

    def test_missing_binary_fingerprint_does_not_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile = fingerprint_aspect(aspect_bin=str(Path(tmp) / "missing-aspect"), search_roots=[])
            self.assertEqual(profile["schema_version"], "1")
            self.assertIsNone(profile["binary"])
            self.assertIsNone(profile["aspect_version"])
            self.assertEqual(profile["support_tier"], "unknown")
            self.assertTrue(profile["warnings"])

    def test_fake_binary_fingerprint_json_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            aspect = _fake_aspect(Path(tmp), "ASPECT version 3.0.0")
            profile = fingerprint_aspect(aspect_bin=str(aspect), search_roots=[])
            self.assertEqual(profile["schema_version"], "1")
            self.assertEqual(profile["binary"], str(aspect.resolve()))
            self.assertEqual(profile["aspect_version"], "3.0.0")
            self.assertIn("parameter_schema", profile)
            self.assertIn("detection_evidence", profile)

    def test_unparseable_binary_version_falls_back_to_version_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "aspect"
            build = source / "build"
            build.mkdir(parents=True)
            (source / "source").mkdir()
            (source / "VERSION").write_text("3.1.0-pre\n", encoding="utf-8")
            aspect = _fake_aspect(build, "error while loading shared libraries: libnetcdf.so.19")
            profile = fingerprint_aspect(aspect_bin=str(aspect), search_roots=[])
            self.assertEqual(profile["aspect_version"], "3.1.0-pre")
            self.assertEqual(profile["version_source"], "VERSION file")
            self.assertEqual(profile["support_tier"], "experimental")
            self.assertTrue(profile["warnings"])

    def test_banner_version_line_is_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            aspect = _fake_aspect_multiline(
                Path(tmp),
                [
                    "--                             This is ASPECT                              --",
                    "--     . version 3.1.0-pre (main, 620c9ea40)",
                    "--     . using deal.II 9.5.2",
                ],
            )
            profile = fingerprint_aspect(aspect_bin=str(aspect), search_roots=[])
            self.assertEqual(profile["aspect_version"], "3.1.0-pre")
            self.assertEqual(profile["git_commit"], "620c9ea40")
            self.assertEqual(profile["support_tier"], "experimental")

    def test_compat_matrix_policy_is_machine_readable(self):
        matrix = policy_matrix()
        self.assertTrue(any(row["support_tier"] == "primary-supported" for row in matrix))
        self.assertTrue(any(row["support_tier"] == "legacy-supported" for row in matrix))

    def test_compat_check_simple_prm(self):
        with tempfile.TemporaryDirectory() as tmp:
            aspect = _fake_aspect(Path(tmp), "ASPECT version 3.0.0")
            prm = Path(tmp) / "case.prm"
            prm.write_text("set Dimension = 2\nset Output directory = output\n", encoding="utf-8")
            profile = fingerprint_aspect(aspect_bin=str(aspect), search_roots=[])
            result = assess_compatibility(prm, profile)
            self.assertEqual(result["support_tier"], "primary-supported")
            self.assertEqual(result["prm_syntax"], "pass")
            self.assertEqual(result["prm_compatibility_risk"], "LOW")

    def test_prm_with_additional_shared_libraries_is_high_plugin_risk(self):
        with tempfile.TemporaryDirectory() as tmp:
            prm = Path(tmp) / "plugin_case.prm"
            prm.write_text(
                "set Dimension = 2\n"
                "set Output directory = output\n"
                "set Additional shared libraries = libpaper_plugin.so\n",
                encoding="utf-8",
            )
            features = inspect_prm_features(prm)
            self.assertTrue(any(feature["name"] == "external shared library" for feature in features))
            result = assess_compatibility(prm, {"aspect_version": "3.0.0", "detection_evidence": []})
            self.assertEqual(result["plugin_api_risk"], "HIGH")

    def test_cli_compat_matrix(self):
        with mock.patch("sys.stdout", new_callable=StringIO) as output:
            code = main(["compat", "matrix"])
        self.assertEqual(code, 0)
        self.assertIn("primary-supported", output.getvalue())

    def test_cli_env_fingerprint_writes_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            aspect = _fake_aspect(tmp_path, "ASPECT version 2.4.0")
            output_json = tmp_path / "aspect_profile.json"
            with mock.patch("sys.stdout", new_callable=StringIO):
                code = main(["env", "fingerprint", "--aspect-bin", str(aspect), "--output", str(output_json)])
            self.assertEqual(code, 0)
            data = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(data["aspect_version"], "2.4.0")
            self.assertEqual(data["support_tier"], "legacy-supported")


def _fake_aspect(root: Path, version_line: str) -> Path:
    aspect = root / "aspect"
    aspect.write_text(
        "#!/usr/bin/env bash\n"
        "if [ \"${1:-}\" = \"--version\" ]; then\n"
        f"  echo '{version_line}'\n"
        "elif [ \"${1:-}\" = \"--help\" ]; then\n"
        "  echo 'ASPECT parameter file .prm help'\n"
        "else\n"
        "  echo 'fake aspect'\n"
        "fi\n",
        encoding="utf-8",
    )
    aspect.chmod(aspect.stat().st_mode | stat.S_IXUSR)
    return aspect


def _fake_aspect_multiline(root: Path, version_lines: list[str]) -> Path:
    aspect = root / "aspect"
    version_script = "\n".join(f"  echo '{line}'" for line in version_lines)
    aspect.write_text(
        "#!/usr/bin/env bash\n"
        "if [ \"${1:-}\" = \"--version\" ]; then\n"
        f"{version_script}\n"
        "elif [ \"${1:-}\" = \"--help\" ]; then\n"
        "  echo 'ASPECT parameter file .prm help'\n"
        "else\n"
        "  echo 'fake aspect'\n"
        "fi\n",
        encoding="utf-8",
    )
    aspect.chmod(aspect.stat().st_mode | stat.S_IXUSR)
    return aspect


if __name__ == "__main__":
    unittest.main()
