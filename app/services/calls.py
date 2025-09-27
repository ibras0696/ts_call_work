from __future__ import annotations
import uuid
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Call


FIELDS = (
    Call.id,
    Call.caller,
    Call.receiver,
    Call.started_at,
    Call.status,
    Call.created_at,
    Call.updated_at,
)


async def create_call(session: AsyncSession, *, caller: str, receiver: str, started_at) -> dict:
    call = Call(caller=caller, receiver=receiver, started_at=started_at)
    session.add(call)
    # Ensure PK is generated without triggering extra lazy loads
    await session.flush()
    # Build dict directly from instance (expire_on_commit=False prevents expiration)
    data = {
        "id": call.id,
        "caller": call.caller,
        "receiver": call.receiver,
        "started_at": call.started_at,
        "status": call.status,
        "created_at": call.created_at,
        "updated_at": call.updated_at,
    }
    await session.commit()
    return data


async def get_call(session: AsyncSession, call_id: uuid.UUID) -> dict | None:
    stmt = select(*FIELDS).where(Call.id == call_id)
    res = await session.execute(stmt)
    r = res.one_or_none()
    if r is None:
        return None
    return {
        "id": r.id,
        "caller": r.caller,
        "receiver": r.receiver,
        "started_at": r.started_at,
        "status": r.status,
        "created_at": r.created_at,
        "updated_at": r.updated_at,
    }


async def search_calls(session: AsyncSession, *, query: str, limit: int = 50, offset: int = 0) -> tuple[int, list[dict]]:
    q = f"%{query}%"
    where = or_(Call.caller.ilike(q), Call.receiver.ilike(q))
    total_stmt = select(func.count()).select_from(Call).where(where)
    total = (await session.execute(total_stmt)).scalar_one()

    stmt = select(*FIELDS).where(where).order_by(Call.created_at.desc()).limit(limit).offset(offset)
    res = await session.execute(stmt)
    rows = res.all()
    items = [
        {
            "id": r.id,
            "caller": r.caller,
            "receiver": r.receiver,
            "started_at": r.started_at,
            "status": r.status,
            "created_at": r.created_at,
            "updated_at": r.updated_at,
        }
        for r in rows
    ]
    return int(total), items
