"""Median $/sqft per ZIP, sweeping one ZIP at a time for real coverage.

A city-wide search returns a map viewport. Searching each ZIP separately is how
you get comparable samples across a metro.

    python3 price_per_sqft.py zips.txt --per-zip 120
    # zips.txt: one ZIP or "78702, TX" per line
"""
from __future__ import annotations

import argparse
import pathlib
import statistics
from concurrent.futures import ThreadPoolExecutor

from zillow import per_sqft, search


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("file", type=pathlib.Path)
    ap.add_argument("--status", default="for_sale", choices=["for_sale", "for_rent", "sold"])
    ap.add_argument("--per-zip", type=int, default=100)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    zips = [ln.strip() for ln in args.file.read_text(encoding="utf-8").splitlines() if ln.strip()]

    def probe(zipcode: str):
        try:
            return zipcode, search(zipcode, args.status, args.per_zip), None
        except RuntimeError as exc:
            return zipcode, [], str(exc)

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for zipcode, rows, error in pool.map(probe, zips):
            if error:
                print(f"{zipcode:<12} !! {error}")
                continue
            values = [v for v in (per_sqft(r) for r in rows) if v]
            beds = [r["beds"] for r in rows if r.get("beds")]
            if len(values) < 3:
                print(f"{zipcode:<12} only {len(values)} usable rows")
                continue
            results.append((zipcode, len(rows), statistics.median(values),
                            statistics.median(beds) if beds else 0))

    print(f"\n{'zip':<12}{'listings':>10}{'$/sqft':>12}{'median beds':>13}")
    for zipcode, n, sqft_price, beds in sorted(results, key=lambda t: -t[2]):
        print(f"{zipcode:<12}{n:>10}{sqft_price:>12,.0f}{beds:>13.0f}")


if __name__ == "__main__":
    main()
