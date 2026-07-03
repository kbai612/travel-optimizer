"""Tests for the date-window logic that decides which history each source pulls.

These are the functions most likely to break silently at year/month boundaries
(off-by-one in the climate window, or December wrap-around in the OpenSky
sampler), so they're pinned against fixed reference dates rather than today's.
"""

import datetime as dt

from extract.open_meteo import climate_year_range
from extract.opensky import monthly_sample_windows


def test_climate_year_range_is_last_three_complete_years() -> None:
    # A run in mid-2026 should cover the last three *complete* calendar years.
    assert climate_year_range(dt.date(2026, 7, 3)) == (2023, 2025)


def test_climate_year_range_on_jan_1_still_excludes_current_year() -> None:
    # Jan 1st is still an incomplete current year, so it's excluded.
    assert climate_year_range(dt.date(2026, 1, 1)) == (2023, 2025)


def test_climate_year_range_spans_exactly_three_years() -> None:
    start, end = climate_year_range(dt.date(2030, 12, 31))
    assert end - start == 2


def test_monthly_sample_windows_returns_twelve_two_day_windows() -> None:
    windows = monthly_sample_windows(dt.date(2026, 7, 3))
    assert len(windows) == 12
    for start, end in windows:
        assert (end - start) == dt.timedelta(days=2)


def test_monthly_sample_windows_are_chronological_and_trailing() -> None:
    today = dt.date(2026, 7, 3)
    windows = monthly_sample_windows(today)
    starts = [s for s, _ in windows]
    # Strictly increasing, and the whole span is in the trailing 12 months.
    assert starts == sorted(starts)
    assert all(s < today for s in starts)
    assert starts[0] >= today - dt.timedelta(days=366)


def test_monthly_sample_windows_wrap_across_year_boundary() -> None:
    # A January run must reach back into the previous year without a month-0 crash.
    windows = monthly_sample_windows(dt.date(2026, 1, 15))
    years = {s.year for s, _ in windows}
    assert years == {2025}
    assert all(1 <= s.month <= 12 for s, _ in windows)
