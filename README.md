# Zillow listings API — for-sale, for-rent and sold rows with coordinates and Zestimates

The [`zillow_search` collector](https://quanticdata.io/collectors/zillow-scraper-api/) takes a
location and a status and returns listings as typed rows: `zpid`, split address (street, city,
state, zipcode), price as text **and** `price_value`, beds, baths, `area_sqft`, lot size, home
type, listing status, `zestimate`, `rent_zestimate`, `days_on_zillow`, broker, latitude,
longitude, image and URL.

$0.001 per listing, up to 500 per run.

```bash
pip install requests
export QUANTICDATA_API_KEY=qd_live_your_key_here

python3 listings.py "Austin, TX" --status for_sale --max 300 --out austin.csv
python3 rent_yield.py "Austin, TX" --max 300         # price vs rent_zestimate, by ZIP
python3 price_per_sqft.py zips.txt                   # median $/sqft across ZIPs
```

## Files

| File | What it does |
|---|---|
| [`zillow.py`](zillow.py) | client + row helpers (`per_sqft`, `gross_yield`, ZIP grouping) |
| [`listings.py`](listings.py) | one search → CSV + a readable summary |
| [`rent_yield.py`](rent_yield.py) | gross rental yield from `price_value` and `rent_zestimate`, by ZIP |
| [`price_per_sqft.py`](price_per_sqft.py) | median $/sqft per ZIP code, ranked |
| [`geojson_export.py`](geojson_export.py) | listings → GeoJSON for a map layer |

## Input

| Field | Notes |
|---|---|
| `location` | required — `"Austin, TX"`, a ZIP, a neighbourhood |
| `status` | `for_sale` (default), `for_rent`, `sold` |
| `max_results` | 1–500, default 40 |

## Output row

```jsonc
{ "rank": 1, "page": 1, "zpid": "29444922",
  "address": "1234 E 6th St, Austin, TX 78702",
  "street": "1234 E 6th St", "city": "Austin", "state": "TX", "zipcode": "78702",
  "price": "$725,000", "price_value": 725000, "currency": "USD",
  "beds": 3, "baths": 2, "area_sqft": 1680, "lot_size": 6098,
  "home_type": "SINGLE_FAMILY", "status": "FOR_SALE", "status_type": "FOR_SALE",
  "listing_type": "Agent", "zestimate": 731400, "rent_zestimate": 3200,
  "days_on_zillow": 12, "broker": "…",
  "latitude": 30.2635, "longitude": -97.7237,
  "image": "https://…", "url": "https://www.zillow.com/homedetails/…" }
```

## Reading this data without fooling yourself

- **A Zestimate is a model output, not a price.** Zillow publishes its own error bands. Use it
  as a relative signal (`price_value / zestimate` is the interesting ratio), never as a comp.
- **`rent_zestimate` is a model too.** Gross yield computed from two models is a screening
  filter, not an investment decision — `rent_yield.py` prints how many rows actually carried
  both numbers so you can see how thin the sample is.
- **Search results are a viewport, not an inventory.** A city search returns what the map shows.
  Sweep ZIP by ZIP (`price_per_sqft.py` does) when you want coverage.
- **`sold` status has a lag** and does not cover every off-market transaction.

## Related

- [Zillow scraper API](https://quanticdata.io/collectors/zillow-scraper-api/) · [All collectors](https://quanticdata.io/collectors/)
- [Real estate data scraping](https://quanticdata.io/real-estate-data-scraping/) · [Market research data](https://quanticdata.io/market-research-data/)
- [Is web scraping legal in the US?](https://quanticdata.io/blog/is-web-scraping-legal-in-us/)

MIT licensed.
