from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReplayRun(Base):
    __tablename__ = "replay_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    dataset_id: Mapped[str] = mapped_column(String(256), nullable=False)
    dataset_checksum: Mapped[str] = mapped_column(String(128), nullable=False)

    seed: Mapped[int] = mapped_column(Integer, nullable=False)
    speed: Mapped[str] = mapped_column(String(16), nullable=False)

    config_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    commit_sha: Mapped[str] = mapped_column(String(64), nullable=False)
    machine_profile: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default="queued")

    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[object | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[object | None] = mapped_column(DateTime(timezone=True), nullable=True)
