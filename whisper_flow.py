#!/usr/bin/env python3
"""
Whisper Flow - Local voice dictation tool
Hold Right Alt to record, release to transcribe and paste anywhere.
"""

import os
import sys
import time
import threading
import numpy as np
import sounddevice as sd
import pyperclip
import keyboard
from faster_whisper import WhisperModel

from PIL import Image, ImageDraw
import pystray

# Single-instance lock via exclusive file open. If another copy is running,
# bind will fail and we exit immediately so we never double-paste.
_LOCK_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".whisper_flow.lock")
try:
    _lock_fh = open(_LOCK_PATH, "w")
    if sys.platform == "win32":
        import msvcrt
        msvcrt.locking(_lock_fh.fileno(), msvcrt.LK_NBLCK, 1)
    _lock_fh.write(str(os.getpid()))
    _lock_fh.flush()
except (OSError, IOError):
    print("Whisper Flow is already running.")
    sys.exit(1)

# --- Config ---
MODEL_SIZE   = "medium"    # tiny | base | small | medium | large-v3
HOTKEY       = "right alt"
SAMPLE_RATE  = 16000
LANGUAGE     = "en"        # set to None to auto-detect
COMPUTE_TYPE = "int8"      # int8 = fastest on CPU with negligible accuracy loss
# --------------

print(f"Loading faster-whisper '{MODEL_SIZE}' model (first run downloads it)...")
model = WhisperModel(MODEL_SIZE, device="cpu", compute_type=COMPUTE_TYPE)
print(f"Ready. Hold [{HOTKEY.upper()}] to dictate into any app.\n")

is_recording = False
audio_buffer = []
buffer_lock  = threading.Lock()
_recording_state = {"active": False}  # for tray tooltip


def audio_callback(indata, frames, time_info, status):
    if is_recording:
        with buffer_lock:
            audio_buffer.append(indata.copy())


stream = sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="float32",
    callback=audio_callback,
)
stream.start()


def process_and_paste(frames):
    if not frames:
        return

    audio = np.concatenate(frames, axis=0).flatten()
    if len(audio) < SAMPLE_RATE * 0.5:
        return

    segments, _info = model.transcribe(
        audio,
        language=LANGUAGE,
        beam_size=5,
        vad_filter=True,   # skip silent stretches in your recording
    )
    text = "".join(seg.text for seg in segments).strip()
    if not text:
        return

    pyperclip.copy(text)
    time.sleep(0.1)
    keyboard.press_and_release("ctrl+v")


def on_key_event(e):
    global is_recording, audio_buffer

    if e.name != HOTKEY:
        return

    if e.event_type == keyboard.KEY_DOWN and not is_recording:
        is_recording = True
        _recording_state["active"] = True
        with buffer_lock:
            audio_buffer = []

    elif e.event_type == keyboard.KEY_UP and is_recording:
        is_recording = False
        _recording_state["active"] = False
        with buffer_lock:
            frames = list(audio_buffer)
        threading.Thread(
            target=process_and_paste, args=(frames,), daemon=True
        ).start()


keyboard.hook(on_key_event)


# --- System tray icon ---
def make_idle_icon():
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # mic body
    d.rounded_rectangle([24, 12, 40, 40], radius=8, fill=(230, 230, 230))
    # stand
    d.rectangle([30, 40, 34, 52], fill=(230, 230, 230))
    d.rectangle([20, 50, 44, 54], fill=(230, 230, 230))
    # mic curve
    d.arc([18, 24, 46, 48], start=0, end=180, fill=(230, 230, 230), width=3)
    return img


def on_quit(icon, item):
    icon.stop()
    os._exit(0)


tray = pystray.Icon(
    "whisper_flow",
    make_idle_icon(),
    "Whisper Flow — Hold Right Alt to dictate",
    menu=pystray.Menu(pystray.MenuItem("Quit Whisper Flow", on_quit)),
)

try:
    tray.run()
except KeyboardInterrupt:
    pass
finally:
    stream.stop()
    stream.close()
