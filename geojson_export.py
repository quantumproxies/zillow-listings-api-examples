"""Listings → GeoJSON, priced and colour-ready for a map layer.

    python3 geojson_export.py "Denver, CO" --max 300 --out denver.geojson
"""
from __future__ import annotations

import argparse
import json

from zillow import per_sqft, search


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("location")
    ap.add_argument("--status", default="for_sale", choices=["for_sale", "for_rent", "sold"])
    ap.add_argument("--max", type=int, default=200)
    ap.add_argument("--out", default="listings.geojson")
    args = ap.parse_args()

    rows = search(args.location, args.status, args.max)

    features = []
    for row in rows:
        lat, lon = row.get("latitude"), row.get("longitude")
        if lat is None or lon is None:
            continue
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "address": row.get("address"),
                "price": row.get("price_value"),
                "beds": row.get("beds"),
                "baths": row.get("baths"),
                "sqft": row.get("area_sqft"),
                "per_sqft": round(per_sqft(row) or 0) or None,
                "home_type": row.get("home_type"),
                "days_on_zillow": row.get("days_on_zillow"),
                "url": row.get("url"),
            },
        })

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": features}, fh, indent=1)

    print(f"{len(features)} of {len(rows)} listings had coordinates → {args.out}")


if __name__ == "__main__":
    main()
