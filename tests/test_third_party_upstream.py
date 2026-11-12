"""Every crate patched from third_party/ is tracked, and attributed.

`[patch.crates-io]` pins the workspace to a vendored fork: a fix upstream stops reaching us, and a fork
nobody watches outlives the bug it was cut for. winit was patched in Cargo.toml with no notice of it at
all, so this checks both files that have to name a vendored crate.
"""
import re
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def patched_crates():
    """The crates `[patch.crates-io]` replaces, and the folder each comes from."""
    with (ROOT / "Cargo.toml").open("rb") as toml:
        patches = tomllib.load(toml).get("patch", {}).get("crates-io", {})
    return {name: Path(value["path"]) for name, value in sorted(patches.items())}


def sections(path):
    """The `## name` sections of a markdown file, by the words after `## `."""
    text = (ROOT / path).read_text()
    parts = re.split(r"^## ", text, flags=re.MULTILINE)[1:]
    return {part.splitlines()[0].strip(): part for part in parts}


class ThirdPartyUpstreamTests(unittest.TestCase):
    def setUp(self):
        self.crates = patched_crates()
        self.upstream = sections("third_party/UPSTREAM.md")
        self.notices = sections("THIRD_PARTY_NOTICES.md")

    def test_the_patches_are_the_ones_this_test_knows(self):
        self.assertEqual(
            sorted(self.crates), ["libmimalloc-sys", "naga", "wgpu-hal", "winit"],
            "Cargo.toml's [patch.crates-io] changed; UPSTREAM.md and this test need the new crate",
        )

    def test_every_patched_crate_is_tracked_with_its_pinned_version(self):
        for crate, path in self.crates.items():
            with self.subTest(crate=crate):
                self.assertTrue((ROOT / path).is_dir(), f"{path} does not exist")
                self.assertIn(crate, self.upstream, f"third_party/UPSTREAM.md has no ## {crate}")
                with (ROOT / path / "Cargo.toml").open("rb") as toml:
                    version = tomllib.load(toml)["package"]["version"]
                self.assertIn(version, self.upstream[crate], f"## {crate} does not name {version}")

    def test_every_patched_crate_has_a_third_party_notice(self):
        for crate in self.crates:
            with self.subTest(crate=crate):
                self.assertTrue(
                    any(title == crate or title.startswith(crate + " ") for title in self.notices),
                    f"THIRD_PARTY_NOTICES.md has no ## {crate}",
                )

    def test_a_patch_says_what_would_let_us_drop_it(self):
        for crate in self.crates:
            with self.subTest(crate=crate):
                self.assertIn("Drop when:", self.upstream[crate])
                self.assertIn("Rebase check:", self.upstream[crate])


if __name__ == "__main__":
    unittest.main()
