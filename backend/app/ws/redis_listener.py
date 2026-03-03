from __future__ import annotations

import asyncio
import json
from typing import AsyncIterator

import redis.asyncio as aioredis

from app.core.config import settings

CHANNEL = "zetapulse:updates"


async def iter_updates() -> AsyncIterator[dict]:
    r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    pubsub = r.pubsub()
    await pubsub.subscribe(CHANNEL)
    try:
        async for msg in pubsub.listen():
            if msg is None:
                await asyncio.sleep(0.01)
                continue
            if msg.get("type") != "message":
                continue
            data = msg.get("data")
            if not data:
                continue
            try:
                yield json.loads(data)
            except Exception:
                continue
    finally:
        try:
            await pubsub.unsubscribe(CHANNEL)
        except Exception:
            pass
        await pubsub.close()
        await r.close()
