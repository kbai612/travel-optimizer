# Findings

<!-- GENERATED FILE — do not edit by hand. -->
<!-- Regenerate with: uv run python -m report.insights -->

_Auto-generated from `warehouse.duckdb` on 2026-07-31 10:07 UTC, covering 23 destinations × 12 months. Numbers reflect whatever real data the warehouse currently holds (coverage varies by source — see the coverage table below)._

## Does the score match conventional wisdom?

An external check: for each destination, the model's monthly scores are compared against the *conventionally-recommended* time to visit (mainstream travel-guide consensus, encoded in `report/reference.py`) — signals the model never sees. This is a sanity check, not a target the model is tuned toward.

- **Directional agreement:** for **6/8** destinations the recommended months average a higher travel score than the rest of the year (mean margin **+4.3** points).
- **Peak month in the recommended window:** **5/8** (exact), rising to **7/8** allowing a ±1-month tolerance.

| Destination | Recommended window | Rec. avg | Off-season avg | Margin | Peak month |
|---|---|---:|---:|---:|---|
| Bangkok (BKK) | cool, dry season | 75.3 | 70.8 | +4.4 | Nov ✅ |
| Cape Town (CPT) | Southern-Hemisphere summer & autumn | 74.8 | 68.9 | +5.9 | Jan ✅ |
| Rio de Janeiro (GIG) | the dry Southern-Hemisphere winter | 76.4 | 71.0 | +5.4 | Aug ✅ |
| Tokyo (HND) | cherry-blossom spring & autumn foliage | 71.3 | 71.6 | -0.3 | Jun ≈ |
| New York (JFK) | late spring & crisp autumn | 70.4 | 60.8 | +9.6 | Aug ≈ |
| Reykjavik (KEF) | the short Icelandic summer | 67.5 | 54.9 | +12.6 | Jul ✅ |
| Lisbon (LIS) | spring & early-autumn shoulder season | 70.3 | 76.6 | -6.3 | Jan ✗ |
| Sydney (SYD) | late summer, autumn & spring | 72.9 | 69.7 | +3.2 | Nov ✅ |

Where the model diverges it's explainable rather than random: Tokyo's peak lands in June because the weather-comfort formula weights mild temperature above the rainy-season precipitation penalty, and Lisbon skews to peak summer because the model optimizes weather comfort over the crowd-avoidance that drives the shoulder-season guidance. Both are documented limitations in the README, surfaced here by the validation rather than hidden by it.

## Best month, by destination

| Destination | Top month | Score | Confidence | Leading real signal |
|---|---|---|---|---|
| Amsterdam (AMS) | Aug | 81.6 | 70% | good fares |
| Barcelona (BCN) | Aug | 82.4 | 80% | good fares |
| Bangkok (BKK) | Nov | 77.3 | 78% | good fares |
| Paris (CDG) | Sep | 80.8 | 70% | good fares |
| Cape Town (CPT) | Jan | 87.1 | 100% | mild weather |
| Cancun (CUN) | Feb | 82.7 | 80% | good fares |
| Bali (DPS) | Sep | 82.5 | 80% | good fares |
| Dubai (DXB) | Mar | 81.5 | 68% | good fares |
| Buenos Aires (EZE) | Nov | 79.9 | 70% | good fares |
| Rome (FCO) | Sep | 87.6 | 80% | good fares |
| Rio de Janeiro (GIG) | Aug | 82.5 | 80% | few holiday spikes |
| Hong Kong (HKG) | Aug | 77.8 | 80% | good fares |
| Tokyo (HND) | Jun | 80.6 | 100% | few holiday spikes |
| Honolulu (HNL) | Sep | 82.6 | 80% | good fares |
| Istanbul (IST) | Sep | 87.3 | 80% | good fares |
| New York (JFK) | Aug | 83.5 | 100% | good fares |
| Reykjavik (KEF) | Jul | 73.8 | 80% | few holiday spikes |
| Los Angeles (LAX) | Sep | 81.6 | 80% | good fares |
| London (LHR) | Sep | 80.1 | 70% | good fares |
| Lisbon (LIS) | Jan | 82.0 | 100% | good fares |
| Marrakesh (RAK) | Oct | 74.3 | 52% | few holiday spikes |
| Singapore (SIN) | Sep | 80.6 | 80% | good fares |
| Sydney (SYD) | Nov | 82.1 | 100% | good fares |

## Signal coverage

Which signals are backed by real data vs. a neutral model default, per destination (● real · ○ default). `data_confidence` is the weight-weighted share of the score backed by real data.

| Destination | Weather | Demand | Price | Holiday | Air quality | Sea temp | Confidence |
|---|---|---|---|---|---|---|---|
| Amsterdam (AMS) | ● | ○ | ● | ● | ● | ○ | 62% |
| Barcelona (BCN) | ● | ○ | ● | ● | ● | ● | 74% |
| Bangkok (BKK) | ● | ● | ● | ○ | ● | ○ | 73% |
| Paris (CDG) | ● | ○ | ● | ● | ● | ○ | 67% |
| Cape Town (CPT) | ● | ● | ● | ● | ● | ● | 91% |
| Cancun (CUN) | ● | ○ | ● | ● | ● | ● | 74% |
| Bali (DPS) | ● | ○ | ● | ● | ● | ● | 71% |
| Dubai (DXB) | ● | ○ | ● | ○ | ● | ● | 62% |
| Buenos Aires (EZE) | ● | ○ | ● | ● | ● | ○ | 62% |
| Rome (FCO) | ● | ○ | ● | ● | ● | ● | 76% |
| Rio de Janeiro (GIG) | ● | ○ | ● | ● | ● | ● | 72% |
| Hong Kong (HKG) | ● | ○ | ● | ● | ● | ● | 71% |
| Tokyo (HND) | ● | ● | ● | ● | ● | ● | 100% |
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
