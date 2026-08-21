"""Gross rental yield by ZIP — a screening filter, not a valuation.

Both inputs (price_value and rent_zestimate) come from a listing and a model.
The script prints the sample size per ZIP so a 12% yield built on two rows is
visibly a 12% yield built on two rows.

    python3 rent_yield.py "Austin, TX" --max 400 --min-rows 5
"""
from __future__ import annotations

import argparse
import statistics

from zillow import by_zip, gross_yield, search


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("location")
    ap.add_argument("--max", type=int, default=300)
    ap.add_argument("--min-rows", type=int, default=4)
    args = ap.parse_args()

    rows = search(args.location, "for_sale", args.max)
    usable = [r for r in rows if gross_yield(r)]
    print(f"{len(rows)} listings, {len(usable)} carry both a price and a rent estimate "
          f"({100 * len(usable) // max(len(rows), 1)}%)\n")

    print(f"{'zip':<8}{'rows':>6}{'median price':>15}{'median rent':>13}{'gross yield':>13}")
    ranked = []
    for zipcode, group in by_zip(usable).items():
        yields = [gross_yield(r) for r in group]
        if len(yields) < args.min_rows:
            continue
        prices = [r["price_value"] for r in group]
        rents = [r["rent_zestimate"] for r in group]
        ranked.append((zipcode, len(group), statistics.median(prices),
                       statistics.median(rents), statistics.median(yields)))

    for zipcode, n, price, rent, y in sorted(ranked, key=lambda t: -t[4]):
        print(f"{zipcode:<8}{n:>6}{price:>15,.0f}{rent:>13,.0f}{100 * y:>12.2f}%")

    if not ranked:
        print(f"(no ZIP reached {args.min_rows} usable rows — raise --max)")


if __name__ == "__main__":
    main()
