from datetime import datetime
from app.schemas.common import ORMBase


class PnLAttributionOut(ORMBase):
    id: int
    run_id: int
    venue_id: int
    instrument_id: int | None
    window_start: datetime
    window_end: datetime
    spread_capture: float
    adverse_selection: float
    fees: float
    latency_slip: float
    pnl_total: float
