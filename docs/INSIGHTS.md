# Findings

<!-- GENERATED FILE — do not edit by hand. -->
<!-- Regenerate with: uv run python -m report.insights -->

_Auto-generated from `warehouse.duckdb` on 2026-07-05 11:00 UTC, covering 23 destinations × 12 months. Numbers reflect whatever real data the warehouse currently holds (coverage varies by source — see the coverage table below)._

## Does the score match conventional wisdom?

An external check: for each destination, the model's monthly scores are compared against the *conventionally-recommended* time to visit (mainstream travel-guide consensus, encoded in `report/reference.py`) — signals the model never sees. This is a sanity check, not a target the model is tuned toward.

- **Directional agreement:** for **6/8** destinations the recommended months average a higher travel score than the rest of the year (mean margin **+4.2** points).
- **Peak month in the recommended window:** **6/8** (exact), rising to **8/8** allowing a ±1-month tolerance.

| Destination | Recommended window | Rec. avg | Off-season avg | Margin | Peak month |
|---|---|---:|---:|---:|---|
| Bangkok (BKK) | cool, dry season | 58.6 | 59.4 | -0.8 | Dec ✅ |
| Cape Town (CPT) | Southern-Hemisphere summer & autumn | 60.3 | 57.4 | +2.8 | Oct ≈ |
| Rio de Janeiro (GIG) | the dry Southern-Hemisphere winter | 64.2 | 58.0 | +6.2 | Aug ✅ |
| Tokyo (HND) | cherry-blossom spring & autumn foliage | 67.6 | 69.4 | -1.8 | Jun ≈ |
| New York (JFK) | late spring & crisp autumn | 69.0 | 60.9 | +8.1 | Sep ✅ |
| Reykjavik (KEF) | the short Icelandic summer | 68.2 | 52.0 | +16.2 | Jul ✅ |
| Lisbon (LIS) | spring & early-autumn shoulder season | 71.8 | 70.9 | +0.8 | Sep ✅ |
| Sydney (SYD) | late summer, autumn & spring | 70.4 | 68.2 | +2.2 | Dec ✅ |

Where the model diverges it's explainable rather than random: Tokyo's peak lands in June because the weather-comfort formula weights mild temperature above the rainy-season precipitation penalty, and Lisbon skews to peak summer because the model optimizes weather comfort over the crowd-avoidance that drives the shoulder-season guidance. Both are documented limitations in the README, surfaced here by the validation rather than hidden by it.

## Best month, by destination

| Destination | Top month | Score | Confidence | Leading real signal |
|---|---|---|---|---|
| Amsterdam (AMS) | Aug | 69.4 | 70% | good fares |
| Barcelona (BCN) | Aug | 70.0 | 80% | good fares |
| Bangkok (BKK) | Dec | 64.4 | 58% | mild weather |
| Paris (CDG) | Sep | 68.7 | 70% | good fares |
| Cape Town (CPT) | Oct | 68.6 | 80% | good fares |
| Cancun (CUN) | Feb | 82.7 | 80% | good fares |
| Bali (DPS) | Jul | 71.0 | 80% | good fares |
| Dubai (DXB) | Dec | 49.8 | 68% | mild weather |
| Buenos Aires (EZE) | Sep | 79.7 | 70% | good fares |
| Rome (FCO) | Sep | 74.4 | 80% | few holiday spikes |
| Rio de Janeiro (GIG) | Aug | 69.4 | 80% | few holiday spikes |
| Hong Kong (HKG) | Aug | 66.1 | 80% | good fares |
| Tokyo (HND) | Jun | 79.3 | 80% | few holiday spikes |
| Honolulu (HNL) | Aug | 85.6 | 80% | good fares |
| Istanbul (IST) | Sep | 74.2 | 80% | good fares |
| New York (JFK) | Sep | 82.2 | 80% | good fares |
| Reykjavik (KEF) | Jul | 75.1 | 80% | good fares |
| Los Angeles (LAX) | Sep | 81.6 | 80% | good fares |
| London (LHR) | Sep | 67.7 | 70% | few holiday spikes |
| Lisbon (LIS) | Sep | 84.4 | 80% | good fares |
| Marrakesh (RAK) | Oct | 63.2 | 52% | few holiday spikes |
| Singapore (SIN) | Oct | 76.9 | 80% | good fares |
| Sydney (SYD) | Dec | 78.6 | 80% | good fares |

## Signal coverage

Which signals are backed by real data vs. a neutral model default, per destination (● real · ○ default). `data_confidence` is the weight-weighted share of the score backed by real data.

| Destination | Weather | Demand | Price | Holiday | Air quality | Sea temp | Confidence |
|---|---|---|---|---|---|---|---|
| Amsterdam (AMS) | ● | ○ | ● | ● | ● | ○ | 61% |
| Barcelona (BCN) | ● | ○ | ● | ● | ● | ● | 66% |
| Bangkok (BKK) | ● | ○ | ● | ○ | ● | ○ | 48% |
| Paris (CDG) | ● | ○ | ● | ● | ● | ○ | 61% |
| Cape Town (CPT) | ● | ○ | ● | ● | ● | ● | 65% |
| Cancun (CUN) | ● | ○ | ● | ● | ● | ● | 71% |
| Bali (DPS) | ● | ○ | ● | ● | ● | ● | 64% |
| Dubai (DXB) | ● | ○ | ● | ○ | ● | ● | 56% |
| Buenos Aires (EZE) | ● | ○ | ● | ● | ● | ○ | 58% |
| Rome (FCO) | ● | ○ | ● | ● | ● | ● | 70% |
| Rio de Janeiro (GIG) | ● | ○ | ● | ● | ● | ● | 68% |
| Hong Kong (HKG) | ● | ○ | ● | ● | ● | ● | 70% |
| Tokyo (HND) | ● | ○ | ● | ● | ● | ● | 74% |
| Honolulu (HNL) | ● | ○ | ● | ● | ● | ● | 68% |
| Istanbul (IST) | ● | ○ | ● | ● | ● | ● | 72% |
| New York (JFK) | ● | ○ | ● | ● | ● | ● | 70% |
| Reykjavik (KEF) | ● | ○ | ● | ● | ● | ● | 65% |
| Los Angeles (LAX) | ● | ○ | ● | ● | ● | ● | 68% |
| London (LHR) | ● | ○ | ● | ● | ● | ○ | 60% |
| Lisbon (LIS) | ● | ○ | ● | ● | ● | ● | 71% |
| Marrakesh (RAK) | ● | ○ | ○ | ● | ● | ○ | 52% |
| Singapore (SIN) | ● | ○ | ● | ● | ● | ● | 64% |
| Sydney (SYD) | ● | ○ | ● | ● | ● | ● | 65% |

## Hemisphere sanity check

Peak months should invert across the equator — Northern-Hemisphere destinations peaking in mid-year, Southern in the local (Dec–Feb) summer half.

- **Northern**: 15/20 peak in the Apr–Sep half.
- **Southern**: 2/3 peak in the Oct–Apr half.
