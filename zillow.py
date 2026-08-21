"""Client and row helpers for the Zillow collector."""
from __future__ import annotations

import os
import statistics
import time
from collections import defaultdict
from typing import Any

import requests

BASE = "https://api.quanticdata.io/v1"
_s = requests.Session()


def _h() -> dict[str, str]:
    key = os.environ.get("QUANTICDATA_API_KEY")
    if not key:
        raise SystemExit("set QUANTICDATA_API_KEY — https://app.quanticdata.io/register")
    return {"Authorization": f"Bearer {key}"}


def search(location: str, status: str = "for_sale", max_results: int = 40) -> list[dict]:
    r = _s.post(f"{BASE}/scraper/collectors/zillow_search/run",
                json={"location": location, "status": status, "max_results": max_results},
                headers=_h(), timeout=300)
    body = r.json()
    if body.get("type") == "error" or not r.ok:
        raise RuntimeError(f"zillow_search ({r.status_code}): {body.get('message')}")

    run = body.get("payload", {})
    while run.get("status") in ("queued", "running"):
        time.sleep(3)
        run = _s.get(f"{BASE}/scraper/collectors/runs/{run['run_id']}",
                     headers=_h(), timeout=60).json().get("payload", {})
    return run.get("results") or []


def per_sqft(row: dict) -> float | None:
    price, area = row.get("price_value"), row.get("area_sqft")
    if not price or not area or area < 100:
        return None
    return price / area


def gross_yield(row: dict) -> float | None:
    """Annual rent / price. Both sides are Zillow estimates — treat as a screen."""
    price, rent = row.get("price_value"), row.get("rent_zestimate")
    if not price or not rent:
        return None
    return (rent * 12) / price


def by_zip(rows: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        zipcode = row.get("zipcode")
        if zipcode:
            grouped[str(zipcode)].append(row)
    return grouped


def median_of(values: list[float], minimum: int = 3) -> float | None:
    clean = [v for v in values if v]
    return statistics.median(clean) if len(clean) >= minimum else None
