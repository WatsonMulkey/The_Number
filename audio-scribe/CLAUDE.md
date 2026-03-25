# Audio Scribe

## Status: Complete — functional, Phase 2 (Ollama) deferred

## Project Overview
Local, offline audio transcription tool using `faster-whisper`. Retro terminal GUI (Tkinter) matching Resume Tailor's aesthetic.

## Stack
- Python 3.13, single-file app (`audio_scribe.py`)
- `faster-whisper` for transcription (CTranslate2 backend)
- `subprocess` + FFmpeg for audio conversion (NOT pydub — memory)
- `pydub` only for metadata (duration/format detection)
- Tkinter GUI with retro terminal theme
- Exports: TXT, SRT, VTT, JSON, DOCX

## Key Patterns
- Threading: `threading.Thread` + `queue.Queue` + `root.after()` polling — NEVER `root.update()` from background thread
- Cancellation: `threading.Event` checked between segments
- Temp files: context manager + `atexit` + `gc.collect()` retry for Windows locking
- FFmpeg: app searches common install paths if `shutil.which` fails

## Dependencies
```
faster-whisper
pydub
python-docx
```

## Running
```bash
python audio_scribe.py
```
