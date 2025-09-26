from __future__ import annotations
import uuid
from pathlib import Path
from typing import BinaryIO
from ..core.config import settings

ALLOWED_EXT = {".mp3", ".wav"}


class StorageError(Exception):
    pass


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def build_filename(call_id: uuid.UUID, original_name: str) -> str:
    ext = Path(original_name).suffix.lower()
    if ext not in ALLOWED_EXT:
        raise StorageError("unsupported_extension")
    return f"{call_id}{ext}"


def save_file(call_id: uuid.UUID, original_name: str, fileobj: BinaryIO) -> Path:
    base = Path(str(settings.RECORDINGS_DIR))
    ensure_dir(base)
    final_name = build_filename(call_id, original_name)
    dst = base / final_name
    with open(dst, "wb") as f:
        while True:
            chunk = fileobj.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
    return dst
