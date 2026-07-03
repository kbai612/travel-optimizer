"""Tests for the shared HTTP client's retry-classification logic.

The retry policy is the one piece of extract/ that every source depends on, so
getting "which failures are worth retrying" right matters across the board.
"""

import httpx
import pytest

from extract.client import _is_retryable


def _status_error(status_code: int) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", "https://example.test/")
    response = httpx.Response(status_code, request=request)
    return httpx.HTTPStatusError("boom", request=request, response=response)


@pytest.mark.parametrize("status", [429, 500, 502, 503, 504])
def test_retryable_statuses(status: int) -> None:
    assert _is_retryable(_status_error(status)) is True


@pytest.mark.parametrize("status", [400, 401, 403, 404, 422])
def test_client_errors_are_not_retryable(status: int) -> None:
    # A 404 or 401 won't fix itself on retry — retrying just wastes quota.
    assert _is_retryable(_status_error(status)) is False


def test_transport_errors_are_retryable() -> None:
    request = httpx.Request("GET", "https://example.test/")
    assert _is_retryable(httpx.ConnectError("no route", request=request)) is True
    assert _is_retryable(httpx.ReadTimeout("slow", request=request)) is True


def test_unrelated_exceptions_are_not_retryable() -> None:
    assert _is_retryable(ValueError("nope")) is False
    assert _is_retryable(KeyError("missing")) is False
