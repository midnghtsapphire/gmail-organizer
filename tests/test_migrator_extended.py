"""Extended tests for gmail_organizer.migrator module — boost coverage."""

import pytest
from unittest.mock import MagicMock, patch, call

from gmail_organizer.config import LABEL_HIERARCHY, GmailOrganizerConfig
from gmail_organizer.migrator import LabelArchitect, LabelMigrator, LabelCleaner


class TestLabelMigratorExtended:
    """Extended tests for LabelMigrator to cover more branches."""

    def setup_method(self):
        self.mock_ops = MagicMock()
        self.label_map = {label: f"id_{i}" for i, label in enumerate(LABEL_HIERARCHY)}
        self.config = GmailOrganizerConfig()

    def test_migrate_all_execute_mode(self):
        """Test actual execution (not dry run)."""
        self.mock_ops.list_labels.return_value = {
            "bank": "bank_id",
            "INBOX": "INBOX",
        }
        self.mock_ops.list_messages.return_value = {
            "messages": [{"id": "msg1"}, {"id": "msg2"}],
        }
        self.mock_ops.modify_message.return_value = {"id": "msg1"}

        migrator = LabelMigrator(self.mock_ops, self.label_map, self.config)
        stats = migrator.migrate_all(dry_run=False)
        assert stats["labels_migrated"] >= 1
        assert stats["messages_moved"] >= 1

    def test_migrate_all_target_not_in_map(self):
        """Test when target label ID not found in label_map."""
        self.mock_ops.list_labels.return_value = {
            "some-old-label": "old_id",
        }
        # Use a label_map that's empty
        migrator = LabelMigrator(self.mock_ops, {}, self.config)
        stats = migrator.migrate_all(dry_run=False)
        # Should skip since target_id not found
        assert stats["labels_migrated"] == 0

    def test_migrate_label_messages_with_pagination(self):
        """Test message migration with pagination."""
        self.mock_ops.list_labels.return_value = {
            "bank": "bank_id",
        }
        self.mock_ops.list_messages.side_effect = [
            {"messages": [{"id": "msg1"}], "nextPageToken": "token2"},
            {"messages": [{"id": "msg2"}]},
        ]
        self.mock_ops.modify_message.return_value = {"id": "ok"}

        migrator = LabelMigrator(self.mock_ops, self.label_map, self.config)
        stats = migrator.migrate_all(dry_run=False)
        assert stats["messages_moved"] >= 2

    def test_migrate_label_messages_error(self):
        """Test error handling during message migration."""
        self.mock_ops.list_labels.return_value = {
            "bank": "bank_id",
        }
        self.mock_ops.list_messages.return_value = {
            "messages": [{"id": "msg1"}],
        }
        self.mock_ops.modify_message.side_effect = Exception("API error")

        migrator = LabelMigrator(self.mock_ops, self.label_map, self.config)
        stats = migrator.migrate_all(dry_run=False)
        assert stats["errors"] >= 1

    def test_migrate_skips_hierarchy_labels(self):
        """Labels already in hierarchy should be skipped."""
        existing = {label: f"id_{i}" for i, label in enumerate(LABEL_HIERARCHY)}
        self.mock_ops.list_labels.return_value = existing

        migrator = LabelMigrator(self.mock_ops, self.label_map, self.config)
        stats = migrator.migrate_all(dry_run=True)
        assert stats["labels_migrated"] == 0

    def test_migrate_label_messages_empty(self):
        """Test when source label has no messages."""
        self.mock_ops.list_labels.return_value = {
            "bank": "bank_id",
        }
        self.mock_ops.list_messages.return_value = {"messages": []}

        migrator = LabelMigrator(self.mock_ops, self.label_map, self.config)
        stats = migrator.migrate_all(dry_run=False)
        assert stats["messages_moved"] == 0


class TestLabelCleanerExtended:
    """Extended tests for LabelCleaner."""

    def test_cleanup_execute_mode(self):
        """Test actual deletion (not dry run)."""
        mock_ops = MagicMock()
        mock_ops.list_labels_full.return_value = [
            {"id": "lbl_1", "name": "old-label", "type": "user"},
        ]
        mock_ops.get_label_info.return_value = {"messagesTotal": 0}

        cleaner = LabelCleaner(mock_ops)
        removed = cleaner.cleanup_empty_labels(dry_run=False)
        assert removed == 1
        mock_ops.delete_label.assert_called_once_with("lbl_1")

    def test_cleanup_skips_hierarchy_labels(self):
        """Labels in our hierarchy should not be removed."""
        mock_ops = MagicMock()
        mock_ops.list_labels_full.return_value = [
            {"id": "lbl_1", "name": LABEL_HIERARCHY[0], "type": "user"},
        ]

        cleaner = LabelCleaner(mock_ops)
        removed = cleaner.cleanup_empty_labels(dry_run=True)
        assert removed == 0


class TestLabelArchitectExtended:
    """Extended tests for LabelArchitect."""

    def test_build_hierarchy_partial_existing(self):
        """Some labels exist, some need creation."""
        mock_ops = MagicMock()
        # Only first 5 labels exist
        existing = {label: f"id_{i}" for i, label in enumerate(LABEL_HIERARCHY[:5])}
        mock_ops.list_labels.return_value = existing
        mock_ops.create_label.return_value = {"id": "new_id"}

        architect = LabelArchitect(mock_ops)
        result = architect.build_hierarchy()

        expected_creates = len(LABEL_HIERARCHY) - 5
        assert mock_ops.create_label.call_count == expected_creates
