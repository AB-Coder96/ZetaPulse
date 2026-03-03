from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.api.deps import get_db
from app.models import Venue, Instrument, FeedMetric
from app.schemas.feed import FeedMetricIn, FeedMetricOut, FeedHealthSummary
from app.ws.publisher import publish_update

router = APIRouter()


def get_or_create_venue(db: Session, name: str) -> Venue:
    v = db.execute(select(Venue).where(Venue.name == name)).scalar_one_or_none()
    if v:
        return v
    v = Venue(name=name)
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


def get_or_create_instrument(db: Session, venue_id: int, symbol: str) -> Instrument:
    inst = (
        db.execute(select(Instrument).where(Instrument.venue_id == venue_id, Instrument.symbol == symbol))
        .scalar_one_or_none()
    )
    if inst:
        return inst
    inst = Instrument(venue_id=venue_id, symbol=symbol)
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst


@router.post("/metrics", response_model=FeedMetricOut)
def ingest_metric(payload: FeedMetricIn, db: Session = Depends(get_db)):
    venue = get_or_create_venue(db, payload.venue)
    instrument_id = None
    symbol = None
    if payload.symbol:
        symbol = payload.symbol
        inst = get_or_create_instrument(db, venue.id, payload.symbol)
        instrument_id = inst.id

    m = FeedMetric(
        venue_id=venue.id,
        instrument_id=instrument_id,
        timestamp=payload.timestamp or datetime.utcnow(),
        msg_rate=payload.msg_rate,
        reconnects=payload.reconnects,
        drops=payload.drops,
        latency_ms=payload.latency_ms,
        jitter_ms=payload.jitter_ms,
        last_seen_ts=payload.last_seen_ts,
        meta=payload.meta,
    )
    db.add(m)
    db.commit()
    db.refresh(m)

    # Publish a lightweight update to live panels
    publish_update(
        {
            "type": "feed_metric",
            "venue": payload.venue,
            "symbol": symbol,
            "timestamp": m.timestamp.isoformat(),
            "msg_rate": m.msg_rate,
            "drops": m.drops,
            "latency_ms": m.latency_ms,
            "jitter_ms": m.jitter_ms,
        }
    )

    return m


@router.get("/health", response_model=List[FeedHealthSummary])
def feed_health(
    window_sec: int = Query(60, ge=5, le=3600),
    db: Session = Depends(get_db),
):
    """Returns latest point per (venue, symbol) in the time window."""
    since = datetime.utcnow() - timedelta(seconds=window_sec)

    venues = db.execute(select(Venue)).scalars().all()
    out: list[FeedHealthSummary] = []
    for v in venues:
        # Latest per venue-level (symbol=null)
        latest = (
            db.execute(
                select(FeedMetric)
                .where(FeedMetric.venue_id == v.id, FeedMetric.timestamp >= since)
                .order_by(desc(FeedMetric.timestamp))
            )
            .scalars()
            .first()
        )
        if latest:
            out.append(
                FeedHealthSummary(
                    venue=v.name,
                    symbol=None,
                    last_msg_rate=latest.msg_rate,
                    last_drops=latest.drops,
                    last_latency_ms=latest.latency_ms,
                    last_jitter_ms=latest.jitter_ms,
                    last_seen_ts=latest.last_seen_ts,
                    timestamp=latest.timestamp,
                )
            )

        instruments = db.execute(select(Instrument).where(Instrument.venue_id == v.id)).scalars().all()
        for inst in instruments:
            latest_i = (
                db.execute(
                    select(FeedMetric)
                    .where(
                        FeedMetric.venue_id == v.id,
                        FeedMetric.instrument_id == inst.id,
                        FeedMetric.timestamp >= since,
                    )
                    .order_by(desc(FeedMetric.timestamp))
                )
                .scalars()
                .first()
            )
            if latest_i:
                out.append(
                    FeedHealthSummary(
                        venue=v.name,
                        symbol=inst.symbol,
                        last_msg_rate=latest_i.msg_rate,
                        last_drops=latest_i.drops,
                        last_latency_ms=latest_i.latency_ms,
                        last_jitter_ms=latest_i.jitter_ms,
                        last_seen_ts=latest_i.last_seen_ts,
                        timestamp=latest_i.timestamp,
                    )
                )

    return out
