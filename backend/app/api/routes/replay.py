from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db
from app.schemas.replay import ReplayRunCreate, ReplayRunOut
from app.models import ReplayRun
from app.util.machine import get_machine_profile_json
from app.core.config import settings
from app.tasks.replay import enqueue_replay_run

router = APIRouter()


@router.post("/runs", response_model=ReplayRunOut)
def create_replay_run(payload: ReplayRunCreate, db: Session = Depends(get_db)):
    run = ReplayRun(
        dataset_id=payload.dataset_id,
        dataset_checksum=payload.dataset_checksum,
        seed=payload.seed,
        speed=payload.speed,
        config_hash=payload.config_hash,
        commit_sha=settings.GIT_COMMIT_SHA,
        machine_profile=get_machine_profile_json(),
        status="queued",
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    enqueue_replay_run(run.id)
    return run


@router.get("/runs/{run_id}", response_model=ReplayRunOut)
def get_replay_run(run_id: int, db: Session = Depends(get_db)):
    run = db.execute(select(ReplayRun).where(ReplayRun.id == run_id)).scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="run not found")
    return run
