from __future__ import annotations
import uuid
from pathlib import Path
from celery import shared_task
from .services.audio import duration_seconds, fake_transcript_first_20s, fake_silence_marks
from .services.recordings import mark_ready


@shared_task(name="tasks.process_recording")
def process_recording(call_id: str, path_str: str) -> None:
    path = Path(path_str)
    dur = duration_seconds(path)
    transcript = fake_transcript_first_20s(path)
    silence = fake_silence_marks(path)

    import asyncio

    async def _save():
        # Import SessionLocal inside the task to ensure engine/session
        # are created in the worker process (after fork), not in parent.
        from .core.db import SessionLocal
        async with SessionLocal() as session:
            await mark_ready(
                session,
                call_id=uuid.UUID(call_id),
                duration=dur,
                transcript=transcript,
                silence=silence,
            )

    asyncio.run(_save())
