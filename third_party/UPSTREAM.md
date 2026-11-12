# Upstream tracking for the vendored patches

`Cargo.toml`'s `[patch.crates-io]` replaces four crates with the copies in this folder. Each one is a
vendored release of someone else's crate with fixes we could not wait for. That buys time and costs
attention: the workspace is pinned to these versions, a security or bug fix upstream does not reach us
until we rebase, and a patch nobody is watching outlives the bug it fixes.

Every entry says what the patch is for, what upstream would let us drop it, and how to check a rebase.
`tests/test_third_party_upstream.py` fails when a crate is patched in `Cargo.toml` and has no entry here or
no notice in [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md), so a new vendored fork cannot arrive
silently.

## wgpu-hal

- **Vendored:** 30.0.1 of [gfx-rs/wgpu](https://github.com/gfx-rs/wgpu).
- **Fixes carried:** [gfx-rs/wgpu#10124](https://github.com/gfx-rs/wgpu/pull/10124) — wgpu 30 creates a
  Vulkan descriptor pool with no pool sizes, which Vulkan allows only since 1.3.215 and Intel's Windows
  driver for 6th-10th gen iGPUs (HD 520/530, UHD 620/630) crashes on with an access violation (#746); the
  same pull request fixes the Metal backend's lookup of the CoreGraphics HDR colour space names, which
  handed CoreGraphics a symbol's address as the string and crashed HDR output on macOS. And
  [gfx-rs/wgpu#10714](https://github.com/gfx-rs/wgpu/pull/10714) — on Windows Vulkan waits for the acquire
  fence only in FIFO, where it was meant to pace frames, so with VSync off every frame waited for the GPU
  to finish the one before (#4604).
- **Drop when:** a wgpu release carries both pull requests. Then remove the folder and the
  `[patch.crates-io]` line together.
- **Rebase check:** `cargo test -p horizon-client-lib --lib gfx` (the backend order, the device search and
  the shader translation tests), then a run on an Intel iGPU with Vulkan and on macOS with HDR on.

## naga

- **Vendored:** 30.0.1 of [gfx-rs/wgpu](https://github.com/gfx-rs/wgpu).
- **Fixes carried:** fixes to its GLSL frontend that Iris/OptiFine-format shader packs need, each applied
  in the commit that needed it; there are no upstream pull request numbers for them
  ([THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)). It also carries the `hlsl-out` feature the gfx
  tests use to translate every WGSL shader as wgpu's DirectX 12 backend does.
- **Drop when:** a naga release parses the shader packs that need these fixes. Because there are no
  upstream numbers to watch, the check below is what tells us.
- **Rebase check:** `cargo test -p horizon-client-lib --lib gfx`, then load a pack from each family the
  game is tested with (Complementary, MakeUp, BSL, Photon, Bliss) and read the parse errors.

## winit

- **Vendored:** 0.30.13 of [rust-windowing/winit](https://github.com/rust-windowing/winit).
- **Fixes carried:** `winit::platform::android::set_input_hook`, marked "Horizon's patch" in
  `src/platform/android.rs` and `src/platform_impl/android/mod.rs`. winit's Android backend turns the
  events it understands into touches, stick moves and mouse buttons and drops the rest (hover, the wheel,
  the buttons' own events), so the app never sees the raw events; the hook gives it each one first
  (`crates/horizon-client/src/android_lib.rs`). Nothing changes on the other platforms.
- **Drop when:** a winit release offers an equivalent hook. **Not upstreamed: there is no pull request to
  watch**, so an update to winit needs this patch re-applied by hand.
- **Rebase check:** `python3 tools/test_world_input_capture.py`,
  `python3 tools/test_mouse_button_events.py` and `python3 tools/test_mouse_scrolling_hook.py`, then a
  phone with a controller and a mouse.

## libmimalloc-sys

- **Vendored:** 0.1.49 of [purpleprotocol/mimalloc_rust](https://github.com/purpleprotocol/mimalloc_rust),
  with the [mimalloc](https://github.com/microsoft/mimalloc) v3 sources it bundles.
- **Fixes carried:** [microsoft/mimalloc#1291](https://github.com/microsoft/mimalloc/issues/1291) —
  mimalloc v3 counts bits with POPCNT when MSVC builds it, so the game died before `main` on CPUs without
  it (Core 2, #7264). `mi_popcount` in `include/mimalloc/bits.h` uses mimalloc's portable bit count there.
- **Drop when:** a libmimalloc-sys release has the fix.
- **Rebase check:** a Windows build that starts on a CPU without POPCNT, or read the generated
  `mi_popcount` for a `popcnt` instruction in the MSVC x64 output.
