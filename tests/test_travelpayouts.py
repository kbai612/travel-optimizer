"""Tests for the Travelpayouts extractor's month-window helper and the calendar
(daily-price) bronze->silver flattening."""

import json
from datetime import date

from extract.travelpayouts import _upcoming_months


def test_upcoming_months_returns_ascending_yyyy_mm_from_today() -> None:
    months = _upcoming_months(6, today=date(2026, 7, 3))
    assert months == ["2026-07", "2026-08", "2026-09", "2026-10", "2026-11", "2026-12"]


def test_upcoming_months_rolls_over_year_boundary() -> None:
    months = _upcoming_months(4, today=date(2026, 11, 15))
    assert months == ["2026-11", "2026-12", "2027-01", "2027-02"]


def test_flatten_price_daily_round_trips_snapshots(tmp_path, monkeypatch) -> None:
    import warehouse.load as load

    monkeypatch.setattr(load, "BRONZE_DIR", tmp_path)
    snap_dir = tmp_path / "travelpayouts_calendar" / "LIS"
    snap_dir.mkdir(parents=True)
    (snap_dir / "calendar_2026-07-03.json").write_text(
        json.dumps(
            {
                "origin": "JFK",
                "collected_at": "2026-07-03",
                "days": {"2026-07-01": 412.0, "2026-07-02": 388.5},
            }
        )
    )

    df = load.flatten_price_daily()

    assert list(df.columns) == ["iata", "origin", "depart_date", "price", "collected_at"]
    assert len(df) == 2
    assert set(df["iata"]) == {"LIS"}
    assert set(df["origin"]) == {"JFK"}
    assert set(df["collected_at"]) == {"2026-07-03"}
    assert sorted(df["depart_date"]) == ["2026-07-01", "2026-07-02"]
    assert df.loc[df["depart_date"] == "2026-07-01", "price"].iloc[0] == 412.0
