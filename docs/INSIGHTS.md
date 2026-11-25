# Findings

<!-- GENERATED FILE — do not edit by hand. -->
<!-- Regenerate with: uv run python -m report.insights -->

_Auto-generated from `warehouse.duckdb` on 2026-11-25 17:56 UTC, covering 23 destinations × 12 months. Numbers reflect whatever real data the warehouse currently holds (coverage varies by source — see the coverage table below)._

## Does the score match conventional wisdom?

An external check: for each destination, the model's monthly scores are compared against the *conventionally-recommended* time to visit (mainstream travel-guide consensus, encoded in `report/reference.py`) — signals the model never sees. This is a sanity check, not a target the model is tuned toward.

- **Directional agreement:** for **7/8** destinations the recommended months average a higher travel score than the rest of the year (mean margin **+4.2** points).
- **Peak month in the recommended window:** **6/8** (exact), rising to **8/8** allowing a ±1-month tolerance.

| Destination | Recommended window | Rec. avg | Off-season avg | Margin | Peak month |
|---|---|---:|---:|---:|---|
| Bangkok (BKK) | cool, dry season | 74.9 | 72.9 | +2.0 | Nov ✅ |
| Cape Town (CPT) | Southern-Hemisphere summer & autumn | 63.5 | 59.8 | +3.7 | Feb ✅ |
| Rio de Janeiro (GIG) | the dry Southern-Hemisphere winter | 66.8 | 63.1 | +3.7 | Aug ✅ |
| Tokyo (HND) | cherry-blossom spring & autumn foliage | 71.2 | 71.7 | -0.5 | Jun ≈ |
| New York (JFK) | late spring & crisp autumn | 72.5 | 65.8 | +6.6 | Aug ≈ |
| Reykjavik (KEF) | the short Icelandic summer | 71.3 | 60.4 | +10.9 | Jul ✅ |
| Lisbon (LIS) | spring & early-autumn shoulder season | 77.2 | 73.1 | +4.1 | Sep ✅ |
| Sydney (SYD) | late summer, autumn & spring | 75.7 | 72.6 | +3.1 | Feb ✅ |

Where the model diverges it's explainable rather than random: Tokyo's peak lands in June because the weather-comfort formula weights mild temperature above the rainy-season precipitation penalty, and Lisbon skews to peak summer because the model optimizes weather comfort over the crowd-avoidance that drives the shoulder-season guidance. Both are documented limitations in the README, surfaced here by the validation rather than hidden by it.

## Best month, by destination

| Destination | Top month | Score | Confidence | Leading real signal |
|---|---|---|---|---|
| Amsterdam (AMS) | Sep | 66.9 | 70% | few holiday spikes |
| Barcelona (BCN) | Aug | 68.9 | 80% | warm seas |
| Bangkok (BKK) | Nov | 77.7 | 58% | good fares |
| Paris (CDG) | Aug | 67.5 | 70% | good fares |
| Cape Town (CPT) | Feb | 71.2 | 80% | good fares |
| Cancun (CUN) | Feb | 82.7 | 80% | good fares |
| Bali (DPS) | Jul | 70.9 | 80% | few holiday spikes |
| Dubai (DXB) | Jan | 49.4 | 68% | good fares |
| Buenos Aires (EZE) | Nov | 79.9 | 70% | good fares |
| Rome (FCO) | Sep | 74.5 | 80% | good fares |
| Rio de Janeiro (GIG) | Aug | 69.8 | 80% | few holiday spikes |
| Hong Kong (HKG) | Nov | 70.9 | 80% | good fares |
| Tokyo (HND) | Jun | 80.3 | 80% | few holiday spikes |
| Honolulu (HNL) | Sep | 82.6 | 80% | good fares |
| Istanbul (IST) | Sep | 73.7 | 80% | few holiday spikes |
| New York (JFK) | Aug | 84.7 | 80% | good fares |
| Reykjavik (KEF) | Jul | 74.4 | 80% | few holiday spikes |
| Los Angeles (LAX) | Sep | 81.6 | 80% | good fares |
| London (LHR) | Sep | 68.1 | 70% | good fares |
| Lisbon (LIS) | Sep | 83.8 | 80% | few holiday spikes |
| Marrakesh (RAK) | Mar | 69.0 | 70% | good fares |
| Singapore (SIN) | Sep | 80.6 | 80% | good fares |
| Sydney (SYD) | Feb | 85.1 | 80% | good fares |

## Signal coverage

Which signals are backed by real data vs. a neutral model default, per destination (● real · ○ default). `data_confidence` is the weight-weighted share of the score backed by real data.

| Destination | Weather | Demand | Price | Holiday | Air quality | Sea temp | Confidence |
|---|---|---|---|---|---|---|---|
| Amsterdam (AMS) | ● | ○ | ● | ● | ● | ○ | 70% |
| Barcelona (BCN) | ● | ○ | ● | ● | ● | ● | 80% |
| Bangkok (BKK) | ● | ○ | ● | ○ | ● | ○ | 58% |
| Paris (CDG) | ● | ○ | ● | ● | ● | ○ | 70% |
| Cape Town (CPT) | ● | ○ | ● | ● | ● | ● | 74% |
| Cancun (CUN) | ● | ○ | ● | ● | ● | ● | 80% |
| Bali (DPS) | ● | ○ | ● | ● | ● | ● | 79% |
| Dubai (DXB) | ● | ○ | ● | ○ | ● | ● | 66% |
| Buenos Aires (EZE) | ● | ○ | ● | ● | ● | ○ | 68% |
| Rome (FCO) | ● | ○ | ● | ● | ● | ● | 80% |
| Rio de Janeiro (GIG) | ● | ○ | ● | ● | ● | ● | 79% |
| Hong Kong (HKG) | ● | ○ | ● | ● | ● | ● | 79% |
| Tokyo (HND) | ● | ○ | ● | ● | ● | ● | 80% |
| Honolulu (HNL) | ● | ○ | ● | ● | ● | ● | 76% |
| Istanbul (IST) | ● | ○ | ● | ● | ● | ● | 80% |
| New York (JFK) | ● | ○ | ● | ● | ● | ● | 80% |
| Reykjavik (KEF) | ● | ○ | ● | ● | ● | ● | 80% |
| Los Angeles (LAX) | ● | ○ | ● | ● | ● | ● | 79% |
| London (LHR) | ● | ○ | ● | ● | ● | ○ | 70% |
| Lisbon (LIS) | ● | ○ | ● | ● | ● | ● | 80% |
| Marrakesh (RAK) | ● | ○ | ● | ● | ● | ○ | 66% |
| Singapore (SIN) | ● | ○ | ● | ● | ● | ● | 74% |
| Sydney (SYD) | ● | ○ | ● | ● | ● | ● | 76% |

## Hemisphere sanity check

Peak months should invert across the equator — Northern-Hemisphere destinations peaking in mid-year, Southern in the local (Dec–Feb) summer half.

- **Northern**: 14/20 peak in the Apr–Sep half.
- **Southern**: 2/3 peak in the Oct–Apr half.
