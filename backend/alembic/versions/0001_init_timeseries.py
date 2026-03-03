"""init schema + timescale hypertables

Revision ID: 0001_init
Revises: 
Create Date: 2026-02-23

"""

from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "venues",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=64), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "instruments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("venue_id", sa.Integer(), sa.ForeignKey("venues.id", ondelete="CASCADE"), nullable=False),
        sa.Column("symbol", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("venue_id", "symbol", name="uq_instruments_venue_symbol"),
    )

    op.create_table(
        "replay_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("dataset_id", sa.String(length=256), nullable=False),
        sa.Column("dataset_checksum", sa.String(length=128), nullable=False),
        sa.Column("seed", sa.Integer(), nullable=False),
        sa.Column("speed", sa.String(length=16), nullable=False),
        sa.Column("config_hash", sa.String(length=128), nullable=False),
        sa.Column("commit_sha", sa.String(length=64), nullable=False),
        sa.Column("machine_profile", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="queued"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "feed_metrics",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("venue_id", sa.Integer(), sa.ForeignKey("venues.id", ondelete="CASCADE"), nullable=False),
        sa.Column("instrument_id", sa.Integer(), sa.ForeignKey("instruments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("msg_rate", sa.Float(), nullable=False),
        sa.Column("reconnects", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("drops", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("latency_ms", sa.Float(), nullable=True),
        sa.Column("jitter_ms", sa.Float(), nullable=True),
        sa.Column("last_seen_ts", sa.DateTime(timezone=True), nullable=True),
        sa.Column("meta", sa.JSON(), nullable=True),
    )
    op.create_index("ix_feed_metrics_ts", "feed_metrics", ["timestamp"])
    op.create_index("ix_feed_metrics_venue_ts", "feed_metrics", ["venue_id", "timestamp"])

    op.create_table(
        "latency_samples",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("replay_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("stage", sa.String(length=64), nullable=False),
        sa.Column("value_us", sa.BigInteger(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_latency_samples_run_stage_ts", "latency_samples", ["run_id", "stage", "timestamp"])

    op.create_table(
        "fills",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("replay_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("venue_id", sa.Integer(), sa.ForeignKey("venues.id", ondelete="CASCADE"), nullable=False),
        sa.Column("instrument_id", sa.Integer(), sa.ForeignKey("instruments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("side", sa.String(length=8), nullable=False),
        sa.Column("qty", sa.Float(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("slippage_bps", sa.Float(), nullable=True),
        sa.Column("fees", sa.Float(), nullable=True),
        sa.Column("latency_us", sa.BigInteger(), nullable=True),
        sa.Column("meta", sa.JSON(), nullable=True),
    )
    op.create_index("ix_fills_run_ts", "fills", ["run_id", "ts"])

    op.create_table(
        "pnl_attribution",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("replay_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("venue_id", sa.Integer(), sa.ForeignKey("venues.id", ondelete="CASCADE"), nullable=False),
        sa.Column("instrument_id", sa.Integer(), sa.ForeignKey("instruments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("spread_capture", sa.Float(), nullable=False, server_default="0"),
        sa.Column("adverse_selection", sa.Float(), nullable=False, server_default="0"),
        sa.Column("fees", sa.Float(), nullable=False, server_default="0"),
        sa.Column("latency_slip", sa.Float(), nullable=False, server_default="0"),
        sa.Column("pnl_total", sa.Float(), nullable=False, server_default="0"),
    )
    op.create_index("ix_pnl_run_window", "pnl_attribution", ["run_id", "window_start"])

    # Timescale hypertables (if extension is enabled)
    op.execute("SELECT create_hypertable('feed_metrics','timestamp', if_not_exists => TRUE);")
    op.execute("SELECT create_hypertable('latency_samples','timestamp', if_not_exists => TRUE);")


def downgrade() -> None:
    op.drop_table("pnl_attribution")
    op.drop_table("fills")
    op.drop_table("latency_samples")
    op.drop_table("feed_metrics")
    op.drop_table("replay_runs")
    op.drop_table("instruments")
    op.drop_table("venues")
