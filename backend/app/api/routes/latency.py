from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.api.deps import get_db
from app.models import LatencySample
from app.schemas.latency import LatencySampleIn, LatencySampleOut, StageSummary
from app.ws.publisher import publish_update

router = APIRouter()


@router.post("/samples", response_model=LatencySampleOut)
def ingest_latency_sample(payload: LatencySampleIn, db: Session = Depends(get_db)):
    s = LatencySample(
        run_id=payload.run_id,
        stage=payload.stage,
        value_us=payload.value_us,
        timestamp=payload.timestamp or datetime.utcnow(),
    )
    db.add(s)
    db.commit()
    db.refresh(s)

    publish_update(
        {
            "type": "latency_sample",
            "run_id": payload.run_id,
            "stage": payload.stage,
            "value_us": payload.value_us,
            "timestamp": s.timestamp.isoformat(),
        }
    )

    return s


@router.get("/runs/{run_id}/summary", response_model=List[StageSummary])
def latency_summary(
    run_id: int,
    window_sec: int = Query(3600, ge=60, le=86400),
    db: Session = Depends(get_db),
):
    """Percentiles per stage for a run in the last window_sec."""
    since = datetime.utcnow() - timedelta(seconds=window_sec)

    sql = text(
        '''
        SELECT
          stage,
          COUNT(*)::int as count,
          percentile_cont(0.50) WITHIN GROUP (ORDER BY value_us)::double precision as p50_us,
          percentile_cont(0.95) WITHIN GROUP (ORDER BY value_us)::double precision as p95_us,
          percentile_cont(0.99) WITHIN GROUP (ORDER BY value_us)::double precision as p99_us,
          percentile_cont(0.999) WITHIN GROUP (ORDER BY value_us)::double precision as p999_us
        FROM latency_samples
        WHERE run_id = :run_id AND timestamp >= :since
        GROUP BY stage
        ORDER BY stage;
        '''
    )

    rows = db.execute(sql, {"run_id": run_id, "since": since}).mappings().all()
    return [StageSummary(**dict(r)) for r in rows]
