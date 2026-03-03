from __future__ import annotations

import random
import time
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.tasks.celery_app import celery_app
from app.db.session import SessionLocal
from app.models import ReplayRun, LatencySample, PnLAttributionRow, Venue, Instrument, Fill
from app.ws.publisher import publish_update


def enqueue_replay_run(run_id: int) -> None:
    replay_run_task.delay(run_id)


@celery_app.task(name="zetapulse.replay_run_task")
def replay_run_task(run_id: int) -> None:
    """Demo replay task. Replace with ZetaForge/your engine."""
    db: Session = SessionLocal()
    try:
        run = db.execute(select(ReplayRun).where(ReplayRun.id == run_id)).scalar_one_or_none()
        if not run:
            return

        run.status = "running"
        run.started_at = datetime.utcnow()
        db.commit()

        publish_update({"type": "replay_status", "run_id": run_id, "status": "running"})

        stages = ["ingest", "normalize", "book", "signal", "risk", "send"]
        start = datetime.utcnow() - timedelta(seconds=30)
        for i in range(500):
            ts = start + timedelta(milliseconds=i * 50)
            for st in stages:
                base = {"ingest": 40, "normalize": 20, "book": 60, "signal": 25, "risk": 30, "send": 15}[st]
                jitter = random.randint(0, 40)
                v = base * 10 + jitter * 10  # microseconds
                db.add(LatencySample(run_id=run_id, stage=st, value_us=v, timestamp=ts))
            if i % 50 == 0:
                db.commit()
                publish_update({"type": "replay_progress", "run_id": run_id, "progress": i / 500})
            time.sleep(0.01)

        venue = db.execute(select(Venue).where(Venue.name == "demo")).scalar_one_or_none()
        if not venue:
            venue = Venue(name="demo")
            db.add(venue)
            db.commit()
            db.refresh(venue)

        inst = (
            db.execute(select(Instrument).where(Instrument.venue_id == venue.id, Instrument.symbol == "DEMO-USD"))
            .scalar_one_or_none()
        )
        if not inst:
            inst = Instrument(venue_id=venue.id, symbol="DEMO-USD")
            db.add(inst)
            db.commit()
            db.refresh(inst)

        # demo fills
        for i in range(60):
            side = "buy" if i % 2 == 0 else "sell"
            price = 100 + random.random() * 2 - 1
            qty = 1 + random.random()
            slippage = random.random() * 2
            fees = 0.01 * qty
            latency = random.randint(100, 600)
            db.add(
                Fill(
                    run_id=run_id,
                    venue_id=venue.id,
                    instrument_id=inst.id,
                    side=side,
                    qty=qty,
                    price=price,
                    slippage_bps=slippage,
                    fees=fees,
                    latency_us=latency,
                    ts=datetime.utcnow() - timedelta(seconds=60 - i),
                    meta={"queue_pos_est": random.random()},
                )
            )
        db.commit()

        # demo pnl attribution (10 windows)
        t0 = datetime.utcnow() - timedelta(minutes=10)
        for j in range(10):
            ws = t0 + timedelta(minutes=j)
            we = ws + timedelta(minutes=1)
            spread = random.uniform(-2, 5)
            adverse = random.uniform(-6, 1)
            fees = random.uniform(-1, -0.1)
            lat = random.uniform(-2, 0.5)
            total = spread + adverse + fees + lat
            db.add(
                PnLAttributionRow(
                    run_id=run_id,
                    venue_id=venue.id,
                    instrument_id=inst.id,
                    window_start=ws,
                    window_end=we,
                    spread_capture=spread,
                    adverse_selection=adverse,
                    fees=fees,
                    latency_slip=lat,
                    pnl_total=total,
                )
            )
        db.commit()

        run.status = "complete"
        run.finished_at = datetime.utcnow()
        db.commit()

        publish_update({"type": "replay_status", "run_id": run_id, "status": "complete"})
    except Exception as e:
        try:
            run = db.execute(select(ReplayRun).where(ReplayRun.id == run_id)).scalar_one_or_none()
            if run:
                run.status = "failed"
                run.finished_at = datetime.utcnow()
                db.commit()
        except Exception:
            pass
        publish_update({"type": "replay_status", "run_id": run_id, "status": "failed", "error": str(e)})
        raise
    finally:
        db.close()
