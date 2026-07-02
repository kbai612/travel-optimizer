# Findings

Generated from the current `warehouse.duckdb` with real data from all four sources,
though coverage varies by destination and signal:

- **Weather** (Open-Meteo) and **holidays** (Nager.Date) — real for all 8 destinations
  (Bangkok's holiday score is neutral by design; see caveats).
- **Demand** (OpenSky) — real for Lisbon, Cape Town, Tokyo, New York. The other 4
  (Bangkok, Rio, Reykjavik, Sydney) hit OpenSky's free-tier daily quota during
  extraction and stay neutral (50) until a future run picks them up.
- **Price** (Travelpayouts) — real, partial-month coverage for 7 of 8 destinations.
  New York is permanently neutral here: it's configured as `HOME_AIRPORT_IATA`, so
  there's no "JFK to JFK" fare to search for.

## Best months, by destination

| Destination | Top month | Score | Why |
|---|---|---|---|
| Bangkok (BKK) | November | 82.6 | Comfort (85.9) and a real cheap fare (price 100) converge; demand still neutral |
| Rio de Janeiro (GIG) | August | 86.1 | Dry-season comfort peak (95.9) plus a real cheap fare (price 100) |
| Tokyo (HND) | June | 81.9 | Comfort + a real, notably good fare (92.7); demand near-neutral |
| Cape Town (CPT) | October | 81.3 | Comfort (88.3) and a real cheap fare (96.6) beat January's better demand score but missing price data |
| Lisbon (LIS) | July (tied with Sep) | 79.9 | Comfort (94.3) and a real cheap fare (97.2); demand neutral for July specifically (that sample window was corrupted and dropped — see caveats) |
| Sydney (SYD) | August | 75.3 | A real cheap fare (100) outweighs February's better comfort score |
| Reykjavik (KEF) | July | 77.5 | Matches common travel wisdom, now reinforced by a real cheap fare (100) |
| New York (JFK) | August | 73.0 | Comfort peak (91.3); demand and price both neutral (JFK is the configured home airport, so it never gets price data) |

## What already looks right

- **Adding price data moved several answers, not just numbers.** Cape Town's top
  month moved from January to **October** once real fares came in — October's
  fare data (96.6) beat January's better demand score but missing price coverage.
  Bangkok moved from January to **November** the same way. This is the four-signal
  model working as intended: a single strong signal doesn't dominate a weak one
  just by being first.
- **Reykjavik keeps matching common knowledge**: July is Iceland's clear best
  month on comfort alone, and now a genuinely cheap real fare reinforces the same
  answer rather than contradicting it.
- **Hemisphere inversion still holds**: Lisbon/New York/Tokyo (Northern Hemisphere)
  peak in local summer; Rio/Cape Town/Sydney (Southern Hemisphere) peak in their
  own summer/shoulder months.

## Caveats worth flagging

- **OpenSky's free-tier daily quota is tight** — real cost of running this at
  full scale. A single extraction attempt across 8 destinations exhausted the
  daily allowance partway through, even with 1-request-per-second pacing added
  afterward. Getting live demand data for all 8 destinations in one day isn't
  realistic on the free tier; spreading destinations across the daily cron run
  (or running `--source opensky` on a handful per day) is the practical path.
- **Lisbon's July demand score is neutral, not just "no data yet."** The first
  OpenSky extraction attempt got rate-limited mid-request and briefly wrote a
  corrupted zero-flight file for that window; it was caught and deleted rather
  than left in as a false "zero traffic" data point, so July now correctly reads
  as "unknown" (neutral) rather than "empty." A future extraction run will
  backfill it with real data.
- **New York will never get a price score under the current config**, because
  `HOME_AIRPORT_IATA=JFK` and Travelpayouts rejects an identical origin/destination
  pair. Changing `HOME_AIRPORT_IATA` to a different home airport (or adding a
  second configured origin) would fix this — worth deciding based on where you'd
  actually be flying from.
- **Travelpayouts prices are cached/historical fares** (a fare that was actually
  found in a past search), not live quotes, and month coverage is uneven — Lisbon
  got 5 of 12 months, Tokyo got 11, some destinations far fewer. Real, but sparse.
- **Bangkok's holiday score is neutral, not zero-pressure**: Nager.Date doesn't
  cover Thailand, so `holiday_pressure_score` defaults to the same neutral value
  every month rather than reflecting real Thai public holidays (e.g. Songkran in
  April). Source-coverage gap, not a modeling choice.
- **Tokyo's June result** is a formula artifact worth knowing about: June sits in
  Japan's rainy season, but the comfort formula weights mean temperature (50%)
  well above precipitation hours (30%), so mild June temperatures outweigh the
  rain penalty. Legitimate limitation of `int_weather_comfort.sql`'s simple
  heuristic, not a data error.
- **Amadeus is gone.** It originally supplied both a secondary demand signal and
  all price data. Amadeus decommissioned its entire self-service portal
  (including existing free keys) on 2026-07-17. Demand now comes from OpenSky
  alone; price comes from the Travelpayouts Data API.
