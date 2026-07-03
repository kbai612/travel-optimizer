"""Shared HTTP client: exponential-backoff retries, 429 handling, JSON helpers.

Every extractor module (open_meteo, nager, opensky, travelpayouts) calls through
`get_json` / `post_json` instead of using httpx directly, so retry and
rate-limit behavior is consistent across all four API sources.
"""

import logging
import time
from typing import Any

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30.0


class ApiError(RuntimeError):
    """Raised when an API call fails after exhausting retries."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, httpx.TransportError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        return status == 429 or status >= 500
    return False


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=30),
    retry=retry_if_exception(_is_retryable),
    reraise=True,
)
def _request(client: httpx.Client, method: str, url: str, **kwargs) -> httpx.Response:
    response = client.request(method, url, **kwargs)
    if response.status_code == 429:
        retry_after = float(response.headers.get("Retry-After", 5))
        logger.warning("429 rate limited on %s, sleeping %.1fs", url, retry_after)
        time.sleep(retry_after)
    response.raise_for_status()
    return response


def _to_json(client: httpx.Client, method: str, url: str, **kwargs) -> Any:
    try:
        response = _request(client, method, url, **kwargs)
    except httpx.HTTPStatusError as exc:
        body = exc.response.text[:200]
        raise ApiError(
            f"{method} {url} failed: {exc.response.status_code} {body}",
            status_code=exc.response.status_code,
        ) from exc
    except httpx.TransportError as exc:
        raise ApiError(f"{method} {url} failed: {exc}") from exc
    if not response.content:
        return None
    try:
        return response.json()
    except ValueError as exc:
        raise ApiError(f"{method} {url} returned non-JSON body: {exc}") from exc


def get_json(client: httpx.Client, url: str, **kwargs) -> Any:
    """GET a URL and return parsed JSON, retrying transient failures with backoff."""
    return _to_json(client, "GET", url, **kwargs)


def post_json(client: httpx.Client, url: str, **kwargs) -> Any:
    """POST to a URL and return parsed JSON, retrying transient failures with backoff."""
    return _to_json(client, "POST", url, **kwargs)


def new_client(headers: dict | None = None, auth: tuple[str, str] | None = None) -> httpx.Client:
    return httpx.Client(timeout=DEFAULT_TIMEOUT, headers=headers or {}, auth=auth)
