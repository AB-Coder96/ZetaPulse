#!/usr/bin/env python3
"""Example ingestion driver.

Generates a small stream of synthetic feed health metrics and POSTs them to the Zetapulse backend.

Replace with a real market-data connector (Coinbase, Kraken, FIX, etc) and keep the POST shape the same.
"""

import argparse
import random
import time
from datetime import datetime

import httpx

DEFAULT_API = "http://localhost:8000"


def generate_metrics(venue: str, symbols: list[str]):
    while True:
        for sym in symbols:
            yield {
                "venue": venue,
                "symbol": sym,
                "timestamp": datetime.utcnow().isoformat(),
                "msg_rate": max(0.0, random.gauss(1200, 200)),
                "reconnects": 0,
                "drops": max(0, int(random.gauss(0, 2))),
                "latency_ms": max(0.0, random.gauss(3.0, 0.8)),
                "jitter_ms": max(0.0, random.gauss(0.9, 0.4)),
                "last_seen_ts": datetime.utcnow().isoformat(),
                "meta": {"source": "services/ingest/run_feed.py"},
            }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", default=DEFAULT_API)
    ap.add_argument("--venue", required=True)
    ap.add_argument("--symbols", required=True, help="Comma-separated, e.g. BTC-USD,ETH-USD")
    ap.add_argument("--sleep", type=float, default=1.0)
    args = ap.parse_args()

    symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]

    with httpx.Client(base_url=args.api, timeout=5.0) as client:
        for metric in generate_metrics(args.venue, symbols):
            r = client.post("/api/v1/feed/metrics", json=metric)
            r.raise_for_status()
            print("sent", metric["venue"], metric["symbol"], metric["msg_rate"])
            time.sleep(args.sleep)


if __name__ == "__main__":
    main()
