from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel, Field, constr
from typing import Optional

E164 = constr(pattern=r"^\+?[1-9]\d{1,14}$")


class CreateCall(BaseModel):
    caller: E164
    receiver: E164
    started_at: datetime


class RecordingOut(BaseModel):
    id: uuid.UUID
    filename: str
    duration_sec: Optional[int] = None
    transcription: Optional[str] = None


class CallOut(BaseModel):
    id: uuid.UUID
    caller: str
    receiver: str
    started_at: datetime
    status: str
    recording: Optional[RecordingOut] = None

    created_at: datetime
    updated_at: datetime
