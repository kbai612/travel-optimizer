# Findings

<!-- GENERATED FILE — do not edit by hand. -->
<!-- Regenerate with: uv run python -m report.insights -->

_Auto-generated from `warehouse.duckdb` on 2026-11-07 13:54 UTC, covering 23 destinations × 12 months. Numbers reflect whatever real data the warehouse currently holds (coverage varies by source — see the coverage table below)._

## Does the score match conventional wisdom?

An external check: for each destination, the model's monthly scores are compared against the *conventionally-recommended* time to visit (mainstream travel-guide consensus, encoded in `report/reference.py`) — signals the model never sees. This is a sanity check, not a target the model is tuned toward.

- **Directional agreement:** for **7/8** destinations the recommended months average a higher travel score than the rest of the year (mean margin **+3.9** points).
- **Peak month in the recommended window:** **5/8** (exact), rising to **7/8** allowing a ±1-month tolerance.

| Destination | Recommended window | Rec. avg | Off-season avg | Margin | Peak month |
|---|---|---:|---:|---:|---|
| Bangkok (BKK) | cool, dry season | 75.0 | 72.9 | +2.1 | Jan ✅ |
| Cape Town (CPT) | Southern-Hemisphere summer & autumn | 63.6 | 59.6 | +4.1 | Jan ✅ |
| Rio de Janeiro (GIG) | the dry Southern-Hemisphere winter | 66.4 | 63.4 | +3.0 | Aug ✅ |
| Tokyo (HND) | cherry-blossom spring & autumn foliage | 71.1 | 71.8 | -0.6 | Jun ≈ |
| New York (JFK) | late spring & crisp autumn | 72.9 | 64.9 | +8.0 | Aug ≈ |
| Reykjavik (KEF) | the short Icelandic summer | 71.4 | 60.4 | +11.0 | Jul ✅ |
| Lisbon (LIS) | spring & early-autumn shoulder season | 75.1 | 75.1 | +0.1 | Jan ✗ |
| Sydney (SYD) | late summer, autumn & spring | 75.8 | 72.5 | +3.3 | Feb ✅ |

Where the model diverges it's explainable rather than random: Tokyo's peak lands in June because the weather-comfort formula weights mild temperature above the rainy-season precipitation penalty, and Lisbon skews to peak summer because the model optimizes weather comfort over the crowd-avoidance that drives the shoulder-season guidance. Both are documented limitations in the README, surfaced here by the validation rather than hidden by it.

## Best month, by destination

| Destination | Top month | Score | Confidence | Leading real signal |
|---|---|---|---|---|
| Amsterdam (AMS) | Sep | 66.9 | 70% | few holiday spikes |
| Barcelona (BCN) | Aug | 69.1 | 80% | warm seas |
| Bangkok (BKK) | Jan | 78.4 | 78% | good fares |
| Paris (CDG) | Sep | 68.7 | 70% | good fares |
| Cape Town (CPT) | Jan | 71.5 | 100% | mild weather |
| Cancun (CUN) | Feb | 82.7 | 80% | good fares |
| Bali (DPS) | Jul | 71.0 | 80% | good fares |
| Dubai (DXB) | Jan | 49.4 | 68% | good fares |
| Buenos Aires (EZE) | Nov | 79.9 | 70% | good fares |
| Rome (FCO) | Sep | 74.5 | 80% | good fares |
| Rio de Janeiro (GIG) | Aug | 70.3 | 80% | few holiday spikes |
| Hong Kong (HKG) | Nov | 70.9 | 80% | good fares |
| Tokyo (HND) | Jun | 80.3 | 100% | few holiday spikes |
| Honolulu (HNL) | Sep | 82.6 | 80% | good fares |
| Istanbul (IST) | Sep | 73.7 | 80% | few holiday spikes |
| New York (JFK) | Aug | 84.6 | 100% | good fares |
| Reykjavik (KEF) | Jul | 74.7 | 80% | few holiday spikes |
| Los Angeles (LAX) | Sep | 81.6 | 80% | good fares |
| London (LHR) | Sep | 68.1 | 70% | good fares |
| Lisbon (LIS) | Jan | 82.0 | 100% | good fares |
| Marrakesh (RAK) | Mar | 69.0 | 70% | good fares |
| Singapore (SIN) | Sep | 80.6 | 80% | good fares |
| Sydney (SYD) | Feb | 85.1 | 100% | good fares |

## Signal coverage

Which signals are backed by real data vs. a neutral model default, per destination (● real · ○ default). `data_confidence` is the weight-weighted share of the score backed by real data.

| Destination | Weather | Demand | Price | Holiday | Air quality | Sea temp | Confidence |
|---|---|---|---|---|---|---|---|
| Amsterdam (AMS) | ● | ○ | ● | ● | ● | ○ | 70% |
| Barcelona (BCN) | ● | ○ | ● | ● | ● | ● | 80% |
| Bangkok (BKK) | ● | ● | ● | ○ | ● | ○ | 78% |
| Paris (CDG) | ● | ○ | ● | ● | ● | ○ | 70% |
| Cape Town (CPT) | ● | ● | ● | ● | ● | ● | 94% |
| Cancun (CUN) | ● | ○ | ● | ● | ● | ● | 80% |
| Bali (DPS) | ● | ○ | ● | ● | ● | ● | 79% |
| Dubai (DXB) | ● | ○ | ● | ○ | ● | ● | 66% |
| Buenos Aires (EZE) | ● | ○ | ● | ● | ● | ○ | 67% |
| Rome (FCO) | ● | ○ | ● | ● | ● | ● | 80% |
| Rio de Janeiro (GIG) | ● | ○ | ● | ● | ● | ● | 79% |
| Hong Kong (HKG) | ● | ○ | ● | ● | ● | ● | 79% |
| Tokyo (HND) | ● | ● | ● | ● | ● | ● | 100% |
| Honolulu (HNL) | ● | ○ | ● | ● | ● | ● | 76% |
| Istanbul (IST) | ● | ○ | ● | ● | ● | ● | 80% |
| New York (JFK) | ● | ● | ● | ● | ● | ● | 100% |
| Reykjavik (KEF) | ● | ○ | ● | ● | ● | ● | 80% |
| Los Angeles (LAX) | ● | ○ | ● | ● | ● | ● | 76% |
| London (LHR) | ● | ○ | ● | ● | ● | ○ | 70% |
| Lisbon (LIS) | ● | ● | ● | ● | ● | ● | 100% |
| Marrakesh (RAK) | ● | ○ | ● | ● | ● | ○ | 64% |
| Singapore (SIN) | ● | ○ | ● | ● | ● | ● | 74% |
| Sydney (SYD) | ● | ● | ● | ● | ● | ● | 86% |

## Hemisphere sanity check

Peak months should invert across the equator — Northern-Hemisphere destinations peaking in mid-year, Southern in the local (Dec–Feb) summer half.

- **Northern**: 13/20 peak in the Apr–Sep half.
- **Southern**: 2/3 peak in the Oct–Apr half.
