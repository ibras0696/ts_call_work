from __future__ import annotations
from pathlib import Path
from typing import List, Dict
from pydub import AudioSegment


def duration_seconds(path: Path) -> int:
    audio = AudioSegment.from_file(path)
    return int(audio.duration_seconds)


def fake_transcript_first_20s(path: Path) -> str:
    audio = AudioSegment.from_file(path)
    sample_ms = min(len(audio), 20_000)
    _ = audio[:sample_ms]
    return f"Detected speech fragment: {sample_ms}ms sample"


def fake_silence_marks(path: Path, window_sec: int = 5) -> List[Dict[str, int]]:
    total = duration_seconds(path)
    marks: List[Dict[str, int]] = []
    t = window_sec
    while t < total:
        marks.append({"start": t, "end": min(t + 1, total)})
        t += window_sec * 2
    return marks
