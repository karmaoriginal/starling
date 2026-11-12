"""The APK's version comes from one place, and the release looks its APKs up by that name.

VERSION_NAME in build_apk.py and the tag a release is made from were two copies of one fact: a tag built
without bumping the constant produced starling-<old>-<abi>.apk for a release titled with the new one, and
the game reads versionName back (android.rs `app_version`) to decide whether GitHub has a newer Starling.
"""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANDROID = ROOT / "packaging/android"


def load(name, path):
    sys.path.insert(0, str(ANDROID))
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


class ApkVersionTests(unittest.TestCase):
    def setUp(self):
        self.apk = load("starling_build_apk", ANDROID / "build_apk.py")

    def test_a_release_takes_its_version_from_the_tag_with_or_without_its_v(self):
        self.assertEqual(self.apk.apply_version("v0.9.0"), "0.9.0")
        self.assertEqual(self.apk.VERSION_NAME, "0.9.0")
        self.assertEqual(self.apk.apply_version("0.9.1"), "0.9.1")
        self.assertEqual(self.apk.VERSION_NAME, "0.9.1")

    def test_the_apk_name_is_the_one_the_release_looks_for(self):
        self.assertEqual(
            self.apk.apk_name("0.9.0", "arm64-v8a"), "starling-0.9.0-arm64-v8a.apk"
        )
        self.assertEqual(
            self.apk.apk_name("0.9.0", "x86", "preview"), "starling-preview-0.9.0-x86.apk"
        )
        release = load("starling_release_assets", ANDROID / "release_assets.py")
        for abi in self.apk.TARGETS:
            with tempfile.TemporaryDirectory() as folder:
                # Only the ABI under test is there, so the ones it reports are the others'.
                (Path(folder) / self.apk.apk_name("0.9.0", abi)).write_bytes(b"apk")
                missing = {a for a in self.apk.TARGETS if a != abi}
                with self.assertRaises(ValueError) as error:
                    release.prepare(Path(folder), "v0.9.0", Path(folder))
                for name in missing:
                    self.assertIn(self.apk.apk_name("0.9.0", name), str(error.exception))

    def test_a_missing_apk_says_what_the_tree_calls_its_version(self):
        release = load("starling_release_assets", ANDROID / "release_assets.py")
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError) as error:
                release.prepare(Path(folder), "v9.9.9", Path(folder))
            self.assertIn("VERSION_NAME = " + self.apk.VERSION_NAME, str(error.exception))


if __name__ == "__main__":
    unittest.main()
