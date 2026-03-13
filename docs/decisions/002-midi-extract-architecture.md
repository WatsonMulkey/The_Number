# ADR 002: MIDI Extract — Architecture Decisions

**Status:** Proposed
**Date:** 2026-03-03
**Decision Makers:** Watson Mulkey, Claude (with senior-dev-skeptic review)

---

## Context

Watson wants a desktop tool that converts audio files (MP3, WAV, FLAC, OGG) to MIDI. Key constraints:
- Must work offline — no cloud APIs
- Must be distributable as a standalone .exe
- Retro terminal aesthetic matching Audio Scribe / Resume Tailor
- Polyphonic transcription (full mixes, not just monophonic melodies)

## Decisions

### 1. basic-pitch over alternatives for audio-to-MIDI transcription

**Decision:** Use Spotify's `basic-pitch` library

**Options Considered:**
- `basic-pitch` — Spotify's open-source polyphonic pitch detection, small model (<17K params), ONNX support on Windows
- `omnizart` — Handles drums/vocals/chords separately, but heavier dependencies and less maintained
- `magenta` (Google Onsets & Frames) — Excellent for piano, but TensorFlow-only and narrow instrument support
- `basicpitch.cpp` — C++ port, smaller binary, but requires C++ build toolchain and less flexible

**Why:** basic-pitch has the best quality-to-complexity ratio. It handles polyphonic audio, supports multiple formats, and on Windows defaults to ONNX runtime (no TensorFlow). The model is tiny. The API is 3 lines.

**Risk:** The dependency chain includes librosa → numba → llvmlite, which adds ~100MB to bundled executables. Acceptable for v1; can be optimized later with a custom ONNX inference wrapper.

### 2. ONNX Runtime over TensorFlow

**Decision:** Use `basic-pitch[onnx]` install, which uses ONNX Runtime instead of TensorFlow

**Options Considered:**
- Full TensorFlow — 500MB+, slow startup, difficult to bundle
- TensorFlow Lite — lighter but not the default on Windows
- ONNX Runtime — ~20MB, fast inference, default backend on Windows
- CoreML — macOS only

**Why:** ONNX Runtime is the default on Windows, significantly smaller than TensorFlow, and basic-pitch's model quality is identical across backends. This is the clear choice for a Windows-targeted distributable.

### 3. Single-file Tkinter app (consistent with Audio Scribe / Resume Tailor)

**Decision:** Everything in `mp3_to_midi.py`. Tkinter GUI with retro terminal theme.

**Why:** Same rationale as ADR 001. The app is <300 lines of functional code. Tkinter is zero-dependency, and the retro theme is already a proven pattern across Watson's desktop tools. Consistency matters.

**When to revisit:** If batch processing, stem separation (DEMUCS pipeline), or other features push the file past 1500 lines.

### 4. threading.Thread for background conversion

**Decision:** Run basic-pitch inference in a background thread, update GUI via `root.after()`.

**Why:** Same pattern as Audio Scribe (ADR 001, Decision 5). basic-pitch's `predict()` is a blocking call that can take 10-60 seconds. Must not freeze the GUI. `root.after()` is the safe way to update Tkinter from a background thread.

### 5. PyInstaller for distribution (deferred to v1.1)

**Decision:** Plan for PyInstaller bundling but ship as a Python script first.

**Known PyInstaller gotchas (from research):**
- ONNX Runtime DLL loading requires `collect_all('onnxruntime')` + explicit hidden imports
- librosa/numba/llvmlite chain requires manual DLL collection
- basic-pitch model files must be bundled as data
- Expected exe size: ~200-400MB

**Why:** Get the tool working and validated first. PyInstaller bundling has known gotchas that warrant their own focused effort. Audio Scribe followed the same phased approach.

### 6. Expose tuning parameters in the GUI

**Decision:** Expose onset threshold, frame threshold, min note length, and MIDI tempo as user-adjustable parameters with sensible defaults.

**Options Considered:**
- Hardcoded defaults, no user control — simplest but frustrating when results are noisy
- Config file — adds file management complexity
- GUI controls with defaults — best UX, lets users iterate quickly

**Why:** Audio-to-MIDI quality varies by source material. A dense mix needs different thresholds than a solo instrument. Exposing these controls lets users dial in quality without editing code.

## Consequences

- **librosa dependency chain**: Pulls in numba + llvmlite + LLVM binaries (~100MB). Acceptable for v1. Future optimization: custom ONNX inference wrapper using only soundfile + scipy + onnxruntime.
- **No stem separation in v1**: Full mixes will produce noisier MIDI than isolated instruments. Users can pre-separate stems externally. DEMUCS integration is a potential v2 feature.
- **No real-time preview**: Conversion is batch-only. A playback feature could be added later using pygame.midi or similar.
