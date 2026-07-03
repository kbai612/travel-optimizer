"""External ground truth for validating the travel score.

The score is a heuristic blend, so on its own it's unfalsifiable — it produces a
number whether or not that number is any good. To check it against something
*outside* the pipeline, this module encodes the conventionally-recommended
"best time to visit" window for each destination, drawn from mainstream travel
guidance (peak/shoulder-season consensus), independent of any signal the model
uses. `report.validation` then measures how well the model's month-by-month
scores line up with these windows.

These windows are deliberately opinionated and static; they are a sanity check,
not a target to optimize toward. Where the model disagrees with them, that's a
finding to explain (see the known formula artifacts in README), not necessarily
a bug to fix.
"""

# month numbers (1-12) widely recommended as the best time to visit, per
# destination IATA, with the one-line rationale behind each window.
RECOMMENDED_MONTHS: dict[str, set[int]] = {
    "LIS": {3, 4, 5, 6, 9, 10},        # spring + early-autumn shoulder; summer is hot & crowded
    "HND": {3, 4, 5, 10, 11},          # cherry-blossom spring + autumn foliage; June is rainy season
    "JFK": {4, 5, 6, 9, 10},           # late-spring + autumn; avoids humid August and January cold
    "CPT": {1, 2, 3, 4, 11, 12},       # Southern-Hemisphere summer + autumn; warm, dry, low wind
    "BKK": {11, 12, 1, 2},             # cool, dry season; avoids monsoon and April heat
    "SYD": {2, 3, 4, 10, 11, 12},      # late-summer + autumn + spring; warm without midsummer extremes
    "KEF": {6, 7, 8},                  # short Icelandic summer; long daylight, mildest temps
    "GIG": {5, 6, 7, 8, 9, 10},        # dry season (Southern winter); lower humidity and rainfall
}

RATIONALE: dict[str, str] = {
    "LIS": "spring & early-autumn shoulder season",
    "HND": "cherry-blossom spring & autumn foliage",
    "JFK": "late spring & crisp autumn",
    "CPT": "Southern-Hemisphere summer & autumn",
    "BKK": "cool, dry season",
    "SYD": "late summer, autumn & spring",
    "KEF": "the short Icelandic summer",
    "GIG": "the dry Southern-Hemisphere winter",
}
