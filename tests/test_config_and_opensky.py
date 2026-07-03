"""Tests for config loading, bronze-path construction, and the OpenSky
already-fetched guard (_has_data) that makes re-runs idempotent."""

import json

from extract.config import Destination, load_destinations
from extract.opensky import _has_data


def test_load_destinations_parses_the_shipped_config() -> None:
    destinations = load_destinations()
    assert len(destinations) >= 1
    assert all(isinstance(d, Destination) for d in destinations)
    # IATA codes must be unique — they key every bronze path and warehouse row.
    iatas = [d.iata for d in destinations]
    assert len(iatas) == len(set(iatas))


def test_bronze_path_layout_and_creates_parents(tmp_path, monkeypatch) -> None:
    import extract.config as config

    monkeypatch.setattr(config, "BRONZE_DIR", tmp_path)
    path = config.bronze_path("open_meteo", "LIS", "2023_2025.json")
    assert path == tmp_path / "open_meteo" / "LIS" / "2023_2025.json"
    assert path.parent.is_dir()  # parents created eagerly


def test_has_data_false_for_missing_file(tmp_path) -> None:
    assert _has_data(tmp_path / "nope.json") is False


def test_has_data_false_for_empty_window(tmp_path) -> None:
    # A landed-but-empty window (no flights) must not count as "already fetched",
    # otherwise a rate-limited zero-flight write would poison the re-run logic.
    path = tmp_path / "empty.json"
    path.write_text(json.dumps({"arrivals": [], "departures": []}))
    assert _has_data(path) is False


def test_has_data_true_when_flights_present(tmp_path) -> None:
    path = tmp_path / "real.json"
    path.write_text(json.dumps({"arrivals": [{"icao24": "abc"}], "departures": []}))
    assert _has_data(path) is True


def test_has_data_false_on_corrupt_json(tmp_path) -> None:
    path = tmp_path / "corrupt.json"
    path.write_text("{not json")
    assert _has_data(path) is False
