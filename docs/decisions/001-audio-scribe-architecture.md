# ADR 001: Audio Scribe — Architecture Decisions

**Status:** Accepted
**Date:** 2026-02-26
**Decision Makers:** Watson Mulkey, Claude (with skeptic + research orchestrator review)

---

## Context

Watson needs a local, offline audio transcription tool. Key constraints:
- Must run entirely offline — no cloud APIs
- Must handle iPhone audio formats (m4a, caf)
- Must be simple to launch (`python audio_scribe.py`)
- Retro terminal aesthetic matching Resume Tailor

## Decisions

### 1. faster-whisper over openai-whisper

**Decision:** Use `faster-whisper` (CTranslate2 backend)

**Options Considered:**
- `openai-whisper` — official, well-documented, but 4x slower and higher memory
- `faster-whisper` — CTranslate2 backend, 4x faster, lower memory, same model quality
- Cloud APIs (Deepgram, AssemblyAI) — rejected per offline constraint

**Why:** Speed matters for a desktop tool. 4x faster means a 10-minute audio file completes in ~1 minute vs ~4 minutes. CTranslate2 has Python 3.13 wheels on Windows (verified).

**Risk:** CTranslate2 is a compiled C++ dependency. If wheels break on a future Python version, fall back to openai-whisper.

### 2. subprocess + FFmpeg over pydub for conversion

**Decision:** Use `subprocess.run(["ffmpeg", ...])` for audio format conversion. Use pydub only for lightweight metadata (duration, format detection).

**Options Considered:**
- `pydub.AudioSegment.from_file()` — convenient API but loads entire file into memory
- `subprocess` + FFmpeg directly — constant memory, streams data

**Why:** A 2-hour audio file is 100-300MB on disk. pydub loads the entire decoded PCM into memory (16-bit mono at 16kHz = ~230MB for 2 hours). subprocess + FFmpeg streams the conversion with constant ~10MB memory.

**Tradeoff:** Requires FFmpeg as a system dependency. App includes startup check with install instructions.

### 3. Single-file application

**Decision:** Everything in `audio_scribe.py`. No modules, no config files, no package structure.

**Options Considered:**
- Multi-file package (`audio_scribe/transcriber.py`, `gui.py`, `exports.py`)
- Single file with sections

**Why:** The app is ~600 lines of functional code. Splitting into modules adds import complexity without benefit. Resume Tailor started as a single file and only split when it hit 2000+ lines. Audio Scribe is well under that threshold.

**When to revisit:** If the file exceeds 1500 lines or if Ollama/LM Studio integration (Phase 2) adds significant complexity.

### 4. Tkinter over alternatives

**Decision:** Tkinter for the GUI framework

**Options Considered:**
- Tkinter — built into Python, no install, retro aesthetic is natural
- PySide6/Qt — more polished but 100MB+ dependency, overkill for this
- Web UI (Flask + browser) — adds network layer, browser dependency
- Terminal UI (textual/rich) — good but file dialogs and copy-paste are awkward

**Why:** Zero additional dependencies. Retro terminal theme works perfectly with Tkinter's flat styling. Resume Tailor proved the pattern works.

### 5. threading.Thread + queue.Queue for concurrency

**Decision:** Background thread communicates with GUI via queue, polled by `root.after(100, check_queue)`.

**Options Considered:**
- `root.update()` from background thread — **rejected**, Tkinter is not thread-safe, causes random crashes
- `asyncio` — doesn't integrate well with Tkinter's event loop
- `multiprocessing` — overkill, adds IPC complexity
- `concurrent.futures.ThreadPoolExecutor` — fine but queue pattern is simpler for progress reporting

**Why:** This is the standard safe pattern for Tkinter + background work. The queue allows typed messages (status, segment, complete, error, cancelled) with clean separation.

### 6. Default to tiny model

**Decision:** Default model selection is `tiny` (75MB)

**Why:** First-run experience matters. Downloading 75MB is fast. User can verify the tool works before committing to a 500MB+ model download. The tiny model is adequate for clear speech in quiet environments.

## Consequences

- **FFmpeg dependency**: Users must install FFmpeg separately. The app checks on startup and shows clear instructions if missing. This is the primary friction point for first-time setup.
- **No GPU acceleration by default**: Uses CPU + int8 quantization. GPU users can modify the device parameter. A future enhancement could auto-detect CUDA.
- **No bundled executable yet**: Requires Python installation. PyInstaller packaging is planned but deferred — CTranslate2's compiled binaries need special `--collect-all` flags.
- **Phase 2 (Ollama integration) deferred**: Ship transcription first, add LLM summarization later. This keeps v1 focused and useful immediately.
