"""The counts AGENTS.md gives for harnesses and probes are the tree's own.

AGENTS.md is the map an agent reads first, and a count in it that has gone stale sends the reader looking
for files that are not there (it said 324 harnesses, 175 and 104 probes when the tree had 382, 183 and 116).
Each number here is a glob over the tree, so the document says how it was counted and this test keeps it true.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"

HARNESSES = re.compile(r"`tools/test_<name>_parity\.py` \((\d+) of them")
PROBES = re.compile(r"\(horizon-world (\d+), horizon-client (\d+)")


def harnesses():
    return len(list((ROOT / "tools").glob("test_*_parity.py")))


def probes(crate):
    return len(list((ROOT / "crates" / crate / "examples").rglob("*.rs")))


class AgentsDocCountsTests(unittest.TestCase):
    def setUp(self):
        self.text = AGENTS.read_text()

    def test_the_harness_count_is_the_globs(self):
        found = HARNESSES.search(self.text)
        self.assertIsNotNone(
            found,
            "AGENTS.md no longer says how many harnesses there are; if the count moved, "
            "update it there and this test's pattern",
        )
        self.assertEqual(int(found.group(1)), harnesses(), "AGENTS.md's harness count")

    def test_the_probe_counts_are_the_examples_folders(self):
        found = PROBES.search(self.text)
        self.assertIsNotNone(
            found,
            "AGENTS.md no longer says how many probes each crate has; if the counts moved, "
            "update them there and this test's pattern",
        )
        self.assertEqual(int(found.group(1)), probes("horizon-world"), "horizon-world's probe count")
        self.assertEqual(int(found.group(2)), probes("horizon-client"), "horizon-client's probe count")

    def test_the_counts_are_not_zero_so_the_globs_still_mean_something(self):
        self.assertGreater(harnesses(), 100)
        self.assertGreater(probes("horizon-world"), 100)
        self.assertGreater(probes("horizon-client"), 100)


if __name__ == "__main__":
    unittest.main()
