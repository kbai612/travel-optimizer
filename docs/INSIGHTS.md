# Findings

<!-- GENERATED FILE — do not edit by hand. -->
<!-- Regenerate with: uv run python -m report.insights -->

_Auto-generated from `warehouse.duckdb` on 2026-07-11 09:02 UTC, covering 23 destinations × 12 months. Numbers reflect whatever real data the warehouse currently holds (coverage varies by source — see the coverage table below)._

## Does the score match conventional wisdom?

An external check: for each destination, the model's monthly scores are compared against the *conventionally-recommended* time to visit (mainstream travel-guide consensus, encoded in `report/reference.py`) — signals the model never sees. This is a sanity check, not a target the model is tuned toward.

- **Directional agreement:** for **7/8** destinations the recommended months average a higher travel score than the rest of the year (mean margin **+4.7** points).
- **Peak month in the recommended window:** **7/8** (exact), rising to **8/8** allowing a ±1-month tolerance.

| Destination | Recommended window | Rec. avg | Off-season avg | Margin | Peak month |
|---|---|---:|---:|---:|---|
| Bangkok (BKK) | cool, dry season | 73.1 | 69.7 | +3.4 | Nov ✅ |
| Cape Town (CPT) | Southern-Hemisphere summer & autumn | 62.6 | 57.4 | +5.2 | Jan ✅ |
| Rio de Janeiro (GIG) | the dry Southern-Hemisphere winter | 65.0 | 59.3 | +5.7 | Aug ✅ |
| Tokyo (HND) | cherry-blossom spring & autumn foliage | 71.1 | 70.6 | +0.5 | Jun ≈ |
| New York (JFK) | late spring & crisp autumn | 68.6 | 60.7 | +7.9 | Sep ✅ |
| Reykjavik (KEF) | the short Icelandic summer | 68.3 | 52.0 | +16.3 | Jul ✅ |
| Lisbon (LIS) | spring & early-autumn shoulder season | 70.3 | 73.8 | -3.5 | Sep ✅ |
| Sydney (SYD) | late summer, autumn & spring | 71.5 | 69.4 | +2.1 | Dec ✅ |

Where the model diverges it's explainable rather than random: Tokyo's peak lands in June because the weather-comfort formula weights mild temperature above the rainy-season precipitation penalty, and Lisbon skews to peak summer because the model optimizes weather comfort over the crowd-avoidance that drives the shoulder-season guidance. Both are documented limitations in the README, surfaced here by the validation rather than hidden by it.

## Best month, by destination

| Destination | Top month | Score | Confidence | Leading real signal |
|---|---|---|---|---|
| Amsterdam (AMS) | Aug | 69.4 | 70% | good fares |
| Barcelona (BCN) | Aug | 70.0 | 80% | good fares |
| Bangkok (BKK) | Nov | 77.3 | 78% | good fares |
| Paris (CDG) | Sep | 68.7 | 70% | good fares |
| Cape Town (CPT) | Jan | 74.9 | 100% | mild weather |
| Cancun (CUN) | Feb | 82.7 | 80% | good fares |
| Bali (DPS) | Jul | 71.0 | 80% | good fares |
| Dubai (DXB) | Dec | 49.5 | 68% | mild weather |
| Buenos Aires (EZE) | Sep | 79.7 | 70% | good fares |
| Rome (FCO) | Sep | 74.4 | 80% | few holiday spikes |
| Rio de Janeiro (GIG) | Aug | 68.4 | 80% | few holiday spikes |
| Hong Kong (HKG) | Aug | 66.1 | 80% | good fares |
| Tokyo (HND) | Jun | 79.0 | 100% | few holiday spikes |
| Honolulu (HNL) | Aug | 85.6 | 80% | good fares |
| Istanbul (IST) | Sep | 74.2 | 80% | good fares |
| New York (JFK) | Sep | 81.6 | 100% | good fares |
| Reykjavik (KEF) | Jul | 75.1 | 80% | good fares |
| Los Angeles (LAX) | Sep | 81.6 | 80% | good fares |
| London (LHR) | Sep | 68.1 | 70% | good fares |
| Lisbon (LIS) | Sep | 80.9 | 100% | good fares |
| Marrakesh (RAK) | Oct | 63.2 | 52% | few holiday spikes |
| Singapore (SIN) | Sep | 80.6 | 80% | good fares |
| Sydney (SYD) | Dec | 76.6 | 100% | mild weather |

## Signal coverage

Which signals are backed by real data vs. a neutral model default, per destination (● real · ○ default). `data_confidence` is the weight-weighted share of the score backed by real data.

| Destination | Weather | Demand | Price | Holiday | Air quality | Sea temp | Confidence |
|---|---|---|---|---|---|---|---|
| Amsterdam (AMS) | ● | ○ | ● | ● | ● | ○ | 61% |
| Barcelona (BCN) | ● | ○ | ● | ● | ● | ● | 68% |
| Bangkok (BKK) | ● | ● | ● | ○ | ● | ○ | 70% |
| Paris (CDG) | ● | ○ | ● | ● | ● | ○ | 63% |
| Cape Town (CPT) | ● | ● | ● | ● | ● | ● | 88% |
| Cancun (CUN) | ● | ○ | ● | ● | ● | ● | 72% |
| Bali (DPS) | ● | ○ | ● | ● | ● | ● | 66% |
| Dubai (DXB) | ● | ○ | ● | ○ | ● | ● | 59% |
| Buenos Aires (EZE) | ● | ○ | ● | ● | ● | ○ | 58% |
| Rome (FCO) | ● | ○ | ● | ● | ● | ● | 71% |
| Rio de Janeiro (GIG) | ● | ○ | ● | ● | ● | ● | 71% |
| Hong Kong (HKG) | ● | ○ | ● | ● | ● | ● | 70% |
| Tokyo (HND) | ● | ● | ● | ● | ● | ● | 98% |
| Honolulu (HNL) | ● | ○ | ● | ● | ● | ● | 70% |
| Istanbul (IST) | ● | ○ | ● | ● | ● | ● | 76% |
| New York (JFK) | ● | ● | ● | ● | ● | ● | 90% |
| Reykjavik (KEF) | ● | ○ | ● | ● | ● | ● | 65% |
| Los Angeles (LAX) | ● | ○ | ● | ● | ● | ● | 68% |
| London (LHR) | ● | ○ | ● | ● | ● | ○ | 60% |
| Lisbon (LIS) | ● | ● | ● | ● | ● | ● | 92% |
| Marrakesh (RAK) | ● | ○ | ○ | ● | ● | ○ | 52% |
| Singapore (SIN) | ● | ○ | ● | ● | ● | ● | 66% |
| Sydney (SYD) | ● | ● | ● | ● | ● | ● | 78% |

## Hemisphere sanity check

Peak months should invert across the equator — Northern-Hemisphere destinations peaking in mid-year, Southern in the local (Dec–Feb) summer half.

- **Northern**: 16/20 peak in the Apr–Sep half.
- **Southern**: 2/3 peak in the Oct–Apr half.
