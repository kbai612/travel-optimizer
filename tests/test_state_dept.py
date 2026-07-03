"""Tests for State Department advisory-title parsing.

The feed has no reliable per-entry ISO code, so parse_advisory scrapes the
country name + level out of a free-text title and maps it against the tracked
countries. That name-matching is the fragile part of the whole advisory signal.
"""

import pytest

from extract.state_dept import COUNTRY_NAME_TO_CODE, parse_advisory


@pytest.mark.parametrize(
    "title,expected",
    [
        ("Portugal - Level 1: Exercise Normal Precautions", ("PT", 1)),
        ("Japan - Level 2: Exercise Increased Caution", ("JP", 2)),
        ("South Africa - Level 3: Reconsider Travel", ("ZA", 3)),
        # Case/spacing shouldn't matter — the regex and lookup are normalized.
        ("brazil-level 4:do not travel", ("BR", 4)),
        ("Iceland   -   Level 1 : Exercise Normal Precautions", ("IS", 1)),
    ],
)
def test_parse_advisory_extracts_country_and_level(title, expected) -> None:
    assert parse_advisory({"Title": title}) == expected


def test_parse_advisory_ignores_untracked_countries() -> None:
    # A country absent from COUNTRY_NAME_TO_CODE must be dropped, not guessed. The
    # guard keeps this example genuinely untracked — if Germany is ever added, this
    # fails loudly (pick another example) instead of the parse silently succeeding.
    assert "germany" not in COUNTRY_NAME_TO_CODE
    assert parse_advisory({"Title": "Germany - Level 2: Exercise Increased Caution"}) is None


@pytest.mark.parametrize(
    "title",
    [
        "",
        "Worldwide Caution",
        "Portugal Travel Advisory",  # no "Level N:" segment
        "Some Country - Level: Missing Number",
    ],
)
def test_parse_advisory_returns_none_on_unparseable_titles(title) -> None:
    assert parse_advisory({"Title": title}) is None


def test_parse_advisory_handles_missing_title_key() -> None:
    assert parse_advisory({}) is None
    assert parse_advisory({"Title": None}) is None
