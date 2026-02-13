"""Extended tests for gmail_organizer.operations module — boost coverage."""

import pytest
from unittest.mock import MagicMock, patch

from gmail_organizer.operations import GmailOperations, TokenBucketRateLimiter
from gmail_organizer.config import GmailOrganizerConfig


class TestGmailOperationsExtended:
    """Extended tests for GmailOperations."""

    @patch("gmail_organizer.operations.build")
    def test_list_messages(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_users = mock_service.users.return_value
        mock_msgs = mock_users.messages.return_value
        mock_list = mock_msgs.list.return_value
        mock_list.execute.return_value = {
            "messages": [{"id": "msg1"}, {"id": "msg2"}],
            "nextPageToken": "token2",
        }

        creds = MagicMock()
        ops = GmailOperations(creds)
        result = ops.list_messages(max_results=10)
        assert len(result["messages"]) == 2
        assert result["nextPageToken"] == "token2"

    @patch("gmail_organizer.operations.build")
    def test_list_messages_with_label(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_users = mock_service.users.return_value
        mock_msgs = mock_users.messages.return_value
        mock_list = mock_msgs.list.return_value
        mock_list.execute.return_value = {"messages": []}

        creds = MagicMock()
        ops = GmailOperations(creds)
        result = ops.list_messages(label_ids=["INBOX"])
        assert result["messages"] == []

    @patch("gmail_organizer.operations.build")
    def test_get_message(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_users = mock_service.users.return_value
        mock_msgs = mock_users.messages.return_value
        mock_get = mock_msgs.get.return_value
        mock_get.execute.return_value = {
            "id": "msg1",
            "payload": {"headers": [{"name": "From", "value": "test@test.com"}]},
        }

        creds = MagicMock()
        ops = GmailOperations(creds)
        result = ops.get_message("msg1")
        assert result["id"] == "msg1"

    @patch("gmail_organizer.operations.build")
    def test_list_labels_full(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_users = mock_service.users.return_value
        mock_labels = mock_users.labels.return_value
        mock_list = mock_labels.list.return_value
        mock_list.execute.return_value = {
            "labels": [
                {"id": "INBOX", "name": "INBOX", "type": "system"},
                {"id": "lbl1", "name": "Custom", "type": "user"},
            ]
        }

        creds = MagicMock()
        ops = GmailOperations(creds)
        result = ops.list_labels_full()
        assert len(result) == 2

    @patch("gmail_organizer.operations.build")
    def test_get_label_info(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_users = mock_service.users.return_value
        mock_labels = mock_users.labels.return_value
        mock_get = mock_labels.get.return_value
        mock_get.execute.return_value = {"id": "lbl1", "messagesTotal": 42}

        creds = MagicMock()
        ops = GmailOperations(creds)
        result = ops.get_label_info("lbl1")
        assert result["messagesTotal"] == 42

    @patch("gmail_organizer.operations.build")
    def test_delete_label(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_users = mock_service.users.return_value
        mock_labels = mock_users.labels.return_value
        mock_delete = mock_labels.delete.return_value
        mock_delete.execute.return_value = {}

        creds = MagicMock()
        ops = GmailOperations(creds)
        ops.delete_label("lbl1")
        mock_labels.delete.assert_called_once()

    @patch("gmail_organizer.operations.build")
    def test_with_custom_config(self, mock_build):
        config = GmailOrganizerConfig(api_calls_per_second=5)
        creds = MagicMock()
        ops = GmailOperations(creds, config)
        assert ops.rate_limiter is not None
