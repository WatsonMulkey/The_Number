# MIDI Extract (mp3-to-midi)

## Project Overview
Audio-to-MIDI transcription tool using basic-pitch (Spotify). Retro terminal GUI matching Audio Scribe / Resume Tailor aesthetic.

## Stack
- Python 3.13, single-file app (`mp3_to_midi.py`)
- `basic-pitch` (Spotify) for polyphonic audio-to-MIDI transcription
- ONNX Runtime backend (NOT TensorFlow)
- Tkinter GUI with retro terminal theme
- Input: MP3, WAV, OGG, FLAC, M4A

## Key Patterns
- Threading: `threading.Thread` for background conversion (same pattern as Audio Scribe)
- Single-file app — all logic in `mp3_to_midi.py`
- PyInstaller build deferred to v1.1

## ADR
- `docs/decisions/002-midi-extract-architecture.md`
- Linear: FOI team, MIDI Extract label (green #10B981), tickets FOI-14 through FOI-17

## Running
```bash
pip install -r requirements.txt
python mp3_to_midi.py
```

## Status
- Draft implementation complete
- ADR: Accepted (skeptic-reviewed 2026-03-03)
