"""
MP3 to MIDI — Audio-to-MIDI Transcription Tool
Uses Spotify's basic-pitch for polyphonic audio transcription.
Retro terminal GUI matching Audio Scribe / Resume Tailor aesthetic.
"""

import os
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

# ── Theme Constants ──────────────────────────────────────────────────────────
BG_COLOR = "#1a1a1a"
FG_COLOR = "#00ff00"
TEXT_BG = "#0d0d0d"
ACCENT_COLOR = "#00aaff"
PLACEHOLDER_COLOR = "#666666"
ERROR_COLOR = "#ff4444"
WARN_COLOR = "#ffaa00"
MONO_FONT = ("Courier New", 10)
MONO_FONT_BOLD = ("Courier New", 10, "bold")
TITLE_FONT = ("Courier New", 7)
HEADER_FONT = ("Courier New", 12, "bold")

# ── File Format Constants ────────────────────────────────────────────────────
SUPPORTED_INPUT = (
    ("Audio Files", "*.mp3 *.wav *.ogg *.flac *.m4a"),
    ("MP3", "*.mp3"),
    ("WAV", "*.wav"),
    ("FLAC", "*.flac"),
    ("OGG", "*.ogg"),
    ("All Files", "*.*"),
)

ASCII_HEADER = r"""
  ╔═══════════════════════════════════════════════════════╗
  ║  ███╗   ███╗██╗██████╗ ██╗                           ║
  ║  ████╗ ████║██║██╔══██╗██║                           ║
  ║  ██╔████╔██║██║██║  ██║██║                           ║
  ║  ██║╚██╔╝██║██║██║  ██║██║                           ║
  ║  ██║ ╚═╝ ██║██║██████╔╝██║                           ║
  ║  ╚═╝     ╚═╝╚═╝╚═════╝ ╚═╝                           ║
  ║  ███████╗██╗  ██╗████████╗██████╗  █████╗  ██████╗   ║
  ║  ██╔════╝╚██╗██╔╝╚══██╔══╝██╔══██╗██╔══██╗██╔════╝   ║
  ║  █████╗   ╚███╔╝    ██║   ██████╔╝███████║██║         ║
  ║  ██╔══╝   ██╔██╗    ██║   ██╔══██╗██╔══██║██║         ║
  ║  ███████╗██╔╝ ██╗   ██║   ██║  ██║██║  ██║╚██████╗   ║
  ║  ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝   ║
  ║                                                       ║
  ║  Audio-to-MIDI Transcription       [basic-pitch]      ║
  ╚═══════════════════════════════════════════════════════╝
"""


class MidiExtractApp:
    """Main application window for MP3-to-MIDI conversion."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MIDI Extract")
        self.root.configure(bg=BG_COLOR)
        self.root.geometry("680x620")
        self.root.minsize(600, 500)

        self.input_path: str = ""
        self.output_path: str = ""
        self.converting = False

        self._build_ui()

    def _build_ui(self):
        """Construct the full GUI layout."""
        main = tk.Frame(self.root, bg=BG_COLOR, padx=20, pady=10)
        main.pack(fill=tk.BOTH, expand=True)

        # ── ASCII Header ─────────────────────────────────────────────────
        header = tk.Label(
            main, text=ASCII_HEADER, font=TITLE_FONT,
            bg=BG_COLOR, fg=ACCENT_COLOR, justify=tk.LEFT,
        )
        header.pack(pady=(0, 5))

        # ── Separator ────────────────────────────────────────────────────
        self._separator(main)

        # ── Input File Section ───────────────────────────────────────────
        input_frame = tk.Frame(main, bg=BG_COLOR)
        input_frame.pack(fill=tk.X, pady=(10, 5))

        tk.Label(
            input_frame, text="INPUT FILE:", font=MONO_FONT_BOLD,
            bg=BG_COLOR, fg=ACCENT_COLOR,
        ).pack(side=tk.LEFT)

        tk.Button(
            input_frame, text="[ BROWSE ]", font=MONO_FONT_BOLD,
            bg=BG_COLOR, fg=FG_COLOR,
            activebackground=BG_COLOR, activeforeground=ACCENT_COLOR,
            relief=tk.FLAT, cursor="hand2",
            command=self._browse_input,
        ).pack(side=tk.RIGHT)

        self.input_label = tk.Label(
            main, text="No file selected", font=MONO_FONT,
            bg=BG_COLOR, fg=PLACEHOLDER_COLOR, anchor=tk.W,
        )
        self.input_label.pack(fill=tk.X, pady=(0, 5))

        # ── Output File Section ──────────────────────────────────────────
        output_frame = tk.Frame(main, bg=BG_COLOR)
        output_frame.pack(fill=tk.X, pady=(5, 5))

        tk.Label(
            output_frame, text="OUTPUT FILE:", font=MONO_FONT_BOLD,
            bg=BG_COLOR, fg=ACCENT_COLOR,
        ).pack(side=tk.LEFT)

        tk.Button(
            output_frame, text="[ BROWSE ]", font=MONO_FONT_BOLD,
            bg=BG_COLOR, fg=FG_COLOR,
            activebackground=BG_COLOR, activeforeground=ACCENT_COLOR,
            relief=tk.FLAT, cursor="hand2",
            command=self._browse_output,
        ).pack(side=tk.RIGHT)

        self.output_label = tk.Label(
            main, text="Auto-generated from input filename", font=MONO_FONT,
            bg=BG_COLOR, fg=PLACEHOLDER_COLOR, anchor=tk.W,
        )
        self.output_label.pack(fill=tk.X, pady=(0, 5))

        # ── Separator ────────────────────────────────────────────────────
        self._separator(main)

        # ── Parameters Section ───────────────────────────────────────────
        tk.Label(
            main, text="PARAMETERS:", font=MONO_FONT_BOLD,
            bg=BG_COLOR, fg=ACCENT_COLOR, anchor=tk.W,
        ).pack(fill=tk.X, pady=(10, 5))

        params_frame = tk.Frame(main, bg=BG_COLOR)
        params_frame.pack(fill=tk.X, pady=(0, 5))

        # Onset threshold
        onset_row = tk.Frame(params_frame, bg=BG_COLOR)
        onset_row.pack(fill=tk.X, pady=2)
        tk.Label(
            onset_row, text="Onset Threshold:", font=MONO_FONT,
            bg=BG_COLOR, fg=FG_COLOR, width=22, anchor=tk.W,
        ).pack(side=tk.LEFT)
        self.onset_var = tk.StringVar(value="0.5")
        self.onset_entry = tk.Entry(
            onset_row, textvariable=self.onset_var, font=MONO_FONT,
            bg=TEXT_BG, fg=FG_COLOR, insertbackground=FG_COLOR,
            relief=tk.FLAT, width=8, borderwidth=2,
        )
        self.onset_entry.pack(side=tk.LEFT)
        tk.Label(
            onset_row, text="(0.0-1.0, higher = fewer notes)", font=MONO_FONT,
            bg=BG_COLOR, fg=PLACEHOLDER_COLOR,
        ).pack(side=tk.LEFT, padx=(10, 0))

        # Frame threshold
        frame_row = tk.Frame(params_frame, bg=BG_COLOR)
        frame_row.pack(fill=tk.X, pady=2)
        tk.Label(
            frame_row, text="Frame Threshold:", font=MONO_FONT,
            bg=BG_COLOR, fg=FG_COLOR, width=22, anchor=tk.W,
        ).pack(side=tk.LEFT)
        self.frame_var = tk.StringVar(value="0.3")
        self.frame_entry = tk.Entry(
            frame_row, textvariable=self.frame_var, font=MONO_FONT,
            bg=TEXT_BG, fg=FG_COLOR, insertbackground=FG_COLOR,
            relief=tk.FLAT, width=8, borderwidth=2,
        )
        self.frame_entry.pack(side=tk.LEFT)
        tk.Label(
            frame_row, text="(0.0-1.0, higher = shorter notes)", font=MONO_FONT,
            bg=BG_COLOR, fg=PLACEHOLDER_COLOR,
        ).pack(side=tk.LEFT, padx=(10, 0))

        # Min note length
        minlen_row = tk.Frame(params_frame, bg=BG_COLOR)
        minlen_row.pack(fill=tk.X, pady=2)
        tk.Label(
            minlen_row, text="Min Note Length (ms):", font=MONO_FONT,
            bg=BG_COLOR, fg=FG_COLOR, width=22, anchor=tk.W,
        ).pack(side=tk.LEFT)
        self.minlen_var = tk.StringVar(value="127.70")
        self.minlen_entry = tk.Entry(
            minlen_row, textvariable=self.minlen_var, font=MONO_FONT,
            bg=TEXT_BG, fg=FG_COLOR, insertbackground=FG_COLOR,
            relief=tk.FLAT, width=8, borderwidth=2,
        )
        self.minlen_entry.pack(side=tk.LEFT)
        tk.Label(
            minlen_row, text="(filter short artifacts)", font=MONO_FONT,
            bg=BG_COLOR, fg=PLACEHOLDER_COLOR,
        ).pack(side=tk.LEFT, padx=(10, 0))

        # MIDI tempo
        tempo_row = tk.Frame(params_frame, bg=BG_COLOR)
        tempo_row.pack(fill=tk.X, pady=2)
        tk.Label(
            tempo_row, text="MIDI Tempo (BPM):", font=MONO_FONT,
            bg=BG_COLOR, fg=FG_COLOR, width=22, anchor=tk.W,
        ).pack(side=tk.LEFT)
        self.tempo_var = tk.StringVar(value="120")
        self.tempo_entry = tk.Entry(
            tempo_row, textvariable=self.tempo_var, font=MONO_FONT,
            bg=TEXT_BG, fg=FG_COLOR, insertbackground=FG_COLOR,
            relief=tk.FLAT, width=8, borderwidth=2,
        )
        self.tempo_entry.pack(side=tk.LEFT)

        # ── Separator ────────────────────────────────────────────────────
        self._separator(main)

        # ── Convert Button ───────────────────────────────────────────────
        self.convert_btn = tk.Button(
            main, text="[ EXTRACT MIDI ]", font=HEADER_FONT,
            bg=BG_COLOR, fg=FG_COLOR,
            activebackground=BG_COLOR, activeforeground=ACCENT_COLOR,
            relief=tk.FLAT, cursor="hand2",
            command=self._start_conversion,
        )
        self.convert_btn.pack(pady=(15, 10))

        # ── Status ───────────────────────────────────────────────────────
        self.status_label = tk.Label(
            main, text="Ready.", font=MONO_FONT,
            bg=BG_COLOR, fg=FG_COLOR, anchor=tk.W,
        )
        self.status_label.pack(fill=tk.X, pady=(5, 0))

        self.progress_label = tk.Label(
            main, text="", font=MONO_FONT,
            bg=BG_COLOR, fg=ACCENT_COLOR, anchor=tk.W,
        )
        self.progress_label.pack(fill=tk.X, pady=(2, 0))

    def _separator(self, parent: tk.Frame):
        """Add a green horizontal separator line."""
        sep = tk.Frame(parent, bg=FG_COLOR, height=1)
        sep.pack(fill=tk.X, pady=5)

    def _browse_input(self):
        """Open file dialog to select input audio file."""
        path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=SUPPORTED_INPUT,
        )
        if path:
            self.input_path = path
            self.input_label.config(text=path, fg=FG_COLOR)
            # Auto-set output path
            out = str(Path(path).with_suffix(".mid"))
            self.output_path = out
            self.output_label.config(text=out, fg=FG_COLOR)

    def _browse_output(self):
        """Open file dialog to select output MIDI file location."""
        initial_dir = str(Path(self.input_path).parent) if self.input_path else None
        initial_name = Path(self.input_path).stem + ".mid" if self.input_path else "output.mid"
        path = filedialog.asksaveasfilename(
            title="Save MIDI File",
            initialdir=initial_dir,
            initialfile=initial_name,
            defaultextension=".mid",
            filetypes=[("MIDI Files", "*.mid"), ("All Files", "*.*")],
        )
        if path:
            self.output_path = path
            self.output_label.config(text=path, fg=FG_COLOR)

    def _validate_params(self) -> dict | None:
        """Validate and return conversion parameters, or None on error."""
        try:
            onset = float(self.onset_var.get())
            if not 0.0 <= onset <= 1.0:
                raise ValueError("Onset threshold must be between 0.0 and 1.0")
        except ValueError as e:
            messagebox.showerror("Invalid Parameter", f"Onset Threshold: {e}")
            return None

        try:
            frame = float(self.frame_var.get())
            if not 0.0 <= frame <= 1.0:
                raise ValueError("Frame threshold must be between 0.0 and 1.0")
        except ValueError as e:
            messagebox.showerror("Invalid Parameter", f"Frame Threshold: {e}")
            return None

        try:
            minlen = float(self.minlen_var.get())
            if minlen < 0:
                raise ValueError("Min note length must be positive")
        except ValueError as e:
            messagebox.showerror("Invalid Parameter", f"Min Note Length: {e}")
            return None

        try:
            tempo = float(self.tempo_var.get())
            if tempo <= 0:
                raise ValueError("Tempo must be positive")
        except ValueError as e:
            messagebox.showerror("Invalid Parameter", f"MIDI Tempo: {e}")
            return None

        return {
            "onset_threshold": onset,
            "frame_threshold": frame,
            "minimum_note_length": minlen,
            "midi_tempo": tempo,
        }

    def _set_status(self, text: str, color: str = FG_COLOR):
        """Update status label (thread-safe via root.after)."""
        self.root.after(0, lambda: self.status_label.config(text=text, fg=color))

    def _set_progress(self, text: str, color: str = ACCENT_COLOR):
        """Update progress label (thread-safe via root.after)."""
        self.root.after(0, lambda: self.progress_label.config(text=text, fg=color))

    def _set_converting(self, state: bool):
        """Toggle UI state during conversion."""
        self.converting = state
        btn_text = "[ CONVERTING... ]" if state else "[ EXTRACT MIDI ]"
        btn_state = tk.DISABLED if state else tk.NORMAL
        self.root.after(0, lambda: self.convert_btn.config(text=btn_text, state=btn_state))

    def _start_conversion(self):
        """Validate inputs and launch conversion in background thread."""
        if self.converting:
            return

        if not self.input_path:
            messagebox.showwarning("No Input", "Please select an audio file first.")
            return

        if not os.path.isfile(self.input_path):
            messagebox.showerror("File Not Found", f"Cannot find:\n{self.input_path}")
            return

        params = self._validate_params()
        if params is None:
            return

        if not self.output_path:
            self.output_path = str(Path(self.input_path).with_suffix(".mid"))

        self._set_converting(True)
        thread = threading.Thread(
            target=self._convert, args=(self.input_path, self.output_path, params),
            daemon=True,
        )
        thread.start()

    def _convert(self, input_path: str, output_path: str, params: dict):
        """Run basic-pitch conversion in background thread."""
        try:
            self._set_status("Loading basic-pitch model...", ACCENT_COLOR)
            self._set_progress("")

            from basic_pitch.inference import predict

            self._set_status(f"Transcribing: {Path(input_path).name}", ACCENT_COLOR)
            self._set_progress("This may take a moment for longer files...")

            model_output, midi_data, note_events = predict(
                input_path,
                onset_threshold=params["onset_threshold"],
                frame_threshold=params["frame_threshold"],
                minimum_note_length=params["minimum_note_length"],
                midi_tempo=params["midi_tempo"],
            )

            self._set_status("Writing MIDI file...", ACCENT_COLOR)
            midi_data.write(output_path)

            # Verify output exists
            if not os.path.isfile(output_path):
                raise FileNotFoundError(f"MIDI file was not created at {output_path}")

            file_size = os.path.getsize(output_path)
            note_count = len(note_events)

            self._set_status(
                f"Done! {note_count} notes extracted. ({file_size:,} bytes)", FG_COLOR,
            )
            self._set_progress(f"Saved: {output_path}", FG_COLOR)

        except ImportError:
            self._set_status("ERROR: basic-pitch not installed", ERROR_COLOR)
            self._set_progress("Run: pip install basic-pitch[onnx]", WARN_COLOR)
        except Exception as e:
            self._set_status(f"ERROR: {e}", ERROR_COLOR)
            self._set_progress("", ERROR_COLOR)
        finally:
            self._set_converting(False)


def main():
    root = tk.Tk()
    root.iconname("MIDI Extract")
    MidiExtractApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
