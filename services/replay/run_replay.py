#!/usr/bin/env python3
"""Start a replay run via the API.

In a real setup this script would:
- compute dataset checksum (sha256)
- build a config hash from run parameters

For now it uses placeholders and relies on the Celery demo task to generate artifacts.
"""

import argparse
import hashlib
import json
import time

import httpx

DEFAULT_API = "http://localhost:8000"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", default=DEFAULT_API)
    ap.add_argument("--dataset", required=True, help="Path to dataset file")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--speed", default="10x")
    ap.add_argument("--config", default="{}", help="JSON string for run config")
    args = ap.parse_args()

    dataset_checksum = sha256_file(args.dataset)
    config_hash = hashlib.sha256(args.config.encode("utf-8")).hexdigest()

    payload = {
        "dataset_id": args.dataset,
        "dataset_checksum": dataset_checksum,
        "seed": args.seed,
        "speed": args.speed,
        "config_hash": config_hash,
    }

    with httpx.Client(base_url=args.api, timeout=10.0) as client:
        r = client.post("/api/v1/replay/runs", json=payload)
        r.raise_for_status()
        run = r.json()
        print("created run", run["id"], "status:", run["status"])

        while True:
            rr = client.get(f"/api/v1/replay/runs/{run['id']}")
            rr.raise_for_status()
            run = rr.json()
            print("status:", run["status"])
            if run["status"] in ("complete", "failed"):
                break
            time.sleep(2)

    print("final run:")
    print(json.dumps(run, indent=2))


if __name__ == "__main__":
    main()
