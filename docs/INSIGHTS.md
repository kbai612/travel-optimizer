# Findings

<!-- GENERATED FILE — do not edit by hand. -->
<!-- Regenerate with: uv run python -m report.insights -->

_Auto-generated from `warehouse.duckdb` on 2026-07-04 09:30 UTC, covering 23 destinations × 12 months. Numbers reflect whatever real data the warehouse currently holds (coverage varies by source — see the coverage table below)._

## Does the score match conventional wisdom?

An external check: for each destination, the model's monthly scores are compared against the *conventionally-recommended* time to visit (mainstream travel-guide consensus, encoded in `report/reference.py`) — signals the model never sees. This is a sanity check, not a target the model is tuned toward.

- **Directional agreement:** for **5/8** destinations the recommended months average a higher travel score than the rest of the year (mean margin **+3.4** points).
- **Peak month in the recommended window:** **6/8** (exact), rising to **7/8** allowing a ±1-month tolerance.

| Destination | Recommended window | Rec. avg | Off-season avg | Margin | Peak month |
|---|---|---:|---:|---:|---|
| Bangkok (BKK) | cool, dry season | 58.4 | 58.6 | -0.2 | Sep ✗ |
| Cape Town (CPT) | Southern-Hemisphere summer & autumn | 59.5 | 56.1 | +3.4 | Jan ✅ |
| Rio de Janeiro (GIG) | the dry Southern-Hemisphere winter | 75.6 | 68.2 | +7.4 | Aug ✅ |
| Tokyo (HND) | cherry-blossom spring & autumn foliage | 67.5 | 69.5 | -2.0 | Jun ≈ |
| New York (JFK) | late spring & crisp autumn | 68.6 | 61.1 | +7.5 | Sep ✅ |
| Reykjavik (KEF) | the short Icelandic summer | 65.6 | 52.0 | +13.6 | Aug ✅ |
| Lisbon (LIS) | spring & early-autumn shoulder season | 69.0 | 73.7 | -4.7 | Sep ✅ |
| Sydney (SYD) | late summer, autumn & spring | 70.4 | 68.2 | +2.2 | Dec ✅ |

Where the model diverges it's explainable rather than random: Tokyo's peak lands in June because the weather-comfort formula weights mild temperature above the rainy-season precipitation penalty, and Lisbon skews to peak summer because the model optimizes weather comfort over the crowd-avoidance that drives the shoulder-season guidance. Both are documented limitations in the README, surfaced here by the validation rather than hidden by it.

## Best month, by destination

| Destination | Top month | Score | Confidence | Leading real signal |
|---|---|---|---|---|
| Amsterdam (AMS) | Aug | 69.4 | 70% | good fares |
| Barcelona (BCN) | Aug | 70.0 | 80% | good fares |
| Bangkok (BKK) | Sep | 64.3 | 78% | good fares |
| Paris (CDG) | Sep | 68.7 | 70% | good fares |
| Cape Town (CPT) | Jan | 68.3 | 82% | mild weather |
| Cancun (CUN) | Feb | 82.3 | 80% | warm seas |
| Bali (DPS) | Jul | 63.3 | 62% | few holiday spikes |
| Dubai (DXB) | Dec | 49.9 | 68% | mild weather |
| Buenos Aires (EZE) | Sep | 79.6 | 70% | few holiday spikes |
| Rome (FCO) | Sep | 73.9 | 80% | few holiday spikes |
| Rio de Janeiro (GIG) | Aug | 81.4 | 80% | few holiday spikes |
| Hong Kong (HKG) | Aug | 66.1 | 80% | good fares |
| Tokyo (HND) | Jun | 79.5 | 100% | few holiday spikes |
| Honolulu (HNL) | Aug | 85.6 | 80% | good fares |
| Istanbul (IST) | Sep | 74.2 | 80% | good fares |
| New York (JFK) | Sep | 81.6 | 100% | good fares |
| Reykjavik (KEF) | Aug | 72.2 | 80% | good fares |
| Los Angeles (LAX) | Aug | 82.7 | 80% | few holiday spikes |
| London (LHR) | Sep | 67.7 | 70% | few holiday spikes |
| Lisbon (LIS) | Sep | 80.9 | 100% | good fares |
| Marrakesh (RAK) | Oct | 63.2 | 52% | few holiday spikes |
| Singapore (SIN) | Sep | 71.6 | 62% | few holiday spikes |
| Sydney (SYD) | Dec | 78.6 | 80% | good fares |

## Signal coverage

Which signals are backed by real data vs. a neutral model default, per destination (● real · ○ default). `data_confidence` is the weight-weighted share of the score backed by real data.

| Destination | Weather | Demand | Price | Holiday | Air quality | Sea temp | Confidence |
|---|---|---|---|---|---|---|---|
| Amsterdam (AMS) | ● | ○ | ● | ● | ● | ○ | 60% |
| Barcelona (BCN) | ● | ○ | ● | ● | ● | ● | 66% |
| Bangkok (BKK) | ● | ● | ● | ○ | ● | ○ | 58% |
| Paris (CDG) | ● | ○ | ● | ● | ● | ○ | 61% |
| Cape Town (CPT) | ● | ● | ○ | ● | ● | ● | 82% |
| Cancun (CUN) | ● | ○ | ● | ● | ● | ● | 70% |
| Bali (DPS) | ● | ○ | ○ | ● | ● | ● | 62% |
| Dubai (DXB) | ● | ○ | ● | ○ | ● | ● | 56% |
| Buenos Aires (EZE) | ● | ○ | ● | ● | ● | ○ | 58% |
| Rome (FCO) | ● | ○ | ● | ● | ● | ● | 68% |
| Rio de Janeiro (GIG) | ● | ○ | ● | ● | ● | ● | 68% |
| Hong Kong (HKG) | ● | ○ | ● | ● | ● | ● | 70% |
| Tokyo (HND) | ● | ● | ● | ● | ● | ● | 94% |
| Honolulu (HNL) | ● | ○ | ● | ● | ● | ● | 68% |
| Istanbul (IST) | ● | ○ | ● | ● | ● | ● | 71% |
| New York (JFK) | ● | ● | ● | ● | ● | ● | 90% |
| Reykjavik (KEF) | ● | ○ | ● | ● | ● | ● | 64% |
| Los Angeles (LAX) | ● | ○ | ● | ● | ● | ● | 68% |
| London (LHR) | ● | ○ | ● | ● | ● | ○ | 60% |
| Lisbon (LIS) | ● | ● | ● | ● | ● | ● | 91% |
| Marrakesh (RAK) | ● | ○ | ○ | ● | ● | ○ | 52% |
| Singapore (SIN) | ● | ○ | ○ | ● | ● | ● | 62% |
| Sydney (SYD) | ● | ○ | ● | ● | ● | ● | 65% |

## Hemisphere sanity check

Peak months should invert across the equator — Northern-Hemisphere destinations peaking in mid-year, Southern in the local (Dec–Feb) summer half.

- **Northern**: 17/20 peak in the Apr–Sep half.
- **Southern**: 2/3 peak in the Oct–Apr half.
