from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PnLAttributionRow(Base):
    __tablename__ = "pnl_attribution"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("replay_runs.id", ondelete="CASCADE"), nullable=False)
    venue_id: Mapped[int] = mapped_column(ForeignKey("venues.id", ondelete="CASCADE"), nullable=False)
    instrument_id: Mapped[int | None] = mapped_column(
        ForeignKey("instruments.id", ondelete="SET NULL"), nullable=True
    )

    window_start: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    window_end: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)

    spread_capture: Mapped[float] = mapped_column(Float, server_default="0", nullable=False)
    adverse_selection: Mapped[float] = mapped_column(Float, server_default="0", nullable=False)
    fees: Mapped[float] = mapped_column(Float, server_default="0", nullable=False)
    latency_slip: Mapped[float] = mapped_column(Float, server_default="0", nullable=False)
    pnl_total: Mapped[float] = mapped_column(Float, server_default="0", nullable=False)

    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now())
