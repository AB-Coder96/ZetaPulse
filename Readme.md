# Zetapulse — Real-Time Trading Systems Dashboard

Zetapulse is a **control-room** web app for trading-systems development. It turns your pipelines into something you can observe, replay, benchmark, and debug—with production-style discipline (**metrics, repeatability, auditability**).

This repo is a **working scaffold**:
- Backend: **FastAPI + Uvicorn**, **SQLAlchemy + Alembic**, **TimescaleDB** (time-series), **Postgres** (metadata), **Redis**
- Workers: **Celery** (Redis broker/result)
- Live updates: **WebSockets** (Redis pubsub fanout)
- Frontend: **React (Vite) + Tailwind + Recharts**
- DevOps: **Docker Compose**, **GitHub Actions** CI

> The replay task is demo-implemented and generates synthetic latency/PnL/fill data. Swap the Celery task body with ZetaForge / your actual replay engine.

---

## Quickstart

```bash
cp .env.example .env
docker compose up -d --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- OpenAPI: http://localhost:8000/docs

### Demo flow
1. Open **Replay Runner** and start a run
2. Watch **Latency Dashboard** and **PnL Attribution** populate
3. Feed Health receives live WS updates (synthetic by default)

> Disable synthetic metrics by setting `ENABLE_DEMO_PUBLISHER=false` in `.env`.

---

## Key UI pages (portfolio “non-negotiables”)

- **Latency Breakdown + histogram** (Latency page)
- **Replay Runner (dataset + seed + run complete)** (Replay page)
- **p99 / p99.9 numbers** (Latency table)
- **Run metadata box** (Replay page: commit SHA + config hash + machine profile)

---

## Architecture (short)

### Database
- `Postgres/TimescaleDB` stores metadata + time-series tables.
- Hypertables: `feed_metrics` and `latency_samples` (created in the first Alembic migration).

### Live updates
- API endpoints / Celery tasks publish JSON to Redis channel `zetapulse:updates`.
- `/ws/updates` listens to Redis pubsub and forwards to all connected clients.

### Workers
- Celery processes replay runs and persists artifacts:
  - latency samples
  - fills
  - pnl attribution rows
  - and status transitions

---

## Useful commands

```bash
# Tail logs
docker compose logs -f --tail=200

# Run a synthetic ingest stream (optional)
python3 services/ingest/run_feed.py --venue coinbase --symbols BTC-USD,ETH-USD

# Start a replay run from CLI (computes real dataset sha256)
python3 services/replay/run_replay.py --dataset data/sample_day.jsonl --seed 42 --speed 10x --config '{"risk":"v1"}'
```

---

## API (high level)

- `POST /api/v1/feed/metrics` ingest a feed metric point
- `GET /api/v1/feed/health` latest metrics per stream

- `POST /api/v1/replay/runs` create a replay run (enqueues Celery task)
- `GET /api/v1/replay/runs/{id}` fetch run status + metadata

- `POST /api/v1/latency/samples` ingest latency sample points
- `GET /api/v1/latency/runs/{id}/summary` percentile summary per stage

- `GET /api/v1/pnl/runs/{id}/attribution` pnl decomposition rows

---

## Deployment options

### AWS ECS/Fargate (recommended)
Run 3 services:
- `backend` (FastAPI)
- `worker` (Celery)
- `frontend` (static build served by Nginx or S3/CloudFront)

You’ll typically place:
- Postgres/TimescaleDB in RDS or self-managed
- Redis in ElastiCache

### EC2 + Nginx
Use `deploy/nginx.conf` as a starting point to:
- Serve the frontend build (Vite build output)
- Reverse-proxy `/api` and `/ws` to `uvicorn`

---

## Notes / TODOs for a real trading stack

- Replace demo `replay_run_task` with your ZetaForge replay runner invocation
- Add authentication/SSO (Cognito, Auth0, etc.)
- Add Prometheus-style `/metrics` endpoint and optional OpenTelemetry
- Add run-to-run diff view (two configs, one dataset)
- Add feed gap anomaly detection rules

---

## License
MIT (see LICENSE)
