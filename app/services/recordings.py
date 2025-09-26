from __future__ import annotations
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Call, Recording, CallStatus


class RecordingAlreadyExists(Exception):
    pass


async def create_recording(session: AsyncSession, *, call_id: uuid.UUID, filename: str) -> Recording:
    existing = await session.execute(select(Recording).where(Recording.call_id == call_id))
    if existing.scalar_one_or_none():
        raise RecordingAlreadyExists

    rec = Recording(call_id=call_id, filename=filename)
    session.add(rec)

    call = await session.get(Call, call_id)
    if call:
        call.status = CallStatus.processing

    await session.commit()
    await session.refresh(rec)
    return rec


async def mark_ready(
    session: AsyncSession,
    *,
    call_id: uuid.UUID,
    duration: int,
    transcript: str,
    silence: list | None,
) -> None:
    res = await session.execute(select(Recording).where(Recording.call_id == call_id))
    rec = res.scalar_one_or_none()
    if not rec:
        return
    rec.duration_sec = duration
    rec.transcription = transcript
    if hasattr(Recording, "silence_marks") and silence is not None:
        setattr(rec, "silence_marks", silence)  # type: ignore[attr-defined]

    call = await session.get(Call, call_id)
    if call:
        call.status = CallStatus.ready

    await session.commit()
