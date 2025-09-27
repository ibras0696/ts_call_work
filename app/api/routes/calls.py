from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ...schemas.call import CreateCall, CallOut, CallsPage
from ...services.calls import create_call, get_call, search_calls
from ...services.storage import make_presigned_url, PresignNotConfigured
from ...services.recordings import get_recording_by_call_id
from ...api.deps import get_db

router = APIRouter(prefix="/calls", tags=["calls"])


@router.post("/", response_model=CallOut, status_code=status.HTTP_201_CREATED)
async def create_call_endpoint(payload: CreateCall, db: AsyncSession = Depends(get_db)) -> CallOut:
    data = await create_call(db, caller=payload.caller, receiver=payload.receiver, started_at=payload.started_at)
    return _to_call_out(data)


@router.get("/{call_id}", response_model=CallOut)
async def get_call_endpoint(call_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> CallOut:
    data = await get_call(db, call_id)
    if not data:
        raise HTTPException(status_code=404, detail="call_not_found")
    return _to_call_out(data)


@router.get("/", response_model=CallsPage)
async def search_calls_endpoint(
    query: str = Query(min_length=2),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> CallsPage:
    total, items = await search_calls(db, query=query, limit=limit, offset=offset)
    return CallsPage(total=total, items=[_to_call_out(it) for it in items])


@router.get("/{call_id}/download")
async def download_call_recording(call_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    data = await get_call(db, call_id)
    if not data:
        raise HTTPException(status_code=404, detail="call_not_found")
    rec = await get_recording_by_call_id(db, call_id=call_id)
    if not rec:
        raise HTTPException(status_code=404, detail="recording_not_found")
    try:
        url = make_presigned_url(rec.filename)
    except PresignNotConfigured:
        raise HTTPException(status_code=501, detail="presign_not_configured")
    return {"url": url}


# mappers

def _to_call_out(data: dict) -> CallOut:
    status = data.get("status")
    status_str = status.value if hasattr(status, "value") else str(status)
    return CallOut(
        id=data.get("id"),
        caller=data.get("caller"),
        receiver=data.get("receiver"),
        started_at=data.get("started_at"),
        status=status_str,
        recording=None,
        created_at=data.get("created_at"),
        updated_at=data.get("updated_at"),
    )
