# ADR 004: MixDiff — Mix Session Snapshot & Diff Tool

**Status**: Accepted (2026-03-23, post skeptic review)
**Date**: 2026-03-15
**Author**: Watson Mulkey + Claude (with senior-dev-skeptic review)

## Context

During mixing and mastering in Ableton Live, producers make many small parameter tweaks across devices — EQ adjustments, compressor thresholds, reverb sends, plugin settings — then export different versions. There's no built-in way to track or articulate what changed between exports. This leads to:

- Inability to describe what changed between mix versions
- No way to quickly revert to a previous mix state
- Lost institutional knowledge about what tweaks improved (or hurt) a mix

## Decision

Build **MixDiff**, a Max for Live Audio Effect device that captures full-session parameter snapshots on manual trigger and displays human-readable diffs between snapshots.

### Device Type

Audio Effect — placed on the Master track (like NTPD). This gives it access to the full Live Object Model without being tied to a specific track.

### Technical Architecture

**Implementation Language**: JavaScript via Max's `js` object (or `v8` for Live 12.2+)

The `LiveAPI` JavaScript object provides full access to the Live Object Model. The core traversal:

```
Song → tracks[] → devices[] → (chains[] → devices[])* → parameters[]
```

Note: Instrument Racks and Effect Racks contain `chains[] → devices[]` recursively. The traversal must be recursive to capture devices nested inside Racks.

**Why JavaScript over pure Max patching**: The snapshot/diff logic involves nested iteration, dictionary operations, and string formatting. This is dramatically simpler in JS than wiring together Max objects. The `LiveAPI` class in JS has direct access to the same LOM as `live.path`/`live.object`.

**Snapshot Data Structure** (stored as JSON in a `dict` object):

```json
{
  "snapshots": {
    "Mix v3 - vocals up": {
      "timestamp": "2026-03-15T14:30:00",
      "data": {
        "0:Vocals": {
          "0:EQ Eight": {
            "1 Frequency A": 2400.0,
            "1 Gain A": 3.5
          },
          "1:Compressor": {
            "Threshold": -18.0,
            "Ratio": 4.0
          }
        },
        "1:Drums": {
          "0:Drum Rack": {
            "_chains": {
              "0:Kick": {
                "0:Saturator": {
                  "Drive": 12.0
                }
              }
            }
          }
        }
      }
    }
  }
}
```

Key hierarchy uses **index-prefixed keys** for uniqueness: `"0:Vocals"` not `"Vocals"`. This prevents silent data loss when tracks or devices share names (e.g., two "EQ Eight" on the same track, two tracks named "Vocals"). The index comes from the LOM path position. The diff display strips the index prefix for human readability.

Rack chains are stored under a `_chains` key, preserving the recursive device hierarchy.

**Storage**: Max `dict` object with `@parameter_enable 1` and `@embed 0`. This persists snapshot data with the Live Set file (not the device file), so each project retains its own snapshot history.

The dict **must use the `---` prefix naming convention** (e.g., `---mixdiff_data`) to ensure per-instance scoping. Without this, multiple MixDiff instances (e.g., on different tracks) would share and corrupt the same dict. Reference the dict from JS via `this.patcher.getnamed("dictname")` rather than the global name.

**Storage budget**: ~500KB per snapshot for a 5,000-parameter session. Default cap of **10 snapshots** with user warning at 5. See Risks section for bloat mitigation.

**UI** (constrained to 169px height):

| Element | Purpose |
|---------|---------|
| `live.text` button | "Take Snapshot" trigger |
| `live.text` button | "Show Diff" trigger |
| `live.menu` (x2) | Select snapshots A and B for comparison |
| `jit.cellblock` | Scrollable table showing diff results |
| `comment` | Snapshot count / status text |

**Diff Output Format** (displayed in `jit.cellblock` table):

```
Change | Track      | Device     | Parameter     | Before  | After
-------|------------|------------|---------------|---------|--------
  ~    | Vocals     | EQ Eight   | 1 Frequency A | 2400 Hz | 3100 Hz
  ~    | Vocals     | Compressor | Threshold     | -18 dB  | -22 dB
  +    | Bass       | Saturator  | —             | —       | (added)
  -    | Strings    | Reverb     | —             | (removed)| —
```

The diff algorithm produces three categories:
1. **Changed (~)**: Same key in both snapshots, value differs
2. **Added (+)**: Key exists in snapshot B but not A (new track/device)
3. **Removed (-)**: Key exists in snapshot A but not B (deleted track/device)

### LOM Traversal Strategy

```javascript
// Index-prefixed key construction
function makeKey(index, name) {
    return index + ":" + name;
}

// Recursive device walker — handles Racks with nested chains
function walkDevices(api, basePath, numDevices, result) {
    for (var d = 0; d < numDevices; d++) {
        var devPath = basePath + " devices " + d;
        api.goto(devPath);
        var deviceKey = makeKey(d, api.getstring("name"));
        result[deviceKey] = {};

        // Capture parameters
        var numParams = api.getcount("parameters");
        for (var p = 0; p < numParams; p++) {
            api.goto(devPath + " parameters " + p);
            var paramName = api.getstring("name");
            result[deviceKey][paramName] = api.get("value");
        }

        // Recurse into Rack chains if present
        api.goto(devPath);
        var numChains = api.getcount("chains");
        if (numChains > 0) {
            result[deviceKey]["_chains"] = {};
            for (var c = 0; c < numChains; c++) {
                var chainPath = devPath + " chains " + c;
                api.goto(chainPath);
                var chainKey = makeKey(c, api.getstring("name"));
                result[deviceKey]["_chains"][chainKey] = {};

                var chainDevices = api.getcount("devices");
                walkDevices(api, chainPath, chainDevices,
                    result[deviceKey]["_chains"][chainKey]);
            }
        }
    }
}

function takeSnapshot(snapshotName) {
    var snapshot = {};
    var api = new LiveAPI("live_set");

    // Walk: regular tracks + return tracks + master
    var trackTypes = [
        { path: "tracks", count: api.getcount("tracks") },
        { path: "return_tracks", count: api.getcount("return_tracks") },
        { path: "master_track", count: 1, isSingle: true }
    ];

    for (var s = 0; s < trackTypes.length; s++) {
        var src = trackTypes[s];
        for (var t = 0; t < src.count; t++) {
            var trackPath = src.isSingle
                ? "live_set " + src.path
                : "live_set " + src.path + " " + t;

            api.goto(trackPath);
            var trackKey = makeKey(t, api.getstring("name"));
            snapshot[trackKey] = {};

            var numDevices = api.getcount("devices");
            walkDevices(api, trackPath, numDevices, snapshot[trackKey]);
        }
    }
    return snapshot;
}
```

Note: This reuses a single `LiveAPI` instance via `goto()` to minimize overhead (constructing new `LiveAPI` objects is expensive).

### Performance Strategy

**The problem**: All LiveAPI/JS calls execute on Max's low-priority thread. A naive loop over 5,000+ parameters blocks this thread for seconds, freezing *all* Max for Live device UIs in the session (not just MixDiff).

**`defer`/`deferlow` does NOT solve this** — those defer *to* the low-priority thread, where the code already runs.

**Solution: Chunked traversal with yield**

Process 5-10 tracks per execution slice, then yield back to the event loop before processing the next chunk:

```javascript
// v8 engine (Live 12.2+): use setTimeout to yield
function snapshotChunked(trackList, chunkSize, callback) {
    var index = 0;
    function processChunk() {
        var end = Math.min(index + chunkSize, trackList.length);
        for (var i = index; i < end; i++) {
            walkTrack(trackList[i]); // process one track
        }
        index = end;
        updateProgress(index, trackList.length);
        if (index < trackList.length) {
            setTimeout(processChunk, 0); // yield, then continue
        } else {
            callback(); // done
        }
    }
    processChunk();
}

// js engine (legacy): use Task object to schedule chunks
var snapshotTask = new Task(processNextChunk, this);
snapshotTask.interval = 50; // ms between chunks
snapshotTask.repeat();
```

**Performance estimates** (revised):
- Small session (<30 tracks, minimal Racks): **under 2 seconds**
- Medium session (50 tracks, some Racks): **2-5 seconds**
- Large session (100+ tracks, heavy Rack nesting): **5-15 seconds**

UI shows track-by-track progress during capture.

### Error Handling

A half-completed snapshot is worse than no snapshot. The traversal:

1. Wraps the full walk in try/catch
2. Builds the snapshot in a temporary variable, NOT directly in the dict
3. Only writes to the dict after successful completion
4. Logs errors to Max Console with context (track index, device path)
5. On error, shows user-facing message: "Snapshot failed — see Max Console for details"

Individual parameter read failures (e.g., device deleted mid-traversal) are caught and skipped with a warning, not a full abort.

### Third-Party Plugin Limitation

VST/AU plugin parameters are accessible through the LOM, but only parameters that have been "configured" in Live's Configure Mode (or auto-populated via `Options.txt` setting `-_PluginAutoPopulateThreshold=128`). Native Ableton devices expose all parameters by default.

This is a known limitation to document, not a blocker. Users who rely heavily on third-party plugins will need to configure parameter exposure once per plugin.

## Phases

### Phase 1 — MVP: Snapshot + Diff
- Manual "Take Snapshot" button with user-provided name
- Full session parameter capture (all tracks, all devices, all Rack chains, all accessible parameters)
- Index-prefixed keys for unique identification
- Store snapshots in `dict` (persisted with Live Set), cap at 10
- Three-category diff: changed / added / removed
- Display diff in scrollable `jit.cellblock` table
- Chunked traversal with progress indicator
- Error handling: validate before save, graceful degradation on per-parameter failures

### Phase 2 — Recall
- Click a snapshot to restore all parameter values (`live.object set value`)
- Selective recall: restore only specific tracks or devices from a snapshot
- Auto-snapshot before recall so the user can revert

**Known complexity — Undo history flooding**: Bulk `set value` calls create one undo entry per parameter. Pressing Ctrl+Z after a 5,000-parameter recall undoes ONE change, not the whole recall. Ableton documents this as a known M4L limitation. Mitigations to investigate before Phase 2 implementation:
- Research undo-bypass techniques (hidden parameter visibility, `_raw` access)
- Confirmation dialog before recall with clear warning
- The auto-snapshot provides a "revert recall" escape hatch that doesn't depend on undo

### Phase 3 — Enhanced UX
- Export diff as text/markdown file (also relieves storage pressure — archive old snapshots externally)
- Snapshot annotations/notes (user adds context)
- Visual indicators for magnitude of change (color-coded diff values)
- Auto-name snapshots with timestamp + export filename if detectable
- Delta compression: store only changed parameters after a baseline snapshot

## Alternatives Considered

| Alternative | Why Rejected |
|---|---|
| Continuous parameter observation | Observer count at scale (1000+) degrades audio performance. Manual snapshot is sufficient and predictable. |
| Python companion app | Breaks the "lives in Ableton" requirement. Adds install/IPC complexity. |
| External file storage | For MVP, data should persist with the Live Set. Export is a Phase 3 nice-to-have. |
| Pure Max patching (no JS) | Nested iteration + dict manipulation + string formatting is impractical without scripting. |
| RNBO | RNBO is for DSP/audio processing, not session introspection. No LOM access. |

## Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Duplicate track/device names cause silent data loss | Critical | Index-prefixed keys (`"0:Vocals/1:EQ Eight"`) |
| Rack/chain devices not captured | High | Recursive `walkDevices` traversal handles nested chains |
| Session structure changes between snapshots | High | Three-category diff: changed / added / removed |
| Bulk recall floods undo history (Phase 2) | High | Research undo-bypass before Phase 2; confirmation dialog; auto-snapshot escape hatch |
| Dict naming causes cross-instance contamination | Medium | Use `---` prefix for per-instance scoping |
| JS traversal blocks Max UI thread | Medium | Chunked traversal with yield between slices |
| Half-completed snapshot saved on error | Medium | Build in temp var, validate before write, try/catch |
| `dict` grows large with many snapshots (~500KB each) | Medium | Cap at 10 snapshots, warn at 5, Phase 3 adds external export |
| Large sessions take 5-15s to snapshot | Medium | Progress indicator, chunked traversal, user expectation setting |
| VST parameters not exposed | Medium | Document Configure Mode requirement, note in UI |
| `@embed 0` + `@parameter_enable 1` edge cases | Medium | Explicit testing protocol during development |
| 169px height constraint limits diff readability | Medium | `jit.cellblock` scrolling; consider floating window in Phase 3 |
| Parameter naming inconsistency across plugins | Low | Display raw names; aliasing is a future enhancement |
| Live version compatibility | Low | Target `js` (broad compat) with optional `v8` path for 12.2+ |

## Development Environment

- **Requires**: Ableton Live 12 Suite (or Standard + Max for Live add-on)
- **Editor**: Max for Live editor (built into Live), external text editor for JS files
- **Testing**: Manual testing in Live with representative sessions (small, medium, large)
- **Distribution**: `.amxd` file (standard M4L device format)

## References

- [Live Object Model (Cycling '74)](https://docs.cycling74.com/max8/vignettes/live_object_model)
- [LiveAPI JavaScript Reference](https://docs.cycling74.com/apiref/js/liveapi/)
- [Max for Live Production Guidelines](https://github.com/Ableton/maxdevtools/blob/main/m4l-production-guidelines/m4l-production-guidelines.md)
- [NTPD Note-Taking Device](https://maxforlive.com/library/device/12448/ntpd) — UX inspiration
- [Device Parameters in Max for Live](https://docs.cycling74.com/legacy/max8/vignettes/live_parameters)
- [LiveAPI Performance (Cycling '74 Forum)](https://cycling74.com/forums/poor-performance-of-liveapi-in-js-object)
- [M4L Observer Limits (Cycling '74 Forum)](https://cycling74.com/forums/m4l-observer-limits)
- [Undo Limitations with M4L Devices (Ableton)](https://help.ableton.com/hc/en-us/articles/209066909-Unable-to-undo-due-to-certain-Max-for-Live-devices)

## Skeptic Review Notes (2026-03-15)

Reviewed by senior-dev-skeptic agent. Key changes made from review:
- Added index-prefixed keys to prevent duplicate name collisions (Critical)
- Added recursive Rack/Chain traversal to LOM strategy (High)
- Replaced `defer` with chunked traversal + yield strategy (Critical)
- Changed dict naming to `---` prefix for per-instance scoping (Medium)
- Added three-category diff (changed/added/removed) (High)
- Documented undo flooding risk for Phase 2 recall (High)
- Added error handling strategy (Medium)
- Upgraded storage risk from Low to Medium with concrete cap
- Revised performance estimates to be realistic for large sessions
