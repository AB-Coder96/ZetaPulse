from datetime import datetime
from pydantic import BaseModel

from app.schemas.common import ORMBase


class LatencySampleIn(BaseModel):
    run_id: int
    stage: str
    value_us: int
    timestamp: datetime | None = None


class LatencySampleOut(ORMBase):
    id: int
    run_id: int
    stage: str
    value_us: int
    timestamp: datetime


class StageSummary(BaseModel):
    stage: str
    p50_us: float
    p95_us: float
    p99_us: float
    p999_us: float
    count: int
