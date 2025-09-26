import io
import os
import sys
import time
import math
import struct
import json
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    print("[ERROR] 'requests' not installed. Install with: pip install requests", file=sys.stderr)
    sys.exit(2)

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")


def gen_tone_wav_bytes(duration_sec: float = 1.0, freq: float = 440.0, rate: int = 8000) -> io.BytesIO:
    """Generate a simple 16-bit mono WAV tone using stdlib only."""
    n_samples = int(duration_sec * rate)
    max_amp = 32767
    buf = io.BytesIO()

    # Write WAV with wave module via manual header using struct (to avoid extra imports)
    # But simpler: use wave module. However, wave only accepts file-like objects that support seek, which BytesIO does.
    import wave

    with wave.open(buf, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)  # 16-bit
        w.setframerate(rate)
        frames = bytearray()
        for i in range(n_samples):
            sample = int(max_amp * math.sin(2 * math.pi * freq * (i / rate)))
            frames += struct.pack('<h', sample)
        w.writeframes(frames)

    buf.seek(0)
    return buf


def main() -> int:
    print(f"[INFO] Using BASE_URL={BASE_URL}")

    # 1) Create call
    payload = {
        "caller": "+79001234567",
        "receiver": "+79007654321",
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    r = requests.post(f"{BASE_URL}/calls/", json=payload)
    print("POST /calls/:", r.status_code, r.text)
    r.raise_for_status()
    call = r.json()
    call_id = call["id"]

    # 2) Upload a tiny WAV
    wav = gen_tone_wav_bytes()
    files = {"file": ("tone.wav", wav, "audio/wav")}
    up = requests.post(f"{BASE_URL}/calls/{call_id}/recording", files=files)
    print(f"POST /calls/{{id}}/recording:", up.status_code, up.text)
    if up.status_code not in (202, 409):
        up.raise_for_status()

    # 3) Poll until ready
    deadline = time.time() + 20
    last = None
    while time.time() < deadline:
        g = requests.get(f"{BASE_URL}/calls/{call_id}")
        last = g
        try:
            data = g.json()
        except json.JSONDecodeError:
            print("GET invalid JSON:", g.status_code, g.text)
            time.sleep(1)
            continue
        print("GET /calls/{id}:", g.status_code, data.get("status"))
        if data.get("status") == "ready":
            print("[OK] Status is ready")
            return 0
        time.sleep(1)

    if last is not None:
        print("[WARN] Final state:", last.status_code, last.text)
    print("[FAIL] Timed out waiting for ready")
    return 1


if __name__ == "__main__":
    sys.exit(main())
