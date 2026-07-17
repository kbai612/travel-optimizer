# Findings

<!-- GENERATED FILE — do not edit by hand. -->
<!-- Regenerate with: uv run python -m report.insights -->

_Auto-generated from `warehouse.duckdb` on 2026-07-17 10:16 UTC, covering 23 destinations × 12 months. Numbers reflect whatever real data the warehouse currently holds (coverage varies by source — see the coverage table below)._

## Does the score match conventional wisdom?

An external check: for each destination, the model's monthly scores are compared against the *conventionally-recommended* time to visit (mainstream travel-guide consensus, encoded in `report/reference.py`) — signals the model never sees. This is a sanity check, not a target the model is tuned toward.

- **Directional agreement:** for **8/8** destinations the recommended months average a higher travel score than the rest of the year (mean margin **+5.8** points).
- **Peak month in the recommended window:** **5/8** (exact), rising to **8/8** allowing a ±1-month tolerance.

| Destination | Recommended window | Rec. avg | Off-season avg | Margin | Peak month |
|---|---|---:|---:|---:|---|
| Bangkok (BKK) | cool, dry season | 73.3 | 69.7 | +3.6 | Nov ✅ |
| Cape Town (CPT) | Southern-Hemisphere summer & autumn | 73.6 | 67.6 | +6.0 | Oct ≈ |
| Rio de Janeiro (GIG) | the dry Southern-Hemisphere winter | 76.2 | 69.7 | +6.5 | Aug ✅ |
| Tokyo (HND) | cherry-blossom spring & autumn foliage | 71.3 | 70.3 | +1.0 | Jun ≈ |
| New York (JFK) | late spring & crisp autumn | 70.8 | 60.2 | +10.6 | Aug ≈ |
| Reykjavik (KEF) | the short Icelandic summer | 66.8 | 54.0 | +12.8 | Jul ✅ |
| Lisbon (LIS) | spring & early-autumn shoulder season | 73.0 | 71.0 | +2.0 | Sep ✅ |
| Sydney (SYD) | late summer, autumn & spring | 73.0 | 69.4 | +3.6 | Nov ✅ |

Where the model diverges it's explainable rather than random: Tokyo's peak lands in June because the weather-comfort formula weights mild temperature above the rainy-season precipitation penalty, and Lisbon skews to peak summer because the model optimizes weather comfort over the crowd-avoidance that drives the shoulder-season guidance. Both are documented limitations in the README, surfaced here by the validation rather than hidden by it.

## Best month, by destination

| Destination | Top month | Score | Confidence | Leading real signal |
|---|---|---|---|---|
| Amsterdam (AMS) | Aug | 81.6 | 70% | good fares |
| Barcelona (BCN) | Aug | 82.4 | 80% | good fares |
| Bangkok (BKK) | Nov | 77.7 | 58% | good fares |
| Paris (CDG) | Sep | 80.8 | 70% | good fares |
| Cape Town (CPT) | Oct | 80.7 | 80% | good fares |
| Cancun (CUN) | Feb | 82.7 | 80% | good fares |
| Bali (DPS) | Jul | 83.5 | 80% | good fares |
| Dubai (DXB) | Dec | 81.8 | 68% | mild weather |
| Buenos Aires (EZE) | Sep | 79.7 | 70% | good fares |
| Rome (FCO) | Sep | 87.4 | 80% | few holiday spikes |
| Rio de Janeiro (GIG) | Aug | 80.6 | 80% | few holiday spikes |
| Hong Kong (HKG) | Aug | 77.8 | 80% | good fares |
| Tokyo (HND) | Jun | 79.1 | 80% | few holiday spikes |
| Honolulu (HNL) | Aug | 85.6 | 80% | good fares |
| Istanbul (IST) | Sep | 87.3 | 80% | good fares |
| New York (JFK) | Aug | 82.6 | 80% | few holiday spikes |
| Reykjavik (KEF) | Jul | 73.4 | 80% | few holiday spikes |
| Los Angeles (LAX) | Sep | 81.6 | 80% | good fares |
| London (LHR) | Sep | 80.1 | 70% | good fares |
| Lisbon (LIS) | Sep | 84.4 | 80% | good fares |
| Marrakesh (RAK) | Oct | 74.3 | 52% | few holiday spikes |
| Singapore (SIN) | Sep | 80.6 | 80% | good fares |
| Sydney (SYD) | Nov | 81.4 | 80% | good fares |

## Signal coverage

Which signals are backed by real data vs. a neutral model default, per destination (● real · ○ default). `data_confidence` is the weight-weighted share of the score backed by real data.

| Destination | Weather | Demand | Price | Holiday | Air quality | Sea temp | Confidence |
|---|---|---|---|---|---|---|---|
| Amsterdam (AMS) | ● | ○ | ● | ● | ● | ○ | 61% |
| Barcelona (BCN) | ● | ○ | ● | ● | ● | ● | 70% |
| Bangkok (BKK) | ● | ○ | ● | ○ | ● | ○ | 50% |
| Paris (CDG) | ● | ○ | ● | ● | ● | ○ | 67% |
| Cape Town (CPT) | ● | ○ | ● | ● | ● | ● | 68% |
| Cancun (CUN) | ● | ○ | ● | ● | ● | ● | 72% |
| Bali (DPS) | ● | ○ | ● | ● | ● | ● | 66% |
| Dubai (DXB) | ● | ○ | ● | ○ | ● | ● | 59% |
| Buenos Aires (EZE) | ● | ○ | ● | ● | ● | ○ | 58% |
| Rome (FCO) | ● | ○ | ● | ● | ● | ● | 71% |
| Rio de Janeiro (GIG) | ● | ○ | ● | ● | ● | ● | 71% |
| Hong Kong (HKG) | ● | ○ | ● | ● | ● | ● | 71% |
| Tokyo (HND) | ● | ○ | ● | ● | ● | ● | 79% |
| Honolulu (HNL) | ● | ○ | ● | ● | ● | ● | 71% |
| Istanbul (IST) | ● | ○ | ● | ● | ● | ● | 77% |
| New York (JFK) | ● | ○ | ● | ● | ● | ● | 71% |
| Reykjavik (KEF) | ● | ○ | ● | ● | ● | ● | 68% |
| Los Angeles (LAX) | ● | ○ | ● | ● | ● | ● | 68% |
| London (LHR) | ● | ○ | ● | ● | ● | ○ | 60% |
| Lisbon (LIS) | ● | ○ | ● | ● | ● | ● | 72% |
| Marrakesh (RAK) | ● | ○ | ○ | ● | ● | ○ | 52% |
| Singapore (SIN) | ● | ○ | ● | ● | ● | ● | 68% |
| Sydney (SYD) | ● | ○ | ● | ● | ● | ● | 70% |

## Hemisphere sanity check

Peak months should invert across the equator — Northern-Hemisphere destinations peaking in mid-year, Southern in the local (Dec–Feb) summer half.

- **Northern**: 16/20 peak in the Apr–Sep half.
- **Southern**: 2/3 peak in the Oct–Apr half.
