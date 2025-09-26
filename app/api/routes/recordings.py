from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ...api.deps import get_db
from ...services.storage import save_file, StorageError
from ...services.recordings import create_recording, RecordingAlreadyExists
from ...core.celery_app import celery_app

router = APIRouter(prefix="/calls", tags=["recordings"])


@router.post("/{call_id}/recording", status_code=status.HTTP_202_ACCEPTED)
async def upload_recording(call_id: uuid.UUID, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    # 1) Save file into volume
    try:
        dst = save_file(call_id, file.filename, file.file)
    except StorageError:
        raise HTTPException(status_code=422, detail="unsupported_extension")

    # 2) Create DB row and set call status to processing
    try:
        rec = await create_recording(db, call_id=call_id, filename=dst.name)
    except RecordingAlreadyExists:
        raise HTTPException(status_code=409, detail="recording_already_exists")

    # 3) Dispatch celery task
    celery_app.send_task("tasks.process_recording", args=[str(call_id), str(dst)])

    return {"recording_id": str(rec.id), "filename": rec.filename}
