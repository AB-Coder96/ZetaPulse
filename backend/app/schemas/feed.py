from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class VenueOut(ORMBase):
    id: int
    name: str


class InstrumentOut(ORMBase):
    id: int
    venue_id: int
    symbol: str


class FeedMetricIn(BaseModel):
    venue: str = Field(..., description="Venue name, e.g. coinbase")
    symbol: str | None = Field(default=None, description="Optional symbol, e.g. BTC-USD")
    timestamp: datetime | None = None
    msg_rate: float
    reconnects: int = 0
    drops: int = 0
    latency_ms: float | None = None
    jitter_ms: float | None = None
    last_seen_ts: datetime | None = None
    meta: dict | None = None


class FeedMetricOut(ORMBase):
    id: int
    venue_id: int
    instrument_id: int | None
    timestamp: datetime
    msg_rate: float
    reconnects: int
    drops: int
    latency_ms: float | None
    jitter_ms: float | None
    last_seen_ts: datetime | None
    meta: dict | None


class FeedHealthSummary(BaseModel):
    venue: str
    symbol: str | None
    last_msg_rate: float
    last_drops: int
    last_latency_ms: float | None
    last_jitter_ms: float | None
    last_seen_ts: datetime | None
    timestamp: datetime
