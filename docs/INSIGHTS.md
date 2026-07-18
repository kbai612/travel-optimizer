# Findings

<!-- GENERATED FILE — do not edit by hand. -->
<!-- Regenerate with: uv run python -m report.insights -->

_Auto-generated from `warehouse.duckdb` on 2026-07-18 08:59 UTC, covering 23 destinations × 12 months. Numbers reflect whatever real data the warehouse currently holds (coverage varies by source — see the coverage table below)._

## Does the score match conventional wisdom?

An external check: for each destination, the model's monthly scores are compared against the *conventionally-recommended* time to visit (mainstream travel-guide consensus, encoded in `report/reference.py`) — signals the model never sees. This is a sanity check, not a target the model is tuned toward.

- **Directional agreement:** for **7/8** destinations the recommended months average a higher travel score than the rest of the year (mean margin **+4.7** points).
- **Peak month in the recommended window:** **6/8** (exact), rising to **8/8** allowing a ±1-month tolerance.

| Destination | Recommended window | Rec. avg | Off-season avg | Margin | Peak month |
|---|---|---:|---:|---:|---|
| Bangkok (BKK) | cool, dry season | 73.3 | 70.8 | +2.5 | Nov ✅ |
| Cape Town (CPT) | Southern-Hemisphere summer & autumn | 73.7 | 67.5 | +6.2 | Jan ✅ |
| Rio de Janeiro (GIG) | the dry Southern-Hemisphere winter | 76.2 | 69.7 | +6.5 | Sep ✅ |
| Tokyo (HND) | cherry-blossom spring & autumn foliage | 71.2 | 70.4 | +0.8 | Jun ≈ |
| New York (JFK) | late spring & crisp autumn | 70.4 | 60.6 | +9.9 | Aug ≈ |
| Reykjavik (KEF) | the short Icelandic summer | 67.0 | 55.0 | +12.0 | Jul ✅ |
| Lisbon (LIS) | spring & early-autumn shoulder season | 70.3 | 73.7 | -3.4 | Sep ✅ |
| Sydney (SYD) | late summer, autumn & spring | 72.9 | 69.5 | +3.3 | Nov ✅ |

Where the model diverges it's explainable rather than random: Tokyo's peak lands in June because the weather-comfort formula weights mild temperature above the rainy-season precipitation penalty, and Lisbon skews to peak summer because the model optimizes weather comfort over the crowd-avoidance that drives the shoulder-season guidance. Both are documented limitations in the README, surfaced here by the validation rather than hidden by it.

## Best month, by destination

| Destination | Top month | Score | Confidence | Leading real signal |
|---|---|---|---|---|
| Amsterdam (AMS) | Aug | 81.6 | 70% | good fares |
| Barcelona (BCN) | Aug | 81.5 | 80% | warm seas |
| Bangkok (BKK) | Nov | 77.3 | 78% | good fares |
| Paris (CDG) | Sep | 80.8 | 70% | good fares |
| Cape Town (CPT) | Jan | 88.1 | 100% | mild weather |
| Cancun (CUN) | Feb | 82.7 | 80% | good fares |
| Bali (DPS) | Jul | 83.5 | 80% | good fares |
| Dubai (DXB) | Dec | 81.8 | 68% | mild weather |
| Buenos Aires (EZE) | Nov | 79.9 | 70% | good fares |
| Rome (FCO) | Sep | 87.5 | 80% | few holiday spikes |
| Rio de Janeiro (GIG) | Sep | 80.6 | 80% | good fares |
| Hong Kong (HKG) | Aug | 77.8 | 80% | good fares |
| Tokyo (HND) | Jun | 79.2 | 100% | few holiday spikes |
| Honolulu (HNL) | Aug | 85.6 | 80% | good fares |
| Istanbul (IST) | Sep | 87.3 | 80% | good fares |
| New York (JFK) | Aug | 82.0 | 100% | few holiday spikes |
| Reykjavik (KEF) | Jul | 73.4 | 80% | few holiday spikes |
| Los Angeles (LAX) | Sep | 81.6 | 80% | good fares |
| London (LHR) | Sep | 80.1 | 70% | good fares |
| Lisbon (LIS) | Sep | 80.9 | 100% | good fares |
| Marrakesh (RAK) | Oct | 74.3 | 52% | few holiday spikes |
| Singapore (SIN) | Sep | 80.6 | 80% | good fares |
| Sydney (SYD) | Nov | 82.1 | 100% | good fares |

## Signal coverage

Which signals are backed by real data vs. a neutral model default, per destination (● real · ○ default). `data_confidence` is the weight-weighted share of the score backed by real data.

| Destination | Weather | Demand | Price | Holiday | Air quality | Sea temp | Confidence |
|---|---|---|---|---|---|---|---|
| Amsterdam (AMS) | ● | ○ | ● | ● | ● | ○ | 61% |
| Barcelona (BCN) | ● | ○ | ● | ● | ● | ● | 71% |
| Bangkok (BKK) | ● | ● | ● | ○ | ● | ○ | 72% |
| Paris (CDG) | ● | ○ | ● | ● | ● | ○ | 67% |
| Cape Town (CPT) | ● | ● | ● | ● | ● | ● | 88% |
| Cancun (CUN) | ● | ○ | ● | ● | ● | ● | 72% |
| Bali (DPS) | ● | ○ | ● | ● | ● | ● | 66% |
| Dubai (DXB) | ● | ○ | ● | ○ | ● | ● | 59% |
| Buenos Aires (EZE) | ● | ○ | ● | ● | ● | ○ | 60% |
| Rome (FCO) | ● | ○ | ● | ● | ● | ● | 71% |
| Rio de Janeiro (GIG) | ● | ○ | ● | ● | ● | ● | 71% |
| Hong Kong (HKG) | ● | ○ | ● | ● | ● | ● | 71% |
| Tokyo (HND) | ● | ● | ● | ● | ● | ● | 98% |
| Honolulu (HNL) | ● | ○ | ● | ● | ● | ● | 71% |
| Istanbul (IST) | ● | ○ | ● | ● | ● | ● | 77% |
| New York (JFK) | ● | ● | ● | ● | ● | ● | 91% |
| Reykjavik (KEF) | ● | ○ | ● | ● | ● | ● | 70% |
| Los Angeles (LAX) | ● | ○ | ● | ● | ● | ● | 68% |
| London (LHR) | ● | ○ | ● | ● | ● | ○ | 60% |
| Lisbon (LIS) | ● | ● | ● | ● | ● | ● | 92% |
| Marrakesh (RAK) | ● | ○ | ○ | ● | ● | ○ | 52% |
| Singapore (SIN) | ● | ○ | ● | ● | ● | ● | 68% |
| Sydney (SYD) | ● | ● | ● | ● | ● | ● | 80% |

## Hemisphere sanity check

Peak months should invert across the equator — Northern-Hemisphere destinations peaking in mid-year, Southern in the local (Dec–Feb) summer half.

- **Northern**: 15/20 peak in the Apr–Sep half.
- **Southern**: 2/3 peak in the Oct–Apr half.
