from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FeedMetric(Base):
    __tablename__ = "feed_metrics"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    venue_id: Mapped[int] = mapped_column(ForeignKey("venues.id", ondelete="CASCADE"), nullable=False)
    instrument_id: Mapped[int | None] = mapped_column(
        ForeignKey("instruments.id", ondelete="SET NULL"), nullable=True
    )

    timestamp: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    msg_rate: Mapped[float] = mapped_column(Float, nullable=False)
    reconnects: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    drops: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    jitter_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_seen_ts: Mapped[object | None] = mapped_column(DateTime(timezone=True), nullable=True)

    meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
