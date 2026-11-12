"""A release note must not call a shipped feature missing.

`known_issues` in tools/release_train.py copies every bullet of docs/known-issues.md into every game
release's notes. A bullet that outlives its fix then tells every player that a working feature is gone,
which is what the shader packs bullet did after the packs came back.
"""
import re
import unittest

from tools import release_train as train

# A word in a bullet, and the files whose presence proves the tree still has that capability.
CAPABILITIES = {
    "shader": [
        "crates/horizon-shaders/src/lib.rs",
        "crates/horizon-optifine/src/lib.rs",
        "crates/horizon-client/src/game/native_shaders.rs",
    ],
    "mod": [
        "crates/horizon-mods/src/lib.rs",
        "crates/horizon-client/src/game/mod_catalog.rs",
    ],
    "controller": [
        "crates/horizon-client-input/src/gamepad.rs",
        "crates/horizon-dualsense/src/lib.rs",
    ],
}

REMOVED = re.compile(
    r"\b(?:has|have|was|were)\s+been\s+removed\b|\bare\s+no\s+longer\b|\bis\s+gone\b|\bno\s+longer\s+work",
    re.IGNORECASE,
)


def wrongly_called_removed(bullet, root):
    """The capability a bullet calls removed while the tree still has it, else None."""
    if not REMOVED.search(bullet):
        return None
    for capability, paths in CAPABILITIES.items():
        if capability not in bullet.lower():
            continue
        if all((root / path).is_file() for path in paths):
            return capability
    return None


class KnownIssuesTests(unittest.TestCase):
    def test_no_shipped_release_note_calls_a_working_feature_missing(self):
        stale = [
            (bullet, wrongly_called_removed(bullet, train.ROOT))
            for bullet in train.known_issues()
        ]
        self.assertEqual(
            [(bullet, name) for bullet, name in stale if name],
            [],
            "docs/known-issues.md tells players a feature is gone while the tree ships it; "
            "remove the bullet in the pull request that fixed it",
        )

    def test_the_shader_packs_bullet_that_shipped_is_caught(self):
        bullet = ("- Shader packs have been removed for now. They will come back later, written "
                  "again from scratch.")
        self.assertEqual(wrongly_called_removed(bullet, train.ROOT), "shader")

    def test_a_bullet_about_something_the_tree_lacks_stays(self):
        # Nothing in CAPABILITIES has a "cheese" capability, and the wording is not a removal.
        self.assertIsNone(wrongly_called_removed("- Cheese wheels do not stack.", train.ROOT))
        # A removal of a capability whose files are not all there is not called stale either.
        self.assertIsNone(
            wrongly_called_removed("- Mod support has been removed for now.", train.ROOT.parent / "nowhere")
        )


if __name__ == "__main__":
    unittest.main()
