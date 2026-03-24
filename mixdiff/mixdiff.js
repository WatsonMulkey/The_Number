/*
 * MixDiff — Mix Session Snapshot & Diff Tool
 * Max for Live Audio Effect — JavaScript Engine
 *
 * Ref: ADR 004 — docs/decisions/004-mixdiff-architecture.md
 * Linear: FOI-23 (scaffold), FOI-24 (traversal), FOI-25 (diff)
 *
 * ============================================================
 * PATCHER SETUP — Create these objects in the Max editor:
 * ============================================================
 *
 * AUDIO (required for Audio Effect):
 *   [plugin~] → [plugout~]   (direct connection, audio passthrough)
 *
 * INIT:
 *   [live.thisdevice] → outlet 0 → [js mixdiff.js]  inlet 0
 *     (sends bang on device load to trigger initialization)
 *
 * STORAGE:
 *   [dict ---mixdiff_data @parameter_enable 1 @embed 0]
 *     (no connections needed — JS accesses it by scripting name)
 *     Set scripting name to: "snapshotDict"
 *
 * UI (all in presentation mode, device height = 169px):
 *
 *   [live.text @text "Snapshot" @mode 1]
 *     Set scripting name to: "btnSnapshot"
 *     outlet 0 → [prepend snapshot] → [js mixdiff.js] inlet 0
 *
 *   [live.text @text "Diff" @mode 1]
 *     Set scripting name to: "btnDiff"
 *     outlet 0 → [prepend diff] → [js mixdiff.js] inlet 0
 *
 *   [live.menu]
 *     Set scripting name to: "menuA"
 *     outlet 0 → [prepend selectA] → [js mixdiff.js] inlet 0
 *
 *   [live.menu]
 *     Set scripting name to: "menuB"
 *     outlet 0 → [prepend selectB] → [js mixdiff.js] inlet 0
 *
 *   [jit.cellblock @rows 20 @cols 6 @selmode 1
 *       @colwidth 50 60 60 80 55 55 @hscroll 0 @vscroll 1]
 *     Set scripting name to: "diffTable"
 *
 *   [comment @text "MixDiff Ready"]
 *     Set scripting name to: "statusText"
 *
 * MESSAGE ROUTING:
 *   All UI messages flow through [prepend <command>] into js inlet 0.
 *   JS finds UI objects via this.patcher.getnamed() using scripting names.
 *
 * ============================================================
 */

// --- Max JS Configuration ---
inlets = 1;
outlets = 0; // We use getnamed() to talk to UI objects directly

// --- Constants ---
var MAX_SNAPSHOTS = 10;
var WARN_THRESHOLD = 5;
var CHUNK_SIZE = 5; // tracks per execution slice

// --- State ---
var snapshots = {};      // {name: {timestamp, data}}
var snapshotNames = [];  // ordered list of names
var selectedA = null;    // name of snapshot A
var selectedB = null;    // name of snapshot B
var initialized = false;
var captureInProgress = false;

// --- UI Object References (populated on init) ---
var ui = {
    diffTable: null,
    statusText: null,
    menuA: null,
    menuB: null,
    btnSnapshot: null,
    btnDiff: null
};

// ============================================================
// INITIALIZATION
// ============================================================

function bang() {
    // Called by live.thisdevice when device fully loads
    post("MixDiff: Initializing...\n");

    // Grab UI object references by scripting name
    ui.diffTable = getUI("diffTable");
    ui.statusText = getUI("statusText");
    ui.menuA = getUI("menuA");
    ui.menuB = getUI("menuB");
    ui.btnSnapshot = getUI("btnSnapshot");
    ui.btnDiff = getUI("btnDiff");

    // Load existing snapshots from dict
    loadFromDict();

    // Set up diff table column headers
    initDiffTable();

    // Populate menus and status
    updateMenus();
    updateStatus("Ready. " + snapshotNames.length + " snapshot(s) loaded.");

    initialized = true;
    post("MixDiff: Initialized. " + snapshotNames.length + " snapshot(s) found.\n");
}

function getUI(scriptingName) {
    var obj = this.patcher.getnamed(scriptingName);
    if (!obj) {
        post("MixDiff WARNING: UI object '" + scriptingName + "' not found. Check scripting names.\n");
    }
    return obj;
}

// ============================================================
// DICT READ/WRITE
// ============================================================

function loadFromDict() {
    try {
        var d = new Dict("---mixdiff_data");

        // Check if dict has snapshot data
        var keys = d.getkeys();
        if (!keys) {
            snapshots = {};
            snapshotNames = [];
            post("MixDiff: No existing snapshots in dict.\n");
            return;
        }

        // Load snapshot names (stored as a separate ordered list)
        var nameList = d.get("_snapshotOrder");
        if (nameList) {
            // Dict returns a single string if 1 item, array if multiple
            if (typeof nameList === "string") {
                snapshotNames = [nameList];
            } else {
                snapshotNames = [];
                for (var i = 0; i < nameList.length; i++) {
                    snapshotNames.push(nameList[i]);
                }
            }
        } else {
            snapshotNames = [];
        }

        // Load each snapshot's data
        snapshots = {};
        for (var i = 0; i < snapshotNames.length; i++) {
            var name = snapshotNames[i];
            var snapshotDict = d.get("snapshots::" + name);
            if (snapshotDict) {
                snapshots[name] = {
                    timestamp: d.get("snapshots::" + name + "::_timestamp"),
                    data: {}
                };
                // The full snapshot data tree lives under snapshots::<name>::data
                // We'll read it as a nested dict reference
                snapshots[name]._dictRef = true; // flag: data stays in dict, read on demand
            }
        }

        post("MixDiff: Loaded " + snapshotNames.length + " snapshot(s) from dict.\n");
    } catch (e) {
        post("MixDiff ERROR loading dict: " + e.message + "\n");
        snapshots = {};
        snapshotNames = [];
    }
}

function saveSnapshotToDict(name, timestamp, snapshotData) {
    try {
        var d = new Dict("---mixdiff_data");

        // Store the snapshot data under snapshots::<name>
        d.set("snapshots::" + name + "::_timestamp", timestamp);

        // Walk the snapshot data tree and store each value
        saveNestedData(d, "snapshots::" + name + "::data", snapshotData);

        // Update the ordered name list
        d.set("_snapshotOrder", snapshotNames);

        post("MixDiff: Saved snapshot '" + name + "' to dict.\n");
        return true;
    } catch (e) {
        post("MixDiff ERROR saving to dict: " + e.message + "\n");
        return false;
    }
}

function saveNestedData(dictObj, basePath, data) {
    var keys = Object.keys(data);
    for (var i = 0; i < keys.length; i++) {
        var key = keys[i];
        var val = data[key];
        var path = basePath + "::" + key;

        if (typeof val === "object" && val !== null) {
            // Recurse into nested objects
            saveNestedData(dictObj, path, val);
        } else {
            // Store leaf value
            dictObj.set(path, val);
        }
    }
}

function deleteSnapshotFromDict(name) {
    try {
        var d = new Dict("---mixdiff_data");
        d.remove("snapshots::" + name);

        // Remove from ordered list
        var idx = snapshotNames.indexOf(name);
        if (idx > -1) {
            snapshotNames.splice(idx, 1);
        }
        d.set("_snapshotOrder", snapshotNames);

        delete snapshots[name];
        post("MixDiff: Deleted snapshot '" + name + "'.\n");
    } catch (e) {
        post("MixDiff ERROR deleting snapshot: " + e.message + "\n");
    }
}

// ============================================================
// SNAPSHOT READING (from dict, for diff)
// ============================================================

function readSnapshotData(name) {
    // Read the full snapshot data tree from dict
    // Returns a nested JS object: {trackKey: {deviceKey: {paramName: value}}}
    try {
        var d = new Dict("---mixdiff_data");
        var result = {};
        var basePath = "snapshots::" + name + "::data";

        // Get track keys
        var trackKeys = d.getkeys(basePath);
        if (!trackKeys) return result;
        if (typeof trackKeys === "string") trackKeys = [trackKeys];

        for (var t = 0; t < trackKeys.length; t++) {
            var trackKey = trackKeys[t];
            var trackPath = basePath + "::" + trackKey;
            result[trackKey] = {};

            // Get device keys for this track
            var deviceKeys = d.getkeys(trackPath);
            if (!deviceKeys) continue;
            if (typeof deviceKeys === "string") deviceKeys = [deviceKeys];

            for (var dv = 0; dv < deviceKeys.length; dv++) {
                var deviceKey = deviceKeys[dv];
                var devicePath = trackPath + "::" + deviceKey;

                if (deviceKey === "_chains") {
                    // Handle Rack chains recursively
                    result[trackKey]["_chains"] = readChainsFromDict(d, devicePath);
                } else {
                    result[trackKey][deviceKey] = {};

                    // Get parameter keys for this device
                    var paramKeys = d.getkeys(devicePath);
                    if (!paramKeys) continue;
                    if (typeof paramKeys === "string") paramKeys = [paramKeys];

                    for (var p = 0; p < paramKeys.length; p++) {
                        var paramKey = paramKeys[p];
                        if (paramKey === "_chains") {
                            result[trackKey][deviceKey]["_chains"] =
                                readChainsFromDict(d, devicePath + "::_chains");
                        } else {
                            result[trackKey][deviceKey][paramKey] =
                                d.get(devicePath + "::" + paramKey);
                        }
                    }
                }
            }
        }

        return result;
    } catch (e) {
        post("MixDiff ERROR reading snapshot '" + name + "': " + e.message + "\n");
        return null;
    }
}

function readChainsFromDict(dictObj, chainsPath) {
    var result = {};
    var chainKeys = dictObj.getkeys(chainsPath);
    if (!chainKeys) return result;
    if (typeof chainKeys === "string") chainKeys = [chainKeys];

    for (var c = 0; c < chainKeys.length; c++) {
        var chainKey = chainKeys[c];
        var chainPath = chainsPath + "::" + chainKey;
        result[chainKey] = {};

        var deviceKeys = dictObj.getkeys(chainPath);
        if (!deviceKeys) continue;
        if (typeof deviceKeys === "string") deviceKeys = [deviceKeys];

        for (var dv = 0; dv < deviceKeys.length; dv++) {
            var deviceKey = deviceKeys[dv];
            var devicePath = chainPath + "::" + deviceKey;

            if (deviceKey === "_chains") {
                // Nested racks — recurse
                result[chainKey]["_chains"] = readChainsFromDict(dictObj, devicePath);
            } else {
                result[chainKey][deviceKey] = {};
                var paramKeys = dictObj.getkeys(devicePath);
                if (!paramKeys) continue;
                if (typeof paramKeys === "string") paramKeys = [paramKeys];

                for (var p = 0; p < paramKeys.length; p++) {
                    var paramKey = paramKeys[p];
                    if (paramKey === "_chains") {
                        result[chainKey][deviceKey]["_chains"] =
                            readChainsFromDict(dictObj, devicePath + "::_chains");
                    } else {
                        result[chainKey][deviceKey][paramKey] =
                            dictObj.get(devicePath + "::" + paramKey);
                    }
                }
            }
        }
    }
    return result;
}

// ============================================================
// SNAPSHOT CAPTURE (FOI-24 — stub, will implement traversal)
// ============================================================

function takeSnapshot() {
    if (captureInProgress) {
        post("MixDiff: Snapshot already in progress.\n");
        updateStatus("Snapshot already in progress...");
        return;
    }

    // Check snapshot cap
    if (snapshotNames.length >= MAX_SNAPSHOTS) {
        post("MixDiff: Maximum " + MAX_SNAPSHOTS + " snapshots reached. Delete one first.\n");
        updateStatus("Max " + MAX_SNAPSHOTS + " snapshots. Delete one first.");
        return;
    }

    // Generate default name with timestamp
    var now = new Date();
    var defaultName = "Snapshot " + (snapshotNames.length + 1) +
        " (" + formatTime(now) + ")";

    post("MixDiff: Taking snapshot '" + defaultName + "'...\n");
    updateStatus("Capturing snapshot...");
    captureInProgress = true;

    // --- FOI-24: Replace this stub with real LOM traversal ---
    var snapshotData = captureSessionParameters();

    if (snapshotData !== null) {
        var timestamp = now.toISOString();

        // Store in memory
        snapshots[defaultName] = {
            timestamp: timestamp,
            data: snapshotData
        };
        snapshotNames.push(defaultName);

        // Persist to dict
        if (saveSnapshotToDict(defaultName, timestamp, snapshotData)) {
            updateMenus();
            var paramCount = countParams(snapshotData);
            updateStatus("Captured: " + defaultName + " (" + paramCount + " params)");
            post("MixDiff: Snapshot complete. " + paramCount + " parameters captured.\n");

            // Warn at threshold
            if (snapshotNames.length >= WARN_THRESHOLD) {
                post("MixDiff: " + snapshotNames.length + "/" + MAX_SNAPSHOTS +
                    " snapshots used. Consider deleting old ones.\n");
            }
        } else {
            // Save failed — roll back
            delete snapshots[defaultName];
            snapshotNames.pop();
            updateStatus("ERROR: Failed to save snapshot.");
        }
    } else {
        updateStatus("ERROR: Snapshot capture failed. See Max Console.");
    }

    captureInProgress = false;
}

function captureSessionParameters() {
    // Full LOM traversal: tracks → devices → (chains → devices)* → parameters
    // Uses a single LiveAPI instance with goto() for performance.
    // Captures regular tracks, return tracks, and master track.

    try {
        var api = new LiveAPI("live_set");
        var data = {};
        var totalParams = 0;
        var errors = [];

        // Build list of all track paths to walk
        var trackPaths = [];

        // Regular tracks
        var numTracks = api.getcount("tracks");
        for (var t = 0; t < numTracks; t++) {
            trackPaths.push({
                path: "live_set tracks " + t,
                index: t,
                type: "track"
            });
        }

        // Return tracks
        var numReturns = api.getcount("return_tracks");
        for (var r = 0; r < numReturns; r++) {
            trackPaths.push({
                path: "live_set return_tracks " + r,
                index: r,
                type: "return"
            });
        }

        // Master track (single, not indexed)
        trackPaths.push({
            path: "live_set master_track",
            index: 0,
            type: "master"
        });

        post("MixDiff: Scanning " + trackPaths.length + " tracks...\n");

        // Walk each track
        for (var i = 0; i < trackPaths.length; i++) {
            var tp = trackPaths[i];

            try {
                api.goto(tp.path);

                // Build track key with type prefix for clarity
                var trackName = api.getstring("name");
                var trackPrefix = tp.type === "return" ? "R" + tp.index
                    : tp.type === "master" ? "M"
                    : String(tp.index);
                var trackKey = trackPrefix + ":" + trackName;

                data[trackKey] = {};

                // Walk devices on this track (recursive for Racks)
                var numDevices = api.getcount("devices");
                var trackResult = walkDevicesForCapture(api, tp.path, numDevices, errors);
                data[trackKey] = trackResult.data;
                totalParams += trackResult.paramCount;

            } catch (trackErr) {
                var errMsg = "Track " + tp.path + ": " + trackErr.message;
                errors.push(errMsg);
                post("MixDiff WARNING: " + errMsg + "\n");
            }

            // Progress update every 5 tracks
            if ((i + 1) % 5 === 0 || i === trackPaths.length - 1) {
                updateStatus("Scanning track " + (i + 1) + "/" + trackPaths.length +
                    " (" + totalParams + " params)...");
            }
        }

        if (errors.length > 0) {
            post("MixDiff: Snapshot completed with " + errors.length + " warning(s).\n");
            for (var e = 0; e < errors.length; e++) {
                post("  - " + errors[e] + "\n");
            }
        }

        post("MixDiff: Captured " + totalParams + " parameters across " +
            trackPaths.length + " tracks.\n");
        return data;

    } catch (e) {
        post("MixDiff ERROR in captureSessionParameters: " + e.message + "\n");
        return null;
    }
}

function walkDevicesForCapture(api, basePath, numDevices, errors) {
    // Recursively walk devices including Rack chains.
    // Returns {data: {...}, paramCount: N}
    var data = {};
    var paramCount = 0;

    for (var d = 0; d < numDevices; d++) {
        var devPath = basePath + " devices " + d;

        try {
            api.goto(devPath);
            var deviceName = api.getstring("name");
            var deviceKey = d + ":" + deviceName;
            data[deviceKey] = {};

            // Capture all parameters for this device
            var numParams = api.getcount("parameters");
            for (var p = 0; p < numParams; p++) {
                try {
                    api.goto(devPath + " parameters " + p);
                    var paramName = api.getstring("name");
                    var paramValue = api.get("value");

                    // LiveAPI.get() returns an array — extract the float value
                    if (paramValue && typeof paramValue === "object" && paramValue.length > 0) {
                        paramValue = paramValue[0];
                    }

                    data[deviceKey][paramName] = paramValue;
                    paramCount++;
                } catch (paramErr) {
                    errors.push("Param " + devPath + " parameters " + p +
                        ": " + paramErr.message);
                }
            }

            // Check for Rack chains (Instrument Rack, Audio Effect Rack, etc.)
            api.goto(devPath);
            var numChains = 0;
            try {
                numChains = api.getcount("chains");
            } catch (e) {
                // Not a Rack device — no chains, that's fine
                numChains = 0;
            }

            if (numChains > 0) {
                data[deviceKey]["_chains"] = {};

                for (var c = 0; c < numChains; c++) {
                    var chainPath = devPath + " chains " + c;

                    try {
                        api.goto(chainPath);
                        var chainName = api.getstring("name");
                        var chainKey = c + ":" + chainName;

                        // Recurse into devices within this chain
                        var chainDeviceCount = api.getcount("devices");
                        var chainResult = walkDevicesForCapture(
                            api, chainPath, chainDeviceCount, errors
                        );
                        data[deviceKey]["_chains"][chainKey] = chainResult.data;
                        paramCount += chainResult.paramCount;

                    } catch (chainErr) {
                        errors.push("Chain " + chainPath + ": " + chainErr.message);
                    }
                }
            }

        } catch (devErr) {
            errors.push("Device " + devPath + ": " + devErr.message);
        }
    }

    return { data: data, paramCount: paramCount };
}

// ============================================================
// DIFF ENGINE (FOI-25 — stub, will implement full diff)
// ============================================================

function showDiff() {
    if (!selectedA || !selectedB) {
        updateStatus("Select two snapshots to compare.");
        post("MixDiff: Cannot diff — select snapshots A and B first.\n");
        return;
    }

    if (selectedA === selectedB) {
        updateStatus("Select two different snapshots.");
        return;
    }

    post("MixDiff: Computing diff: '" + selectedA + "' vs '" + selectedB + "'...\n");
    updateStatus("Computing diff...");

    // Read both snapshots from dict
    var dataA = readSnapshotData(selectedA);
    var dataB = readSnapshotData(selectedB);

    if (!dataA || !dataB) {
        updateStatus("ERROR: Could not read snapshot data.");
        return;
    }

    // Compute the diff
    var diffResults = computeDiff(dataA, dataB);

    // Display results
    displayDiff(diffResults);

    var summary = diffResults.length + " change(s) between '" +
        selectedA + "' and '" + selectedB + "'";
    updateStatus(summary);
    post("MixDiff: " + summary + "\n");
}

function computeDiff(dataA, dataB) {
    // FOI-25: Full recursive diff implementation
    // Returns array of {type, track, device, param, before, after}
    //   type: "~" (changed), "+" (added), "-" (removed)

    var results = [];
    var allTrackKeys = mergeKeys(Object.keys(dataA), Object.keys(dataB));

    for (var t = 0; t < allTrackKeys.length; t++) {
        var trackKey = allTrackKeys[t];
        var trackA = dataA[trackKey];
        var trackB = dataB[trackKey];
        var trackDisplay = stripIndex(trackKey);

        if (!trackA) {
            // Entire track added
            results.push({
                type: "+", track: trackDisplay,
                device: "(all)", param: "—",
                before: "—", after: "(added)"
            });
            continue;
        }
        if (!trackB) {
            // Entire track removed
            results.push({
                type: "-", track: trackDisplay,
                device: "(all)", param: "—",
                before: "(removed)", after: "—"
            });
            continue;
        }

        // Compare devices within track
        var allDeviceKeys = mergeKeys(Object.keys(trackA), Object.keys(trackB));
        for (var d = 0; d < allDeviceKeys.length; d++) {
            var deviceKey = allDeviceKeys[d];
            if (deviceKey === "_chains") {
                // Recurse into chains
                var chainResults = diffChains(
                    trackA["_chains"] || {},
                    trackB["_chains"] || {},
                    trackDisplay
                );
                results = results.concat(chainResults);
                continue;
            }

            var devA = trackA[deviceKey];
            var devB = trackB[deviceKey];
            var deviceDisplay = stripIndex(deviceKey);

            if (!devA) {
                results.push({
                    type: "+", track: trackDisplay,
                    device: deviceDisplay, param: "—",
                    before: "—", after: "(added)"
                });
                continue;
            }
            if (!devB) {
                results.push({
                    type: "-", track: trackDisplay,
                    device: deviceDisplay, param: "—",
                    before: "(removed)", after: "—"
                });
                continue;
            }

            // Compare parameters within device
            diffParams(devA, devB, trackDisplay, deviceDisplay, results);
        }
    }

    return results;
}

function diffChains(chainsA, chainsB, trackDisplay) {
    var results = [];
    var allChainKeys = mergeKeys(Object.keys(chainsA), Object.keys(chainsB));

    for (var c = 0; c < allChainKeys.length; c++) {
        var chainKey = allChainKeys[c];
        var chainA = chainsA[chainKey] || {};
        var chainB = chainsB[chainKey] || {};
        var chainDisplay = trackDisplay + " > " + stripIndex(chainKey);

        var allDeviceKeys = mergeKeys(Object.keys(chainA), Object.keys(chainB));
        for (var d = 0; d < allDeviceKeys.length; d++) {
            var deviceKey = allDeviceKeys[d];
            if (deviceKey === "_chains") {
                // Nested rack — recurse deeper
                var nestedResults = diffChains(
                    chainA["_chains"] || {},
                    chainB["_chains"] || {},
                    chainDisplay
                );
                results = results.concat(nestedResults);
                continue;
            }

            var devA = chainA[deviceKey];
            var devB = chainB[deviceKey];
            var deviceDisplay = stripIndex(deviceKey);

            if (!devA) {
                results.push({
                    type: "+", track: chainDisplay,
                    device: deviceDisplay, param: "—",
                    before: "—", after: "(added)"
                });
                continue;
            }
            if (!devB) {
                results.push({
                    type: "-", track: chainDisplay,
                    device: deviceDisplay, param: "—",
                    before: "(removed)", after: "—"
                });
                continue;
            }

            diffParams(devA, devB, chainDisplay, deviceDisplay, results);
        }
    }
    return results;
}

function diffParams(devA, devB, trackDisplay, deviceDisplay, results) {
    var allParamKeys = mergeKeys(Object.keys(devA), Object.keys(devB));

    for (var p = 0; p < allParamKeys.length; p++) {
        var paramKey = allParamKeys[p];
        if (paramKey === "_chains" || paramKey === "_paramCount") continue;

        var valA = devA[paramKey];
        var valB = devB[paramKey];

        if (valA === undefined) {
            results.push({
                type: "+", track: trackDisplay,
                device: deviceDisplay, param: paramKey,
                before: "—", after: formatValue(valB)
            });
        } else if (valB === undefined) {
            results.push({
                type: "-", track: trackDisplay,
                device: deviceDisplay, param: paramKey,
                before: formatValue(valA), after: "—"
            });
        } else if (!valuesEqual(valA, valB)) {
            results.push({
                type: "~", track: trackDisplay,
                device: deviceDisplay, param: paramKey,
                before: formatValue(valA), after: formatValue(valB)
            });
        }
    }
}

// ============================================================
// UI DISPLAY
// ============================================================

function initDiffTable() {
    if (!ui.diffTable) return;
    var cb = ui.diffTable;

    // Set column count and headers
    cb.message("cols", 6);
    cb.message("colwidth", 0, 30);   // Change type
    cb.message("colwidth", 1, 80);   // Track
    cb.message("colwidth", 2, 80);   // Device
    cb.message("colwidth", 3, 90);   // Parameter
    cb.message("colwidth", 4, 60);   // Before
    cb.message("colwidth", 5, 60);   // After

    // Set headers (row 0)
    cb.message("set", 0, 0, "");
    cb.message("set", 0, 1, "Track");
    cb.message("set", 0, 2, "Device");
    cb.message("set", 0, 3, "Parameter");
    cb.message("set", 0, 4, "Before");
    cb.message("set", 0, 5, "After");
}

function displayDiff(diffResults) {
    if (!ui.diffTable) {
        post("MixDiff: Cannot display diff — diffTable not found.\n");
        return;
    }

    var cb = ui.diffTable;

    // Clear previous results (keep header row)
    cb.message("clear");
    initDiffTable();

    if (diffResults.length === 0) {
        cb.message("rows", 2);
        cb.message("set", 1, 1, "No changes detected.");
        return;
    }

    // Set row count: header + results
    cb.message("rows", diffResults.length + 1);

    for (var i = 0; i < diffResults.length; i++) {
        var row = i + 1; // skip header row
        var r = diffResults[i];

        cb.message("set", row, 0, r.type);
        cb.message("set", row, 1, r.track);
        cb.message("set", row, 2, r.device);
        cb.message("set", row, 3, r.param);
        cb.message("set", row, 4, r.before);
        cb.message("set", row, 5, r.after);
    }
}

function updateMenus() {
    updateMenu(ui.menuA, snapshotNames);
    updateMenu(ui.menuB, snapshotNames);
}

function updateMenu(menuObj, names) {
    if (!menuObj) return;

    // Clear existing items
    menuObj.message("clear");

    if (names.length === 0) {
        menuObj.message("append", "(no snapshots)");
    } else {
        for (var i = 0; i < names.length; i++) {
            menuObj.message("append", names[i]);
        }
    }
}

function updateStatus(text) {
    if (ui.statusText) {
        ui.statusText.message("set", text);
    }
    // Always log to console as well
    post("MixDiff: " + text + "\n");
}

// ============================================================
// MESSAGE ROUTING — receives messages from patcher
// ============================================================

function anything() {
    var msg = messagename;
    var args = arrayfromargs(arguments);

    switch (msg) {
        case "snapshot":
            // live.text toggle sends 0 and 1 — only fire on press (1)
            if (args.length > 0 && args[0] === 1) {
                takeSnapshot();
            }
            break;

        case "diff":
            // live.text toggle sends 0 and 1 — only fire on press (1)
            if (args.length > 0 && args[0] === 1) {
                showDiff();
            }
            break;

        case "selectA":
            if (args.length > 0 && args[0] >= 0 && args[0] < snapshotNames.length) {
                selectedA = snapshotNames[args[0]];
                post("MixDiff: Selected A = '" + selectedA + "'\n");
            }
            break;

        case "selectB":
            if (args.length > 0 && args[0] >= 0 && args[0] < snapshotNames.length) {
                selectedB = snapshotNames[args[0]];
                post("MixDiff: Selected B = '" + selectedB + "'\n");
            }
            break;

        case "delete":
            if (args.length > 0 && args[0] >= 0 && args[0] < snapshotNames.length) {
                var nameToDelete = snapshotNames[args[0]];
                deleteSnapshotFromDict(nameToDelete);
                updateMenus();
                updateStatus("Deleted '" + nameToDelete + "'. " +
                    snapshotNames.length + " remaining.");
            }
            break;

        default:
            post("MixDiff: Unknown message '" + msg + "'\n");
    }
}

// ============================================================
// UTILITY FUNCTIONS
// ============================================================

function makeKey(index, name) {
    return index + ":" + name;
}

function stripIndex(key) {
    // "0:Vocals" → "Vocals"
    var colonIdx = key.indexOf(":");
    if (colonIdx > -1) {
        return key.substring(colonIdx + 1);
    }
    return key;
}

function mergeKeys(keysA, keysB) {
    // Combine two key arrays, preserving order from A then adding new from B
    var seen = {};
    var result = [];

    for (var i = 0; i < keysA.length; i++) {
        if (!seen[keysA[i]]) {
            result.push(keysA[i]);
            seen[keysA[i]] = true;
        }
    }
    for (var j = 0; j < keysB.length; j++) {
        if (!seen[keysB[j]]) {
            result.push(keysB[j]);
            seen[keysB[j]] = true;
        }
    }
    return result;
}

function formatValue(val) {
    if (val === null || val === undefined) return "—";
    if (typeof val === "number") {
        // Round to 2 decimal places for readability
        return (Math.round(val * 100) / 100).toString();
    }
    return String(val);
}

function valuesEqual(a, b) {
    // Float comparison with tolerance for parameter values
    if (typeof a === "number" && typeof b === "number") {
        return Math.abs(a - b) < 0.0001;
    }
    return a === b;
}

function countParams(data) {
    var count = 0;
    var trackKeys = Object.keys(data);
    for (var t = 0; t < trackKeys.length; t++) {
        count += countDeviceParams(data[trackKeys[t]]);
    }
    return count;
}

function countDeviceParams(devices) {
    var count = 0;
    var keys = Object.keys(devices);
    for (var d = 0; d < keys.length; d++) {
        var key = keys[d];
        if (key === "_chains") {
            // Recurse into chains
            var chainKeys = Object.keys(devices["_chains"]);
            for (var c = 0; c < chainKeys.length; c++) {
                count += countDeviceParams(devices["_chains"][chainKeys[c]]);
            }
            continue;
        }
        var device = devices[key];
        if (typeof device !== "object") continue;
        var paramKeys = Object.keys(device);
        for (var p = 0; p < paramKeys.length; p++) {
            if (paramKeys[p] !== "_chains" && paramKeys[p] !== "_paramCount") {
                count++;
            }
        }
        // Count params in nested chains within this device
        if (device["_chains"]) {
            var nestedChainKeys = Object.keys(device["_chains"]);
            for (var nc = 0; nc < nestedChainKeys.length; nc++) {
                count += countDeviceParams(device["_chains"][nestedChainKeys[nc]]);
            }
        }
    }
    return count;
}

function formatTime(date) {
    var h = date.getHours();
    var m = date.getMinutes();
    var ampm = h >= 12 ? "pm" : "am";
    h = h % 12;
    if (h === 0) h = 12;
    return h + ":" + (m < 10 ? "0" : "") + m + ampm;
}

post("MixDiff: Script loaded. Waiting for device init...\n");
