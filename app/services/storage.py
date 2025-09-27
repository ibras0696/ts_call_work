from __future__ import annotations
import uuid
from pathlib import Path
from typing import BinaryIO
from ..core.config import settings
try:
    import boto3  # type: ignore
    from botocore.client import Config  # type: ignore
except Exception:  # optional dependency
    boto3 = None
    Config = None

ALLOWED_EXT = {".mp3", ".wav"}


class StorageError(Exception):
    pass


class PresignNotConfigured(Exception):
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


def _s3_client():
    if not getattr(settings, "S3_ENABLED", False):
        raise PresignNotConfigured
    if boto3 is None or Config is None:
        raise PresignNotConfigured
    session = boto3.session.Session()
    return session.client(
        "s3",
        endpoint_url=getattr(settings, "S3_ENDPOINT_URL", None),
        aws_access_key_id=getattr(settings, "S3_ACCESS_KEY", None),
        aws_secret_access_key=getattr(settings, "S3_SECRET_KEY", None),
        region_name=getattr(settings, "S3_REGION", None) or "us-east-1",
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}, retries={"max_attempts": 2}),
        use_ssl=bool(getattr(settings, "S3_SECURE", False)),
    )


def make_presigned_url(object_name: str, expires_in: int = 3600) -> str:
    s3 = _s3_client()
    bucket = getattr(settings, "S3_BUCKET", None)
    if not bucket:
        raise PresignNotConfigured
    return s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": bucket, "Key": object_name},
        ExpiresIn=expires_in,
    )
