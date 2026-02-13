"""
API Operations Module for Gmail Organizer v2
==============================================
Gmail API operations with token bucket rate limiter
and exponential backoff retry logic.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any, Callable, Dict, List, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

from .config import GmailOrganizerConfig
from .utils import C


# ---------------------------------------------------------------------------
# Token Bucket Rate Limiter
# ---------------------------------------------------------------------------
class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for API calls.
    Thread-safe with burst support.
    """

    def __init__(self, rate: float = 10.0, capacity: float = 12.0):
        self.rate = rate
        self.capacity = capacity
        self._tokens = capacity
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self, tokens: float = 1.0) -> float:
        """Acquire tokens, blocking if necessary. Returns wait time."""
        waited = 0.0
        while True:
            with self._lock:
                self._refill()
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return waited
                deficit = tokens - self._tokens
                wait_time = deficit / self.rate
            time.sleep(wait_time)
            waited += wait_time

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
        self._last_refill = now

    @property
    def available_tokens(self) -> float:
        with self._lock:
            self._refill()
            return self._tokens


# ---------------------------------------------------------------------------
# API Call with Exponential Backoff
# ---------------------------------------------------------------------------
def api_call_with_backoff(
    func: Callable,
    *args: Any,
    max_retries: int = 7,
    base_delay: float = 1.0,
    rate_limiter: Optional[TokenBucketRateLimiter] = None,
    logger: Optional[logging.Logger] = None,
    **kwargs: Any,
) -> Any:
    """Execute an API call with exponential backoff on rate-limit errors."""
    _logger = logger or logging.getLogger(__name__)

    if rate_limiter:
        rate_limiter.acquire()

    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except HttpError as e:
            status = e.resp.status if hasattr(e, "resp") else 0
            if status in (429, 500, 503):
                delay = base_delay * (2 ** attempt)
                _logger.warning(
                    f"API error (HTTP {status}). "
                    f"Retry {attempt + 1}/{max_retries} in {delay:.1f}s..."
                )
                time.sleep(delay)
            else:
                raise
        except ConnectionError as e:
            delay = base_delay * (2 ** attempt)
            _logger.warning(f"Connection error: {e}. Retry {attempt + 1}/{max_retries}...")
            time.sleep(delay)

    raise RuntimeError(f"API call failed after {max_retries} retries")


# ---------------------------------------------------------------------------
# Gmail API Operations
# ---------------------------------------------------------------------------
class GmailOperations:
    """Encapsulates Gmail API operations with rate limiting."""

    def __init__(
        self,
        credentials: Credentials,
        config: Optional[GmailOrganizerConfig] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.config = config or GmailOrganizerConfig()
        self.logger = logger or logging.getLogger(__name__)
        self.service = build("gmail", "v1", credentials=credentials)
        self.rate_limiter = TokenBucketRateLimiter(
            rate=self.config.api_calls_per_second,
            capacity=self.config.api_calls_per_second + 2,
        )

    def _call(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """Rate-limited API call with backoff."""
        return api_call_with_backoff(
            func, *args,
            max_retries=self.config.max_retries,
            base_delay=self.config.base_delay,
            rate_limiter=self.rate_limiter,
            logger=self.logger,
            **kwargs,
        )

    def list_labels(self) -> Dict[str, str]:
        """Return dict mapping label name -> label id."""
        results = self._call(
            self.service.users().labels().list(userId="me").execute
        )
        labels = results.get("labels", [])
        return {lbl["name"]: lbl["id"] for lbl in labels}

    def list_labels_full(self) -> List[Dict[str, Any]]:
        """Return full label objects list."""
        results = self._call(
            self.service.users().labels().list(userId="me").execute
        )
        return results.get("labels", [])

    def create_label(self, name: str) -> Dict[str, Any]:
        """Create a label and return the result."""
        body = {
            "name": name,
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show",
        }
        return self._call(
            self.service.users().labels().create(
                userId="me", body=body
            ).execute
        )

    def get_label_info(self, label_id: str) -> Dict[str, Any]:
        """Get detailed info for a label."""
        return self._call(
            self.service.users().labels().get(
                userId="me", id=label_id
            ).execute
        )

    def delete_label(self, label_id: str) -> None:
        """Delete a label."""
        self._call(
            self.service.users().labels().delete(
                userId="me", id=label_id
            ).execute
        )

    def list_messages(
        self,
        label_ids: Optional[List[str]] = None,
        max_results: int = 100,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List messages with optional label filter."""
        kwargs: Dict[str, Any] = {
            "userId": "me",
            "maxResults": max_results,
        }
        if label_ids:
            kwargs["labelIds"] = label_ids
        if page_token:
            kwargs["pageToken"] = page_token

        return self._call(
            self.service.users().messages().list(**kwargs).execute
        )

    def get_message(
        self,
        message_id: str,
        format: str = "metadata",
        metadata_headers: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get a message by ID."""
        kwargs: Dict[str, Any] = {
            "userId": "me",
            "id": message_id,
            "format": format,
        }
        if metadata_headers:
            kwargs["metadataHeaders"] = metadata_headers

        return self._call(
            self.service.users().messages().get(**kwargs).execute
        )

    def modify_message(
        self,
        message_id: str,
        add_label_ids: Optional[List[str]] = None,
        remove_label_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Modify labels on a message."""
        body = {
            "addLabelIds": add_label_ids or [],
            "removeLabelIds": remove_label_ids or [],
        }
        return self._call(
            self.service.users().messages().modify(
                userId="me", id=message_id, body=body
            ).execute
        )
