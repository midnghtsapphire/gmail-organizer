"""Tests for gmail_organizer.operations module."""

import time
import threading
import pytest
from unittest.mock import MagicMock, patch

from gmail_organizer.operations import (
    TokenBucketRateLimiter,
    api_call_with_backoff,
    GmailOperations,
)
from gmail_organizer.config import GmailOrganizerConfig


class TestTokenBucketRateLimiter:
    def test_initial_capacity(self):
        limiter = TokenBucketRateLimiter(rate=10.0, capacity=10.0)
        assert limiter.available_tokens <= 10.0

    def test_acquire(self):
        limiter = TokenBucketRateLimiter(rate=100.0, capacity=10.0)
        waited = limiter.acquire(1.0)
        assert waited >= 0

    def test_refill(self):
        limiter = TokenBucketRateLimiter(rate=1000.0, capacity=10.0)
        limiter.acquire(10.0)
        time.sleep(0.02)
        assert limiter.available_tokens > 0

    def test_thread_safety(self):
        limiter = TokenBucketRateLimiter(rate=100.0, capacity=100.0)
        errors = []
        def work():
            try:
                for _ in range(10):
                    limiter.acquire(0.1)
            except Exception as e:
                errors.append(e)
        threads = [threading.Thread(target=work) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(errors) == 0


class TestApiCallWithBackoff:
    def test_success(self):
        func = MagicMock(return_value="ok")
        assert api_call_with_backoff(func, max_retries=3, base_delay=0.01) == "ok"

    def test_retry_429(self):
        mock_resp = MagicMock()
        mock_resp.status = 429
        from googleapiclient.errors import HttpError
        err = HttpError(mock_resp, b"rate limit")
        func = MagicMock(side_effect=[err, "ok"])
        assert api_call_with_backoff(func, max_retries=3, base_delay=0.01) == "ok"

    def test_no_retry_403(self):
        mock_resp = MagicMock()
        mock_resp.status = 403
        from googleapiclient.errors import HttpError
        err = HttpError(mock_resp, b"forbidden")
        func = MagicMock(side_effect=err)
        with pytest.raises(HttpError):
            api_call_with_backoff(func, max_retries=3, base_delay=0.01)

    def test_exhausted_retries(self):
        mock_resp = MagicMock()
        mock_resp.status = 503
        from googleapiclient.errors import HttpError
        err = HttpError(mock_resp, b"unavailable")
        func = MagicMock(side_effect=err)
        with pytest.raises(RuntimeError):
            api_call_with_backoff(func, max_retries=2, base_delay=0.01)

    def test_connection_error(self):
        func = MagicMock(side_effect=[ConnectionError("timeout"), "ok"])
        assert api_call_with_backoff(func, max_retries=3, base_delay=0.01) == "ok"


class TestGmailOperations:
    @patch("gmail_organizer.operations.build")
    def test_init(self, mock_build):
        creds = MagicMock()
        ops = GmailOperations(creds)
        mock_build.assert_called_once()

    @patch("gmail_organizer.operations.build")
    def test_list_labels(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_users = mock_service.users.return_value
        mock_labels = mock_users.labels.return_value
        mock_list = mock_labels.list.return_value
        mock_list.execute.return_value = {
            "labels": [
                {"name": "INBOX", "id": "INBOX"},
                {"name": "SENT", "id": "SENT"},
            ]
        }
        creds = MagicMock()
        ops = GmailOperations(creds)
        labels = ops.list_labels()
        assert "INBOX" in labels

    @patch("gmail_organizer.operations.build")
    def test_create_label(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_users = mock_service.users.return_value
        mock_labels = mock_users.labels.return_value
        mock_create = mock_labels.create.return_value
        mock_create.execute.return_value = {"id": "new_id", "name": "TEST"}

        creds = MagicMock()
        ops = GmailOperations(creds)
        result = ops.create_label("TEST")
        assert result["id"] == "new_id"

    @patch("gmail_organizer.operations.build")
    def test_modify_message(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_users = mock_service.users.return_value
        mock_msgs = mock_users.messages.return_value
        mock_modify = mock_msgs.modify.return_value
        mock_modify.execute.return_value = {"id": "msg_1"}

        creds = MagicMock()
        ops = GmailOperations(creds)
        result = ops.modify_message("msg_1", add_label_ids=["lbl_1"])
        assert result["id"] == "msg_1"
