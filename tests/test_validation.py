"""Tests for the external-reference score validation (report.validation)."""

from report.validation import _adjacent_months, validate, validate_destination


def _flat(score: float) -> dict[int, float]:
    return {m: score for m in range(1, 13)}


def test_adjacent_months_wraps_around_year() -> None:
    # January's neighbours include December; December's include January.
    assert _adjacent_months({1}) == {12, 1, 2}
    assert _adjacent_months({12}) == {11, 12, 1}


def test_directional_ok_when_recommended_months_score_higher() -> None:
    scores = _flat(50.0)
    for m in (6, 7, 8):  # boost the recommended Reykjavik window
        scores[m] = 90.0
    result = validate_destination("KEF", scores)
    assert result.directional_ok is True
    assert result.margin > 0
    assert result.top_in_window is True
    assert result.top_adjacent is True


def test_directional_fails_when_offseason_scores_higher() -> None:
    scores = _flat(50.0)
    scores[1] = 99.0  # January is outside Reykjavik's Jun–Aug window
    result = validate_destination("KEF", scores)
    assert result.directional_ok is False
    assert result.top_in_window is False
    assert result.top_adjacent is False


def test_top_adjacent_but_not_in_window() -> None:
    # BKK window is {11,12,1,2}; a March peak is adjacent to Feb but not inside.
    scores = _flat(50.0)
    scores[3] = 80.0
    result = validate_destination("BKK", scores)
    assert result.top_in_window is False
    assert result.top_adjacent is True


def test_validate_skips_destinations_without_a_reference() -> None:
    summary = validate({"KEF": _flat(50.0), "ZZZ": _flat(99.0)})
    assert summary.n == 1
    assert summary.results[0].iata == "KEF"


def test_summary_aggregates_hits_and_margin() -> None:
    good = _flat(50.0)
    for m in (6, 7, 8):
        good[m] = 90.0
    bad = _flat(50.0)
    bad[1] = 99.0
    summary = validate({"KEF": good, "GIG": bad})
    assert summary.n == 2
    assert summary.directional_hits == 1
    assert summary.top_in_window_hits == 1
    assert isinstance(summary.mean_margin, float)
