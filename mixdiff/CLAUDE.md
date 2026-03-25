# MixDiff

## Status: Active — Phase 1 confirmed working in Ableton, UI polish + remaining tests pending

## Project Overview
Max for Live Audio Effect — "changelog for your mix." Captures full-session parameter snapshots on manual trigger, displays human-readable diffs between any two snapshots.

## Stack
- Max for Live (M4L) Audio Effect device
- JavaScript via Max `js` object (`mixdiff.js`)
- LiveAPI for Live Object Model traversal
- `dict` storage for snapshot persistence

## Key Files
- `MixDiff.amxd` — The M4L device file (binary format, NOT plain JSON)
- `mixdiff.js` — JavaScript engine (~1,025 lines)

## Critical Gotchas
- **NEVER hand-write .amxd from scratch** — these files wrap JSON in a proprietary binary header (undocumented by Cycling '74). Save a blank device from Max editor, then modify the JSON inside.
- `plugin~ 2` means "channel 2 only" (NOT "2 channels"). Always use `plugin~ 1 2` and `plugout~ 1 2` for stereo Audio Effects.
- `live.text` toggle mode fires on both press (1) and release (0). Always guard with `args[0] === 1`.
- Device UI height locked at 169px.
- `defer`/`deferlow` doesn't help for JS thread blocking — use `Task` object or `setTimeout` for chunked execution.
- Dict naming must use `---` prefix for per-instance scoping in M4L.
- VST params need Configure Mode or `Options.txt` setting.

## ADR
- `docs/decisions/004-mixdiff-architecture.md`
- Linear: FOI team, MixDiff label (blue #3B82F6), tickets FOI-23 through FOI-26

## Architecture
- Index-prefixed keys prevent duplicate name collisions
- Recursive Rack/Chain traversal for nested devices
- Chunked execution (yield between track slices) to prevent UI freeze
- Three-category diff: changed, added, removed
- Storage cap: 10 snapshots (~500KB each), warn at 5

## Requirements
- Ableton Live 12 Suite (or Standard + M4L add-on)

## Status
- Phase 1 (Snapshot + Diff): Implementation complete, pending Ableton testing
- Phase 2 (Recall): Deferred — undo history flooding risk documented
- Phase 3 (Export/UX): Deferred
