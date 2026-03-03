from fastapi import APIRouter

from app.api.routes import feed, replay, latency, pnl

api_router = APIRouter()
api_router.include_router(feed.router, prefix="/feed", tags=["feed"])
api_router.include_router(replay.router, prefix="/replay", tags=["replay"])
api_router.include_router(latency.router, prefix="/latency", tags=["latency"])
api_router.include_router(pnl.router, prefix="/pnl", tags=["pnl"])
