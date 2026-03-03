from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LatencySample(Base):
    __tablename__ = "latency_samples"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("replay_runs.id", ondelete="CASCADE"), nullable=False)
    stage: Mapped[str] = mapped_column(String(64), nullable=False)
    value_us: Mapped[int] = mapped_column(BigInteger, nullable=False)
    timestamp: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
