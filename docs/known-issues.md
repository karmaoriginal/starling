# Known issues

Every game release lists the bullets below under "Known issues" (tools/release_train.py). Keep them short and
written for players; remove a bullet in the pull request that fixes it.

Nothing is listed right now, and a release with no bullet publishes no "Known issues" section at all
(`notes` in tools/release_train.py).

A bullet here reaches every player's release notes, so one that outlives its fix tells players a working
feature is missing. That happened with the shader packs bullet, which said packs "have been removed for now"
long after `crates/horizon-shaders`, `crates/horizon-optifine` and `crates/horizon-client/src/game/native_shaders.rs`
shipped them again: every release from then on told players shader packs were gone while the game's own
shader pack was in the APK. Before adding a bullet, check the tree really lacks what it names;
`tests/test_known_issues.py` fails when a bullet says a capability was removed while the code that provides
it is in the tree.
