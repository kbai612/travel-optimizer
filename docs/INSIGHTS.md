# Findings

<!-- GENERATED FILE — do not edit by hand. -->
<!-- Regenerate with: uv run python -m report.insights -->

_Auto-generated from `warehouse.duckdb` on 2026-07-03 06:48 UTC, covering 23 destinations × 12 months. Numbers reflect whatever real data the warehouse currently holds (coverage varies by source — see the coverage table below)._

## Does the score match conventional wisdom?

An external check: for each destination, the model's monthly scores are compared against the *conventionally-recommended* time to visit (mainstream travel-guide consensus, encoded in `report/reference.py`) — signals the model never sees. This is a sanity check, not a target the model is tuned toward.

- **Directional agreement:** for **6/8** destinations the recommended months average a higher travel score than the rest of the year (mean margin **+2.8** points).
- **Peak month in the recommended window:** **5/8** (exact), rising to **8/8** allowing a ±1-month tolerance.

| Destination | Recommended window | Rec. avg | Off-season avg | Margin | Peak month |
|---|---|---:|---:|---:|---|
| Bangkok (BKK) | cool, dry season | 60.9 | 59.0 | +1.9 | Nov ✅ |
| Cape Town (CPT) | Southern-Hemisphere summer & autumn | 60.8 | 57.3 | +3.4 | Jan ✅ |
| Rio de Janeiro (GIG) | the dry Southern-Hemisphere winter | 75.0 | 69.8 | +5.2 | Aug ✅ |
| Tokyo (HND) | cherry-blossom spring & autumn foliage | 69.4 | 71.7 | -2.3 | Jun ≈ |
| New York (JFK) | late spring & crisp autumn | 65.0 | 59.5 | +5.5 | Aug ≈ |
| Reykjavik (KEF) | the short Icelandic summer | 72.2 | 61.6 | +10.7 | Jul ✅ |
| Lisbon (LIS) | spring & early-autumn shoulder season | 68.9 | 73.0 | -4.1 | Jul ≈ |
| Sydney (SYD) | late summer, autumn & spring | 73.9 | 71.7 | +2.2 | Feb ✅ |

Where the model diverges it's explainable rather than random: Tokyo's peak lands in June because the weather-comfort formula weights mild temperature above the rainy-season precipitation penalty, and Lisbon skews to peak summer because the model optimizes weather comfort over the crowd-avoidance that drives the shoulder-season guidance. Both are documented limitations in the README, surfaced here by the validation rather than hidden by it.

## Best month, by destination

| Destination | Top month | Score | Confidence | Leading real signal |
|---|---|---|---|---|
| Amsterdam (AMS) | Aug | 69.4 | 70% | good fares |
| Barcelona (BCN) | Aug | 69.4 | 80% | good fares |
| Bangkok (BKK) | Nov | 66.0 | 58% | good fares |
| Paris (CDG) | Sep | 68.7 | 70% | good fares |
| Cape Town (CPT) | Jan | 68.3 | 82% | mild weather |
| Cancun (CUN) | Aug | 81.1 | 80% | good fares |
| Bali (DPS) | Jul | 63.3 | 62% | few holiday spikes |
| Dubai (DXB) | Dec | 49.4 | 68% | mild weather |
| Buenos Aires (EZE) | Dec | 77.5 | 70% | good fares |
| Rome (FCO) | Sep | 74.5 | 80% | good fares |
| Rio de Janeiro (GIG) | Aug | 84.4 | 80% | good fares |
| Hong Kong (HKG) | Aug | 64.9 | 80% | few holiday spikes |
| Tokyo (HND) | Jun | 79.9 | 100% | few holiday spikes |
| Honolulu (HNL) | Aug | 85.6 | 80% | good fares |
| Istanbul (IST) | Sep | 74.2 | 80% | good fares |
| New York (JFK) | Aug | 74.5 | 82% | few holiday spikes |
| Reykjavik (KEF) | Jul | 85.1 | 100% | light crowds |
| Los Angeles (LAX) | Aug | 82.2 | 80% | few holiday spikes |
| London (LHR) | Sep | 68.1 | 70% | good fares |
| Lisbon (LIS) | Jul | 81.5 | 80% | good fares |
| Marrakesh (RAK) | Oct | 63.2 | 52% | few holiday spikes |
| Singapore (SIN) | Sep | 71.6 | 62% | few holiday spikes |
| Sydney (SYD) | Feb | 86.2 | 82% | light crowds |

## Signal coverage

Which signals are backed by real data vs. a neutral model default, per destination (● real · ○ default). `data_confidence` is the weight-weighted share of the score backed by real data.

| Destination | Weather | Demand | Price | Holiday | Air quality | Sea temp | Confidence |
|---|---|---|---|---|---|---|---|
| Amsterdam (AMS) | ● | ○ | ● | ● | ● | ○ | 61% |
| Barcelona (BCN) | ● | ○ | ● | ● | ● | ● | 66% |
| Bangkok (BKK) | ● | ○ | ● | ○ | ● | ○ | 49% |
| Paris (CDG) | ● | ○ | ● | ● | ● | ○ | 62% |
| Cape Town (CPT) | ● | ● | ● | ● | ● | ● | 85% |
| Cancun (CUN) | ● | ○ | ● | ● | ● | ● | 70% |
| Bali (DPS) | ● | ○ | ○ | ● | ● | ● | 62% |
| Dubai (DXB) | ● | ○ | ● | ○ | ● | ● | 58% |
| Buenos Aires (EZE) | ● | ○ | ● | ● | ● | ○ | 56% |
| Rome (FCO) | ● | ○ | ● | ● | ● | ● | 68% |
| Rio de Janeiro (GIG) | ● | ○ | ● | ● | ● | ● | 70% |
| Hong Kong (HKG) | ● | ○ | ● | ● | ● | ● | 68% |
| Tokyo (HND) | ● | ● | ● | ● | ● | ● | 98% |
| Honolulu (HNL) | ● | ○ | ● | ● | ● | ● | 65% |
| Istanbul (IST) | ● | ○ | ● | ● | ● | ● | 71% |
| New York (JFK) | ● | ● | ○ | ● | ● | ● | 82% |
| Reykjavik (KEF) | ● | ● | ● | ● | ● | ● | 82% |
| Los Angeles (LAX) | ● | ○ | ● | ● | ● | ● | 66% |
| London (LHR) | ● | ○ | ● | ● | ● | ○ | 60% |
| Lisbon (LIS) | ● | ● | ● | ● | ● | ● | 88% |
| Marrakesh (RAK) | ● | ○ | ○ | ● | ● | ○ | 52% |
| Singapore (SIN) | ● | ○ | ○ | ● | ● | ● | 62% |
| Sydney (SYD) | ● | ● | ● | ● | ● | ● | 72% |

## Hemisphere sanity check

Peak months should invert across the equator — Northern-Hemisphere destinations peaking in mid-year, Southern in the local (Dec–Feb) summer half.

- **Northern**: 16/20 peak in the Apr–Sep half.
- **Southern**: 2/3 peak in the Oct–Apr half.
