"""Tests for the Travelpayouts extractor's month-window helper and bronze->silver loading."""

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


def test_flatten_price_snapshot_manifest_keeps_empty_snapshots(tmp_path, monkeypatch) -> None:
    import warehouse.load as load

    monkeypatch.setattr(load, "BRONZE_DIR", tmp_path)

    monthly_dir = tmp_path / "travelpayouts" / "LIS"
    monthly_dir.mkdir(parents=True)
    (monthly_dir / "monthly_prices_2026-07-03.json").write_text(
        json.dumps({"origin": "JFK", "collected_at": "2026-07-03", "monthly": {}})
    )

    calendar_dir = tmp_path / "travelpayouts_calendar" / "LIS"
    calendar_dir.mkdir(parents=True)
    (calendar_dir / "calendar_2026-07-03.json").write_text(
        json.dumps({"origin": "JFK", "collected_at": "2026-07-03", "days": {}})
    )

    df = load.flatten_price_snapshot_manifest()

    assert list(df.columns) == ["snapshot_source", "iata", "origin", "collected_at"]
    assert len(df) == 2
    assert set(df["snapshot_source"]) == {"travelpayouts", "travelpayouts_calendar"}
    assert set(df["iata"]) == {"LIS"}
    assert set(df["origin"]) == {"JFK"}
    assert set(df["collected_at"]) == {"2026-07-03"}


def test_price_loaders_skip_legacy_undated_snapshots(tmp_path, monkeypatch) -> None:
    import warehouse.load as load

    monkeypatch.setattr(load, "BRONZE_DIR", tmp_path)

    monthly_dir = tmp_path / "travelpayouts" / "LIS"
    monthly_dir.mkdir(parents=True)
    (monthly_dir / "monthly_prices.json").write_text(
        json.dumps({"origin": "JFK", "monthly": {"2026-08": {"price": 499.0}}})
    )
    (monthly_dir / "monthly_prices_2026-07-03.json").write_text(
        json.dumps(
            {
                "origin": "JFK",
                "collected_at": "2026-07-03",
                "monthly": {"2026-08": {"price": 412.0}},
            }
        )
    )

    calendar_dir = tmp_path / "travelpayouts_calendar" / "LIS"
    calendar_dir.mkdir(parents=True)
    (calendar_dir / "calendar.json").write_text(
        json.dumps({"origin": "JFK", "days": {"2026-07-01": 555.0}})
    )
    (calendar_dir / "calendar_2026-07-03.json").write_text(
        json.dumps(
            {
                "origin": "JFK",
                "collected_at": "2026-07-03",
                "days": {"2026-07-01": 388.5},
            }
        )
    )

    monthly_df = load.flatten_price_monthly()
    daily_df = load.flatten_price_daily()
    manifest_df = load.flatten_price_snapshot_manifest()

    assert len(monthly_df) == 1
    assert monthly_df["price"].iloc[0] == 412.0
    assert set(monthly_df["collected_at"]) == {"2026-07-03"}

    assert len(daily_df) == 1
    assert daily_df["price"].iloc[0] == 388.5
    assert set(daily_df["collected_at"]) == {"2026-07-03"}

    assert len(manifest_df) == 2
    assert set(manifest_df["collected_at"]) == {"2026-07-03"}
