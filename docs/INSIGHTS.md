# Findings

<!-- GENERATED FILE — do not edit by hand. -->
<!-- Regenerate with: uv run python -m report.insights -->

_Auto-generated from `warehouse.duckdb` on 2026-08-29 13:25 UTC, covering 23 destinations × 12 months. Numbers reflect whatever real data the warehouse currently holds (coverage varies by source — see the coverage table below)._

## Does the score match conventional wisdom?

An external check: for each destination, the model's monthly scores are compared against the *conventionally-recommended* time to visit (mainstream travel-guide consensus, encoded in `report/reference.py`) — signals the model never sees. This is a sanity check, not a target the model is tuned toward.

- **Directional agreement:** for **7/8** destinations the recommended months average a higher travel score than the rest of the year (mean margin **+5.3** points).
- **Peak month in the recommended window:** **7/8** (exact), rising to **8/8** allowing a ±1-month tolerance.

| Destination | Recommended window | Rec. avg | Off-season avg | Margin | Peak month |
|---|---|---:|---:|---:|---|
| Bangkok (BKK) | cool, dry season | 76.2 | 71.4 | +4.8 | Dec ✅ |
| Cape Town (CPT) | Southern-Hemisphere summer & autumn | 62.8 | 59.9 | +2.9 | Nov ✅ |
| Rio de Janeiro (GIG) | the dry Southern-Hemisphere winter | 65.7 | 62.3 | +3.4 | Aug ✅ |
| Tokyo (HND) | cherry-blossom spring & autumn foliage | 71.3 | 71.7 | -0.3 | Jun ≈ |
| New York (JFK) | late spring & crisp autumn | 72.2 | 61.1 | +11.1 | Sep ✅ |
| Reykjavik (KEF) | the short Icelandic summer | 71.1 | 56.7 | +14.3 | Jul ✅ |
| Lisbon (LIS) | spring & early-autumn shoulder season | 75.6 | 73.7 | +1.9 | Sep ✅ |
| Sydney (SYD) | late summer, autumn & spring | 75.5 | 71.1 | +4.3 | Feb ✅ |

Where the model diverges it's explainable rather than random: Tokyo's peak lands in June because the weather-comfort formula weights mild temperature above the rainy-season precipitation penalty, and Lisbon skews to peak summer because the model optimizes weather comfort over the crowd-avoidance that drives the shoulder-season guidance. Both are documented limitations in the README, surfaced here by the validation rather than hidden by it.

## Best month, by destination

| Destination | Top month | Score | Confidence | Leading real signal |
|---|---|---|---|---|
| Amsterdam (AMS) | Aug | 68.8 | 70% | few holiday spikes |
| Barcelona (BCN) | Aug | 70.0 | 80% | good fares |
| Bangkok (BKK) | Dec | 78.0 | 58% | good fares |
| Paris (CDG) | Sep | 68.7 | 70% | good fares |
| Cape Town (CPT) | Nov | 70.2 | 80% | good fares |
| Cancun (CUN) | Feb | 82.7 | 80% | good fares |
| Bali (DPS) | Jul | 71.0 | 80% | good fares |
| Dubai (DXB) | Jan | 49.3 | 68% | good fares |
| Buenos Aires (EZE) | Nov | 79.9 | 70% | good fares |
| Rome (FCO) | Sep | 74.5 | 80% | good fares |
| Rio de Janeiro (GIG) | Aug | 68.5 | 80% | few holiday spikes |
| Hong Kong (HKG) | Nov | 70.9 | 80% | good fares |
| Tokyo (HND) | Jun | 80.6 | 80% | few holiday spikes |
| Honolulu (HNL) | Sep | 82.6 | 80% | good fares |
| Istanbul (IST) | Sep | 74.2 | 80% | good fares |
| New York (JFK) | Sep | 82.2 | 80% | good fares |
| Reykjavik (KEF) | Jul | 74.2 | 80% | few holiday spikes |
| Los Angeles (LAX) | Aug | 82.2 | 80% | few holiday spikes |
| London (LHR) | Sep | 68.1 | 70% | good fares |
| Lisbon (LIS) | Sep | 84.4 | 80% | good fares |
| Marrakesh (RAK) | Oct | 70.6 | 70% | few holiday spikes |
| Singapore (SIN) | Sep | 80.6 | 80% | good fares |
| Sydney (SYD) | Feb | 85.2 | 80% | good fares |

## Signal coverage

Which signals are backed by real data vs. a neutral model default, per destination (● real · ○ default). `data_confidence` is the weight-weighted share of the score backed by real data.

| Destination | Weather | Demand | Price | Holiday | Air quality | Sea temp | Confidence |
|---|---|---|---|---|---|---|---|
| Amsterdam (AMS) | ● | ○ | ● | ● | ● | ○ | 64% |
| Barcelona (BCN) | ● | ○ | ● | ● | ● | ● | 77% |
| Bangkok (BKK) | ● | ○ | ● | ○ | ● | ○ | 56% |
| Paris (CDG) | ● | ○ | ● | ● | ● | ○ | 70% |
| Cape Town (CPT) | ● | ○ | ● | ● | ● | ● | 72% |
| Cancun (CUN) | ● | ○ | ● | ● | ● | ● | 79% |
| Bali (DPS) | ● | ○ | ● | ● | ● | ● | 74% |
| Dubai (DXB) | ● | ○ | ● | ○ | ● | ● | 63% |
| Buenos Aires (EZE) | ● | ○ | ● | ● | ● | ○ | 66% |
| Rome (FCO) | ● | ○ | ● | ● | ● | ● | 79% |
| Rio de Janeiro (GIG) | ● | ○ | ● | ● | ● | ● | 77% |
| Hong Kong (HKG) | ● | ○ | ● | ● | ● | ● | 79% |
| Tokyo (HND) | ● | ○ | ● | ● | ● | ● | 80% |
| Honolulu (HNL) | ● | ○ | ● | ● | ● | ● | 71% |
| Istanbul (IST) | ● | ○ | ● | ● | ● | ● | 80% |
| New York (JFK) | ● | ○ | ● | ● | ● | ● | 72% |
| Reykjavik (KEF) | ● | ○ | ● | ● | ● | ● | 74% |
| Los Angeles (LAX) | ● | ○ | ● | ● | ● | ● | 74% |
| London (LHR) | ● | ○ | ● | ● | ● | ○ | 66% |
| Lisbon (LIS) | ● | ○ | ● | ● | ● | ● | 79% |
| Marrakesh (RAK) | ● | ○ | ● | ● | ● | ○ | 57% |
| Singapore (SIN) | ● | ○ | ● | ● | ● | ● | 71% |
| Sydney (SYD) | ● | ○ | ● | ● | ● | ● | 74% |

## Hemisphere sanity check

Peak months should invert across the equator — Northern-Hemisphere destinations peaking in mid-year, Southern in the local (Dec–Feb) summer half.

- **Northern**: 14/20 peak in the Apr–Sep half.
- **Southern**: 2/3 peak in the Oct–Apr half.
