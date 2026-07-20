# Findings

<!-- GENERATED FILE — do not edit by hand. -->
<!-- Regenerate with: uv run python -m report.insights -->

_Auto-generated from `warehouse.duckdb` on 2026-07-20 11:21 UTC, covering 23 destinations × 12 months. Numbers reflect whatever real data the warehouse currently holds (coverage varies by source — see the coverage table below)._

## Does the score match conventional wisdom?

An external check: for each destination, the model's monthly scores are compared against the *conventionally-recommended* time to visit (mainstream travel-guide consensus, encoded in `report/reference.py`) — signals the model never sees. This is a sanity check, not a target the model is tuned toward.

- **Directional agreement:** for **8/8** destinations the recommended months average a higher travel score than the rest of the year (mean margin **+5.4** points).
- **Peak month in the recommended window:** **5/8** (exact), rising to **8/8** allowing a ±1-month tolerance.

| Destination | Recommended window | Rec. avg | Off-season avg | Margin | Peak month |
|---|---|---:|---:|---:|---|
| Bangkok (BKK) | cool, dry season | 73.4 | 70.8 | +2.5 | Nov ✅ |
| Cape Town (CPT) | Southern-Hemisphere summer & autumn | 73.6 | 67.6 | +6.0 | Oct ≈ |
| Rio de Janeiro (GIG) | the dry Southern-Hemisphere winter | 76.4 | 71.0 | +5.4 | Aug ✅ |
| Tokyo (HND) | cherry-blossom spring & autumn foliage | 71.4 | 70.4 | +1.0 | Jun ≈ |
| New York (JFK) | late spring & crisp autumn | 70.8 | 60.4 | +10.4 | Aug ≈ |
| Reykjavik (KEF) | the short Icelandic summer | 67.3 | 55.0 | +12.3 | Jul ✅ |
| Lisbon (LIS) | spring & early-autumn shoulder season | 73.0 | 71.0 | +2.0 | Sep ✅ |
| Sydney (SYD) | late summer, autumn & spring | 73.0 | 69.5 | +3.5 | Nov ✅ |

Where the model diverges it's explainable rather than random: Tokyo's peak lands in June because the weather-comfort formula weights mild temperature above the rainy-season precipitation penalty, and Lisbon skews to peak summer because the model optimizes weather comfort over the crowd-avoidance that drives the shoulder-season guidance. Both are documented limitations in the README, surfaced here by the validation rather than hidden by it.

## Best month, by destination

| Destination | Top month | Score | Confidence | Leading real signal |
|---|---|---|---|---|
| Amsterdam (AMS) | Aug | 81.6 | 70% | good fares |
| Barcelona (BCN) | Aug | 82.2 | 80% | good fares |
| Bangkok (BKK) | Nov | 77.7 | 58% | good fares |
| Paris (CDG) | Sep | 80.8 | 70% | good fares |
| Cape Town (CPT) | Oct | 80.7 | 80% | good fares |
| Cancun (CUN) | Feb | 82.7 | 80% | good fares |
| Bali (DPS) | Jul | 83.5 | 80% | good fares |
| Dubai (DXB) | Dec | 81.8 | 68% | mild weather |
| Buenos Aires (EZE) | Nov | 79.9 | 70% | good fares |
| Rome (FCO) | Sep | 87.6 | 80% | good fares |
| Rio de Janeiro (GIG) | Aug | 81.0 | 80% | few holiday spikes |
| Hong Kong (HKG) | Aug | 77.8 | 80% | good fares |
| Tokyo (HND) | Jun | 79.2 | 80% | few holiday spikes |
| Honolulu (HNL) | Aug | 85.6 | 80% | good fares |
| Istanbul (IST) | Sep | 87.3 | 80% | good fares |
| New York (JFK) | Aug | 84.0 | 80% | few holiday spikes |
| Reykjavik (KEF) | Jul | 73.5 | 80% | few holiday spikes |
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
| Barcelona (BCN) | ● | ○ | ● | ● | ● | ● | 72% |
| Bangkok (BKK) | ● | ○ | ● | ○ | ● | ○ | 52% |
| Paris (CDG) | ● | ○ | ● | ● | ● | ○ | 67% |
| Cape Town (CPT) | ● | ○ | ● | ● | ● | ● | 68% |
| Cancun (CUN) | ● | ○ | ● | ● | ● | ● | 72% |
| Bali (DPS) | ● | ○ | ● | ● | ● | ● | 68% |
| Dubai (DXB) | ● | ○ | ● | ○ | ● | ● | 59% |
| Buenos Aires (EZE) | ● | ○ | ● | ● | ● | ○ | 60% |
| Rome (FCO) | ● | ○ | ● | ● | ● | ● | 71% |
| Rio de Janeiro (GIG) | ● | ○ | ● | ● | ● | ● | 72% |
| Hong Kong (HKG) | ● | ○ | ● | ● | ● | ● | 71% |
| Tokyo (HND) | ● | ○ | ● | ● | ● | ● | 79% |
| Honolulu (HNL) | ● | ○ | ● | ● | ● | ● | 71% |
| Istanbul (IST) | ● | ○ | ● | ● | ● | ● | 77% |
| New York (JFK) | ● | ○ | ● | ● | ● | ● | 71% |
| Reykjavik (KEF) | ● | ○ | ● | ● | ● | ● | 70% |
| Los Angeles (LAX) | ● | ○ | ● | ● | ● | ● | 68% |
| London (LHR) | ● | ○ | ● | ● | ● | ○ | 60% |
| Lisbon (LIS) | ● | ○ | ● | ● | ● | ● | 72% |
| Marrakesh (RAK) | ● | ○ | ○ | ● | ● | ○ | 52% |
| Singapore (SIN) | ● | ○ | ● | ● | ● | ● | 68% |
| Sydney (SYD) | ● | ○ | ● | ● | ● | ● | 70% |

## Hemisphere sanity check

Peak months should invert across the equator — Northern-Hemisphere destinations peaking in mid-year, Southern in the local (Dec–Feb) summer half.

- **Northern**: 15/20 peak in the Apr–Sep half.
- **Southern**: 2/3 peak in the Oct–Apr half.
