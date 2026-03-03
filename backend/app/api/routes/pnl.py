from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db
from app.models import PnLAttributionRow, ReplayRun
from app.schemas.pnl import PnLAttributionOut

router = APIRouter()


@router.get("/runs/{run_id}/attribution", response_model=List[PnLAttributionOut])
def pnl_attribution(run_id: int, db: Session = Depends(get_db)):
    run = db.execute(select(ReplayRun).where(ReplayRun.id == run_id)).scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="run not found")

    rows = (
        db.execute(
            select(PnLAttributionRow)
            .where(PnLAttributionRow.run_id == run_id)
            .order_by(PnLAttributionRow.window_start)
        )
        .scalars()
        .all()
    )
    return rows
