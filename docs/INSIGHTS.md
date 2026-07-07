# Findings

<!-- GENERATED FILE — do not edit by hand. -->
<!-- Regenerate with: uv run python -m report.insights -->

_Auto-generated from `warehouse.duckdb` on 2026-07-07 10:33 UTC, covering 23 destinations × 12 months. Numbers reflect whatever real data the warehouse currently holds (coverage varies by source — see the coverage table below)._

## Does the score match conventional wisdom?

An external check: for each destination, the model's monthly scores are compared against the *conventionally-recommended* time to visit (mainstream travel-guide consensus, encoded in `report/reference.py`) — signals the model never sees. This is a sanity check, not a target the model is tuned toward.

- **Directional agreement:** for **7/8** destinations the recommended months average a higher travel score than the rest of the year (mean margin **+4.4** points).
- **Peak month in the recommended window:** **6/8** (exact), rising to **7/8** allowing a ±1-month tolerance.

| Destination | Recommended window | Rec. avg | Off-season avg | Margin | Peak month |
|---|---|---:|---:|---:|---|
| Bangkok (BKK) | cool, dry season | 60.3 | 59.3 | +1.0 | Sep ✗ |
| Cape Town (CPT) | Southern-Hemisphere summer & autumn | 60.3 | 57.4 | +3.0 | Jan ✅ |
| Rio de Janeiro (GIG) | the dry Southern-Hemisphere winter | 75.6 | 68.2 | +7.4 | Aug ✅ |
| Tokyo (HND) | cherry-blossom spring & autumn foliage | 70.9 | 69.3 | +1.6 | Jun ≈ |
| New York (JFK) | late spring & crisp autumn | 68.6 | 60.9 | +7.8 | Sep ✅ |
| Reykjavik (KEF) | the short Icelandic summer | 68.3 | 52.0 | +16.3 | Jul ✅ |
| Lisbon (LIS) | spring & early-autumn shoulder season | 70.3 | 73.8 | -3.5 | Sep ✅ |
| Sydney (SYD) | late summer, autumn & spring | 70.2 | 68.3 | +1.9 | Dec ✅ |

Where the model diverges it's explainable rather than random: Tokyo's peak lands in June because the weather-comfort formula weights mild temperature above the rainy-season precipitation penalty, and Lisbon skews to peak summer because the model optimizes weather comfort over the crowd-avoidance that drives the shoulder-season guidance. Both are documented limitations in the README, surfaced here by the validation rather than hidden by it.

## Best month, by destination

| Destination | Top month | Score | Confidence | Leading real signal |
|---|---|---|---|---|
| Amsterdam (AMS) | Aug | 69.4 | 70% | good fares |
| Barcelona (BCN) | Aug | 69.9 | 80% | good fares |
| Bangkok (BKK) | Sep | 64.5 | 78% | good fares |
| Paris (CDG) | Sep | 68.7 | 70% | good fares |
| Cape Town (CPT) | Jan | 68.3 | 82% | mild weather |
| Cancun (CUN) | Feb | 82.7 | 80% | good fares |
| Bali (DPS) | Jul | 71.0 | 80% | good fares |
| Dubai (DXB) | Dec | 49.8 | 68% | mild weather |
| Buenos Aires (EZE) | Sep | 79.7 | 70% | good fares |
| Rome (FCO) | Sep | 74.4 | 80% | few holiday spikes |
| Rio de Janeiro (GIG) | Aug | 81.7 | 80% | few holiday spikes |
| Hong Kong (HKG) | Aug | 66.1 | 80% | good fares |
| Tokyo (HND) | Jun | 78.9 | 100% | few holiday spikes |
| Honolulu (HNL) | Aug | 85.6 | 80% | good fares |
| Istanbul (IST) | Sep | 74.2 | 80% | good fares |
| New York (JFK) | Sep | 81.6 | 100% | good fares |
| Reykjavik (KEF) | Jul | 75.1 | 80% | good fares |
| Los Angeles (LAX) | Sep | 81.6 | 80% | good fares |
| London (LHR) | Sep | 68.1 | 70% | good fares |
| Lisbon (LIS) | Sep | 80.9 | 100% | good fares |
| Marrakesh (RAK) | Oct | 63.2 | 52% | few holiday spikes |
| Singapore (SIN) | Oct | 76.9 | 80% | good fares |
| Sydney (SYD) | Dec | 77.9 | 100% | good fares |

## Signal coverage

Which signals are backed by real data vs. a neutral model default, per destination (● real · ○ default). `data_confidence` is the weight-weighted share of the score backed by real data.

| Destination | Weather | Demand | Price | Holiday | Air quality | Sea temp | Confidence |
|---|---|---|---|---|---|---|---|
| Amsterdam (AMS) | ● | ○ | ● | ● | ● | ○ | 61% |
| Barcelona (BCN) | ● | ○ | ● | ● | ● | ● | 68% |
| Bangkok (BKK) | ● | ● | ● | ○ | ● | ○ | 69% |
| Paris (CDG) | ● | ○ | ● | ● | ● | ○ | 61% |
| Cape Town (CPT) | ● | ● | ● | ● | ● | ● | 85% |
| Cancun (CUN) | ● | ○ | ● | ● | ● | ● | 71% |
| Bali (DPS) | ● | ○ | ● | ● | ● | ● | 65% |
| Dubai (DXB) | ● | ○ | ● | ○ | ● | ● | 58% |
| Buenos Aires (EZE) | ● | ○ | ● | ● | ● | ○ | 58% |
| Rome (FCO) | ● | ○ | ● | ● | ● | ● | 70% |
| Rio de Janeiro (GIG) | ● | ○ | ● | ● | ● | ● | 68% |
| Hong Kong (HKG) | ● | ○ | ● | ● | ● | ● | 70% |
| Tokyo (HND) | ● | ● | ● | ● | ● | ● | 97% |
| Honolulu (HNL) | ● | ○ | ● | ● | ● | ● | 70% |
| Istanbul (IST) | ● | ○ | ● | ● | ● | ● | 76% |
| New York (JFK) | ● | ● | ● | ● | ● | ● | 90% |
| Reykjavik (KEF) | ● | ○ | ● | ● | ● | ● | 65% |
| Los Angeles (LAX) | ● | ○ | ● | ● | ● | ● | 68% |
| London (LHR) | ● | ○ | ● | ● | ● | ○ | 60% |
| Lisbon (LIS) | ● | ● | ● | ● | ● | ● | 92% |
| Marrakesh (RAK) | ● | ○ | ○ | ● | ● | ○ | 52% |
| Singapore (SIN) | ● | ○ | ● | ● | ● | ● | 64% |
| Sydney (SYD) | ● | ● | ● | ● | ● | ● | 75% |

## Hemisphere sanity check

Peak months should invert across the equator — Northern-Hemisphere destinations peaking in mid-year, Southern in the local (Dec–Feb) summer half.

- **Northern**: 16/20 peak in the Apr–Sep half.
- **Southern**: 2/3 peak in the Oct–Apr half.
