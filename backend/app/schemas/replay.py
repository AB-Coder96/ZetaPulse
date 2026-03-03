from datetime import datetime
from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class ReplayRunCreate(BaseModel):
    dataset_id: str = Field(..., description="Dataset path/id, e.g. data/sample_day.jsonl")
    dataset_checksum: str = Field(..., description="Checksum for reproducibility")
    seed: int = 42
    speed: str = "1x"
    config_hash: str = Field(..., description="Hash of run config")


class ReplayRunOut(ORMBase):
    id: int
    dataset_id: str
    dataset_checksum: str
    seed: int
    speed: str
    config_hash: str
    commit_sha: str
    machine_profile: str
    status: str
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
