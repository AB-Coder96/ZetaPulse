# Backend

- FastAPI 

- Uvicorn (server)

- SQLAlchemy + Alembic (migrations)

- PostgreSQL (metadata)

- TimescaleDB (time-series metrics)

- Redis 

- Celery (workers) + Redis broker 

- WebSockets for live updates

# Frontend

- React + JavaScript

- CSS

- Charts: Plotly or Recharts

- WebSocket client for live panels

# DevOps

- Docker Compose

- GitHub Actions (lint/test/build)

# deploy: 
- AWS ECS/Fargate or EC2 + Nginx

# Zetapulse — Real-Time Trading Systems Dashboard

Zetapulse is a “control room” web application for trading-systems development. It turns your pipelines into something you can **observe, replay, benchmark, and debug**—with production-style discipline (metrics, repeatability, auditability).

It is designed to pair with projects like **ZetaForge** (replay/sim/execution) and **LatencyLab** (benchmarks), but it can also run standalone with public market feeds.

---

## What Zetapulse shows

### 1) Feed Health
- per-venue message rate (msgs/sec) and reconnect counts
- dropped message counters + gap detection
- feed latency & jitter indicators
- last-seen timestamps per symbol/stream

### 2) Replay Runner
- select dataset/day + speed (1x/10x/100x)
- run deterministic replay and persist run artifacts
- show fills, slippage, queue-position estimate (optional)
- “replay diff” view: compare two runs (config change, code change)

### 3) Latency Dashboard
- stage breakdown (ingest → normalize → book → signal → risk → send)
- histograms for p50/p95/p99/p99.9 per stage
- “last benchmark run” with commit SHA + machine profile

### 4) PnL Attribution (for sim/backtests)
- spread capture vs adverse selection vs fees vs latency slip
- PnL decomposition by venue/symbol/time window
- trade list + drill-down into individual fill traces

---

## Suggested Stack

**Frontend**
- React + Tailwind
- Plotly (or your chart lib)
- WebSockets/SSE for live updates

**Backend**
- Django REST *or* FastAPI (both are fine)
- async workers for ingestion & replay runs (Celery/RQ/Arq)
- metrics endpoints (Prometheus-style optional)

**Storage**
- PostgreSQL for metadata + configs
- TimescaleDB for time-series (ticks, metrics, run traces)
- Redis for hot cache (optional)

---

## Data Model (minimal, scalable)

- `Venue` / `Instrument`
- `FeedMetric` (rate, drops, jitter)
- `ReplayRun` (dataset, seed, config hash, commit SHA)
- `LatencySample` (stage, ns/us, timestamp, run id)
- `Fill` / `OrderEvent` / `PnLAttributionRow`

Key idea: **every run** is reproducible and stored with:
- dataset ID + checksum
- seed
- config hash
- commit SHA
- machine profile (CPU, kernel, governor)

---

## Quickstart (example)

### Local (docker-compose suggested)
```bash
docker compose up -d
# backend: http://localhost:8000
# frontend: http://localhost:5173
```

### Ingest a public feed (example)
```bash
python3 services/ingest/run_feed.py --venue coinbase --symbols BTC-USD,ETH-USD
```

### Start a replay run
```bash
python3 services/replay/run_replay.py --dataset data/sample_day.jsonl --seed 42 --speed 10x
```

---

## What to show on your portfolio site (non-negotiables)

Add these to the Zetapulse project page:

1) Screenshot: **Latency Breakdown + histogram**
2) Screenshot: **Replay Runner** (dataset + seed + “run complete”)
3) A small table of your **latest p99/p99.9** numbers (from ZetaForge/LatencyLab)
4) A “Run metadata” box showing **commit SHA + config hash**

This turns Zetapulse from “a dashboard” into proof of engineering rigor.

---

## Roadmap
- run-to-run diff view (two configs, one dataset)
- anomaly detection for feed gaps (simple rules → later ML)
- OpenTelemetry trace viewer integration
- nightly benchmark regression job + alerting

---
