"""Tests for gmail_organizer.migrator module."""

import pytest
from unittest.mock import MagicMock, patch

from gmail_organizer.config import LABEL_HIERARCHY, GmailOrganizerConfig
from gmail_organizer.migrator import LabelArchitect, LabelMigrator, LabelCleaner


class TestLabelArchitect:
    def test_build_hierarchy_creates_missing(self):
        mock_ops = MagicMock()
        mock_ops.list_labels.return_value = {"INBOX": "INBOX_ID"}
        mock_ops.create_label.return_value = {"id": "new_id"}

        architect = LabelArchitect(mock_ops)
        result = architect.build_hierarchy()

        assert isinstance(result, dict)
        assert mock_ops.create_label.call_count > 0

    def test_build_hierarchy_skips_existing(self):
        mock_ops = MagicMock()
        existing = {label: f"id_{i}" for i, label in enumerate(LABEL_HIERARCHY)}
        mock_ops.list_labels.return_value = existing

        architect = LabelArchitect(mock_ops)
        result = architect.build_hierarchy()

        mock_ops.create_label.assert_not_called()

    def test_build_hierarchy_handles_error(self):
        mock_ops = MagicMock()
        mock_ops.list_labels.return_value = {}
        mock_ops.create_label.side_effect = Exception("API error")

        architect = LabelArchitect(mock_ops)
        result = architect.build_hierarchy()
        assert isinstance(result, dict)


class TestLabelMigrator:
    def setup_method(self):
        self.mock_ops = MagicMock()
        self.label_map = {label: f"id_{i}" for i, label in enumerate(LABEL_HIERARCHY)}
        self.config = GmailOrganizerConfig()

    def test_find_migration_target_bank(self):
        migrator = LabelMigrator(self.mock_ops, self.label_map, self.config)
        target = migrator.find_migration_target("bank")
        assert target is not None
        assert "Banking" in target or "Financial" in target

    def test_find_migration_target_music(self):
        migrator = LabelMigrator(self.mock_ops, self.label_map, self.config)
        target = migrator.find_migration_target("music")
        assert target is not None
        assert "MUSIC" in target

    def test_find_migration_target_unknown(self):
        migrator = LabelMigrator(self.mock_ops, self.label_map, self.config)
        target = migrator.find_migration_target("zzz_unknown_label_zzz")
        assert target is None

    def test_find_migration_target_case_insensitive(self):
        migrator = LabelMigrator(self.mock_ops, self.label_map, self.config)
        t1 = migrator.find_migration_target("BANK")
        t2 = migrator.find_migration_target("bank")
        assert t1 == t2

    def test_migrate_all_dry_run(self):
        self.mock_ops.list_labels.return_value = {
            "bank": "bank_id",
            "music": "music_id",
            "INBOX": "INBOX",
        }
        migrator = LabelMigrator(self.mock_ops, self.label_map, self.config)
        stats = migrator.migrate_all(dry_run=True)
        assert stats["labels_migrated"] >= 0
        assert stats["messages_moved"] == 0

    def test_migrate_all_skips_system_labels(self):
        self.mock_ops.list_labels.return_value = {
            "INBOX": "INBOX",
            "SENT": "SENT",
            "CATEGORY_SOCIAL": "CAT_SOC",
        }
        migrator = LabelMigrator(self.mock_ops, self.label_map, self.config)
        stats = migrator.migrate_all(dry_run=True)
        assert stats["labels_migrated"] == 0


class TestLabelCleaner:
    def test_cleanup_empty_dry_run(self):
        mock_ops = MagicMock()
        mock_ops.list_labels_full.return_value = [
            {"id": "lbl_1", "name": "old-label", "type": "user"},
        ]
        mock_ops.get_label_info.return_value = {"messagesTotal": 0}

        cleaner = LabelCleaner(mock_ops)
        removed = cleaner.cleanup_empty_labels(dry_run=True)
        assert removed >= 1
        mock_ops.delete_label.assert_not_called()

    def test_cleanup_skips_system(self):
        mock_ops = MagicMock()
        mock_ops.list_labels_full.return_value = [
            {"id": "INBOX", "name": "INBOX", "type": "system"},
        ]

        cleaner = LabelCleaner(mock_ops)
        removed = cleaner.cleanup_empty_labels(dry_run=True)
        assert removed == 0

    def test_cleanup_skips_nonempty(self):
        mock_ops = MagicMock()
        mock_ops.list_labels_full.return_value = [
            {"id": "lbl_1", "name": "has-messages", "type": "user"},
        ]
        mock_ops.get_label_info.return_value = {"messagesTotal": 50}

        cleaner = LabelCleaner(mock_ops)
        removed = cleaner.cleanup_empty_labels(dry_run=True)
        assert removed == 0

    def test_cleanup_handles_error(self):
        mock_ops = MagicMock()
        mock_ops.list_labels_full.return_value = [
            {"id": "lbl_1", "name": "error-label", "type": "user"},
        ]
        mock_ops.get_label_info.side_effect = Exception("API error")

        cleaner = LabelCleaner(mock_ops)
        removed = cleaner.cleanup_empty_labels(dry_run=True)
        assert removed == 0
