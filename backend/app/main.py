from __future__ import annotations

import asyncio
import random
from datetime import datetime

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.api.router import api_router
from app.ws.redis_listener import iter_updates
from app.ws.publisher import publish_update
from app.db.session import engine

app = FastAPI(title=settings.APP_NAME)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.get("/meta")
def meta():
    return {
        "app": settings.APP_NAME,
        "env": settings.ENV,
        "commit_sha": settings.GIT_COMMIT_SHA,
        "now_utc": datetime.utcnow().isoformat(),
    }


@app.websocket("/ws/updates")
async def ws_updates(ws: WebSocket):
    await ws.accept()
    try:
        await ws.send_json({"type": "hello", "commit_sha": settings.GIT_COMMIT_SHA})
        async for payload in iter_updates():
            await ws.send_json(payload)
    except Exception:
        pass


async def demo_publisher_loop():
    venues = ["coinbase", "binance", "kraken"]
    symbols = ["BTC-USD", "ETH-USD", "SOL-USD"]
    while True:
        v = random.choice(venues)
        sym = random.choice(symbols)
        publish_update(
            {
                "type": "feed_metric",
                "venue": v,
                "symbol": sym,
                "timestamp": datetime.utcnow().isoformat(),
                "msg_rate": max(0.0, random.gauss(1500, 250)),
                "drops": max(0, int(random.gauss(1, 2))),
                "latency_ms": max(0.0, random.gauss(3.5, 1.0)),
                "jitter_ms": max(0.0, random.gauss(0.8, 0.4)),
            }
        )
        await asyncio.sleep(1.0)


@app.on_event("startup")
async def _startup():
    # sanity-check DB (non-fatal)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        pass

    if settings.ENABLE_DEMO_PUBLISHER:
        asyncio.create_task(demo_publisher_loop())
