"""Validate the travel score against the external reference in report.reference.

Three complementary checks, from strict to lenient:

  - directional   — do the recommended months average a higher score than the
                    rest of the year? (the model's *shape* agrees with consensus)
  - top-in-window — does the single highest-scoring month fall inside the
                    recommended window? (strict, and fuzzy by nature — "best
                    month" is rarely a single unambiguous answer)
  - top-adjacent  — is the highest-scoring month within one calendar month of
                    the window (wrapping Dec↔Jan)? (tolerant of that fuzziness)

All functions here are pure and operate on plain dicts, so they're unit-tested
without touching DuckDB.
"""

from dataclasses import dataclass

from report.reference import RATIONALE, RECOMMENDED_MONTHS


def _adjacent_months(window: set[int]) -> set[int]:
    """The window plus its immediate neighbours, wrapping around the year."""
    expanded = set(window)
    for m in window:
        expanded.add(12 if m == 1 else m - 1)
        expanded.add(1 if m == 12 else m + 1)
    return expanded


@dataclass
class DestinationResult:
    iata: str
    rationale: str
    recommended_avg: float
    offseason_avg: float
    margin: float
    directional_ok: bool
    top_month: int
    top_in_window: bool
    top_adjacent: bool


def validate_destination(iata: str, scores_by_month: dict[int, float]) -> DestinationResult:
    window = RECOMMENDED_MONTHS[iata]
    rec = [s for m, s in scores_by_month.items() if m in window]
    off = [s for m, s in scores_by_month.items() if m not in window]
    rec_avg = sum(rec) / len(rec) if rec else 0.0
    off_avg = sum(off) / len(off) if off else 0.0
    top_month = max(scores_by_month, key=scores_by_month.get)
    return DestinationResult(
        iata=iata,
        rationale=RATIONALE.get(iata, ""),
        recommended_avg=round(rec_avg, 1),
        offseason_avg=round(off_avg, 1),
        margin=round(rec_avg - off_avg, 1),
        directional_ok=rec_avg > off_avg,
        top_month=top_month,
        top_in_window=top_month in window,
        top_adjacent=top_month in _adjacent_months(window),
    )


@dataclass
class ValidationSummary:
    results: list[DestinationResult]

    @property
    def n(self) -> int:
        return len(self.results)

    @property
    def directional_hits(self) -> int:
        return sum(r.directional_ok for r in self.results)

    @property
    def top_in_window_hits(self) -> int:
        return sum(r.top_in_window for r in self.results)

    @property
    def top_adjacent_hits(self) -> int:
        return sum(r.top_adjacent for r in self.results)

    @property
    def mean_margin(self) -> float:
        if not self.results:
            return 0.0
        return round(sum(r.margin for r in self.results) / len(self.results), 1)


def validate(scores_by_dest: dict[str, dict[int, float]]) -> ValidationSummary:
    """scores_by_dest: {iata: {month: travel_score}} for destinations we have a
    reference window for. Destinations without a reference are skipped."""
    results = [
        validate_destination(iata, scores)
        for iata, scores in sorted(scores_by_dest.items())
        if iata in RECOMMENDED_MONTHS
    ]
    return ValidationSummary(results=results)
