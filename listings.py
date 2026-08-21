"""One Zillow search → CSV, with the summary you would compute by hand anyway.

    python3 listings.py "Austin, TX" --status for_sale --max 300 --out austin.csv
"""
from __future__ import annotations

import argparse
import csv
import statistics
from collections import Counter

from zillow import median_of, per_sqft, search

FIELDS = ["rank", "zpid", "address", "city", "state", "zipcode", "price", "price_value",
          "beds", "baths", "area_sqft", "lot_size", "home_type", "status", "listing_type",
          "zestimate", "rent_zestimate", "days_on_zillow", "broker",
          "latitude", "longitude", "url"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("location")
    ap.add_argument("--status", default="for_sale", choices=["for_sale", "for_rent", "sold"])
    ap.add_argument("--max", type=int, default=100)
    ap.add_argument("--out", default="listings.csv")
    args = ap.parse_args()

    rows = search(args.location, args.status, args.max)

    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    prices = sorted(r["price_value"] for r in rows if r.get("price_value"))
    sqft = [v for v in (per_sqft(r) for r in rows) if v]
    dom = [r["days_on_zillow"] for r in rows if isinstance(r.get("days_on_zillow"), (int, float))]

    print(f"{len(rows)} {args.status.replace('_', ' ')} listings in {args.location} → {args.out}\n")
    if prices:
        q = statistics.quantiles(prices, n=4) if len(prices) >= 4 else [prices[0]] * 3
        print(f"price      p25 ${q[0]:,.0f}   median ${q[1]:,.0f}   p75 ${q[2]:,.0f}")
    if sqft:
        print(f"$/sqft     median ${median_of(sqft):,.0f}")
    if dom:
        print(f"days on    median {statistics.median(dom):.0f}")

    print("\nhome types")
    for kind, n in Counter(r.get("home_type") for r in rows).most_common(8):
        print(f"  {n:>4}  {kind}")

    over = [r for r in rows if r.get("zestimate") and r.get("price_value")
            and r["price_value"] > r["zestimate"] * 1.1]
    print(f"\n{len(over)} listings asking more than 110% of their Zestimate")
    for row in sorted(over, key=lambda r: -(r["price_value"] / r["zestimate"]))[:8]:
        ratio = row["price_value"] / row["zestimate"]
        print(f"  {ratio:.2f}x  {row.get('price')}  (Zestimate ${row['zestimate']:,})  "
              f"{row.get('address')}")


if __name__ == "__main__":
    main()
