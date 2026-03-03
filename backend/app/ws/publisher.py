import json
import redis

from app.core.config import settings

_CHANNEL = "zetapulse:updates"
_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


def publish_update(payload: dict) -> None:
    try:
        _client.publish(_CHANNEL, json.dumps(payload))
    except Exception:
        # Don't fail API paths if Redis is unavailable
        return
