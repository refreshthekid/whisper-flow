# Whisper Flow

A local, free clone of [Wispr Flow](https://wisprflow.ai). Hold **Right Alt** anywhere on your computer, speak, release — your words get transcribed and pasted into whatever app you're focused on.

Runs 100% offline using [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (a 4× faster reimplementation of OpenAI's Whisper). No API keys, no subscriptions, no data leaves your machine.

## Features

- **System-wide hotkey.** Hold Right Alt anywhere — browser, Word, terminal, Discord — and dictate.
- **Local transcription.** Whisper `medium` model with `int8` quantization. Good accuracy, ~1–3s latency on modern CPUs.
- **System tray icon.** Right-click to quit.
- **Single-instance lock.** Can't accidentally run two copies that double-paste.
- **Auto-starts at login.** Installer drops a shortcut in your Startup folder.

## Requirements

- Windows 10 or 11
- Python 3.10 or newer ([download here](https://www.python.org/downloads/) — check "Add Python to PATH" during install)
- ~1 GB free disk (for the Whisper model + dependencies)
- A microphone

## Install

### Option 1: with Claude Code (easiest)

Open Claude Code in the folder where you cloned this repo and say:

> Install this Whisper Flow tool. Run install.bat.

That's it. Claude Code will handle Python checks, dependency install, autostart setup, and launch.

### Option 2: by hand

1. Clone or download this repo:
   ```
   git clone https://github.com/refreshthekid/whisper-flow.git
   cd whisper-flow
   ```
2. Double-click `install.bat`. It will:
   - Check you have Python on PATH
   - Install all Python dependencies via pip
   - Detect your `pythonw.exe` and write a launcher
   - Drop a shortcut in your Startup folder so it boots automatically on login
   - Launch Whisper Flow

First launch downloads the Whisper `medium` model (~750 MB) from Hugging Face. Subsequent launches are instant.

## Use

Hold **Right Alt**, speak, release. Your words get pasted into whatever text field is focused.

The microphone icon in your system tray means it's running. Right-click → **Quit Whisper Flow** to stop.

## Uninstall

Double-click `uninstall.bat`. This stops any running instance and removes the autostart shortcut. The source files stay; delete the folder manually if you want them gone.

## Configuration

Edit the constants near the top of [`whisper_flow.py`](whisper_flow.py):

| Setting | Default | Notes |
|---|---|---|
| `MODEL_SIZE` | `"medium"` | `tiny` / `base` / `small` / `medium` / `large-v3`. Bigger = more accurate but slower. |
| `HOTKEY` | `"right alt"` | Any single key name [supported by the keyboard library](https://github.com/boppreh/keyboard#api). |
| `LANGUAGE` | `"en"` | Set to `None` to auto-detect language. |
| `COMPUTE_TYPE` | `"int8"` | `int8` (fastest CPU), `float16` (GPU), `float32` (slowest, most accurate). |

After editing, restart via the tray icon or run `uninstall.bat` followed by `install.bat`.

## Troubleshooting

**"Whisper Flow is already running."**
The single-instance lock thinks another copy is alive. Run `uninstall.bat` to kill everything, then re-launch.

**Tray icon missing.**
Windows hides new icons. Click the `^` chevron near your clock and drag the mic icon onto the visible tray.

**Transcription is doubled or tripled.**
Multiple instances are running. `uninstall.bat` then `install.bat` fixes it.

**Microsoft Store Python doesn't work.**
This installer is built for Microsoft Store Python (the default if you got Python from the Windows Store). If you used the python.org installer instead, it'll still work — `install.bat` finds `pythonw.exe` next to `python.exe` automatically.

## How it works

1. `keyboard` library hooks Right Alt globally
2. `sounddevice` streams mic audio into a ring buffer while the key is held
3. On release, the buffer is handed to `faster-whisper` for transcription
4. Result is copied to clipboard and pasted via simulated `Ctrl+V`

That's the whole trick. See [`whisper_flow.py`](whisper_flow.py) — it's under 150 lines.

## License

MIT. Do whatever you want.
