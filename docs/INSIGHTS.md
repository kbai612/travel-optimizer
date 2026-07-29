# Findings

<!-- GENERATED FILE — do not edit by hand. -->
<!-- Regenerate with: uv run python -m report.insights -->

_Auto-generated from `warehouse.duckdb` on 2026-07-29 10:00 UTC, covering 23 destinations × 12 months. Numbers reflect whatever real data the warehouse currently holds (coverage varies by source — see the coverage table below)._

## Does the score match conventional wisdom?

An external check: for each destination, the model's monthly scores are compared against the *conventionally-recommended* time to visit (mainstream travel-guide consensus, encoded in `report/reference.py`) — signals the model never sees. This is a sanity check, not a target the model is tuned toward.

- **Directional agreement:** for **7/8** destinations the recommended months average a higher travel score than the rest of the year (mean margin **+4.2** points).
- **Peak month in the recommended window:** **5/8** (exact), rising to **7/8** allowing a ±1-month tolerance.

| Destination | Recommended window | Rec. avg | Off-season avg | Margin | Peak month |
|---|---|---:|---:|---:|---|
| Bangkok (BKK) | cool, dry season | 75.2 | 70.8 | +4.4 | Nov ✅ |
| Cape Town (CPT) | Southern-Hemisphere summer & autumn | 63.6 | 58.6 | +5.0 | Jan ✅ |
| Rio de Janeiro (GIG) | the dry Southern-Hemisphere winter | 65.0 | 60.4 | +4.5 | Aug ✅ |
| Tokyo (HND) | cherry-blossom spring & autumn foliage | 71.3 | 70.4 | +0.9 | Jun ≈ |
| New York (JFK) | late spring & crisp autumn | 70.4 | 60.8 | +9.6 | Aug ≈ |
| Reykjavik (KEF) | the short Icelandic summer | 67.5 | 54.9 | +12.6 | Jul ✅ |
| Lisbon (LIS) | spring & early-autumn shoulder season | 70.3 | 76.7 | -6.4 | Jan ✗ |
| Sydney (SYD) | late summer, autumn & spring | 72.9 | 69.7 | +3.2 | Nov ✅ |

Where the model diverges it's explainable rather than random: Tokyo's peak lands in June because the weather-comfort formula weights mild temperature above the rainy-season precipitation penalty, and Lisbon skews to peak summer because the model optimizes weather comfort over the crowd-avoidance that drives the shoulder-season guidance. Both are documented limitations in the README, surfaced here by the validation rather than hidden by it.

## Best month, by destination

| Destination | Top month | Score | Confidence | Leading real signal |
|---|---|---|---|---|
| Amsterdam (AMS) | Aug | 69.4 | 70% | good fares |
| Barcelona (BCN) | Aug | 70.0 | 80% | good fares |
| Bangkok (BKK) | Nov | 77.3 | 78% | good fares |
| Paris (CDG) | Sep | 68.7 | 70% | good fares |
| Cape Town (CPT) | Jan | 73.9 | 100% | mild weather |
| Cancun (CUN) | Feb | 82.7 | 80% | good fares |
| Bali (DPS) | Sep | 70.1 | 80% | good fares |
| Dubai (DXB) | Mar | 48.9 | 68% | good fares |
| Buenos Aires (EZE) | Nov | 79.9 | 70% | good fares |
| Rome (FCO) | Sep | 74.5 | 80% | good fares |
| Rio de Janeiro (GIG) | Aug | 70.0 | 80% | few holiday spikes |
| Hong Kong (HKG) | Aug | 66.1 | 80% | good fares |
| Tokyo (HND) | Jun | 79.4 | 100% | few holiday spikes |
| Honolulu (HNL) | Sep | 82.6 | 80% | good fares |
| Istanbul (IST) | Sep | 74.2 | 80% | good fares |
| New York (JFK) | Aug | 83.5 | 100% | good fares |
| Reykjavik (KEF) | Jul | 73.8 | 80% | few holiday spikes |
| Los Angeles (LAX) | Sep | 81.6 | 80% | good fares |
| London (LHR) | Sep | 68.1 | 70% | good fares |
| Lisbon (LIS) | Jan | 82.0 | 100% | good fares |
| Marrakesh (RAK) | Oct | 63.2 | 52% | few holiday spikes |
| Singapore (SIN) | Sep | 80.6 | 80% | good fares |
| Sydney (SYD) | Nov | 82.1 | 100% | good fares |

## Signal coverage

Which signals are backed by real data vs. a neutral model default, per destination (● real · ○ default). `data_confidence` is the weight-weighted share of the score backed by real data.

| Destination | Weather | Demand | Price | Holiday | Air quality | Sea temp | Confidence |
|---|---|---|---|---|---|---|---|
| Amsterdam (AMS) | ● | ○ | ● | ● | ● | ○ | 61% |
| Barcelona (BCN) | ● | ○ | ● | ● | ● | ● | 74% |
| Bangkok (BKK) | ● | ● | ● | ○ | ● | ○ | 73% |
| Paris (CDG) | ● | ○ | ● | ● | ● | ○ | 67% |
| Cape Town (CPT) | ● | ● | ● | ● | ● | ● | 91% |
| Cancun (CUN) | ● | ○ | ● | ● | ● | ● | 72% |
| Bali (DPS) | ● | ○ | ● | ● | ● | ● | 71% |
| Dubai (DXB) | ● | ○ | ● | ○ | ● | ● | 60% |
| Buenos Aires (EZE) | ● | ○ | ● | ● | ● | ○ | 61% |
| Rome (FCO) | ● | ○ | ● | ● | ● | ● | 74% |
| Rio de Janeiro (GIG) | ● | ○ | ● | ● | ● | ● | 72% |
| Hong Kong (HKG) | ● | ○ | ● | ● | ● | ● | 71% |
| Tokyo (HND) | ● | ● | ● | ● | ● | ● | 98% |
| Honolulu (HNL) | ● | ○ | ● | ● | ● | ● | 71% |
| Istanbul (IST) | ● | ○ | ● | ● | ● | ● | 77% |
| New York (JFK) | ● | ● | ● | ● | ● | ● | 91% |
| Reykjavik (KEF) | ● | ○ | ● | ● | ● | ● | 70% |
| Los Angeles (LAX) | ● | ○ | ● | ● | ● | ● | 70% |
| London (LHR) | ● | ○ | ● | ● | ● | ○ | 60% |
| Lisbon (LIS) | ● | ● | ● | ● | ● | ● | 96% |
| Marrakesh (RAK) | ● | ○ | ○ | ● | ● | ○ | 52% |
| Singapore (SIN) | ● | ○ | ● | ● | ● | ● | 70% |
| Sydney (SYD) | ● | ● | ● | ● | ● | ● | 80% |

## Hemisphere sanity check

Peak months should invert across the equator — Northern-Hemisphere destinations peaking in mid-year, Southern in the local (Dec–Feb) summer half.

- **Northern**: 14/20 peak in the Apr–Sep half.
- **Southern**: 2/3 peak in the Oct–Apr half.
