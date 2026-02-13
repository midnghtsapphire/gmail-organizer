"""Tests for gmail_organizer.reporter module."""

import json
import os
import tempfile
import pytest

from gmail_organizer.reporter import ReportGenerator


class TestReportGenerator:
    def setup_method(self):
        self.reporter = ReportGenerator()

    def test_print_label_report(self, capsys):
        label_map = {"INBOX": "id1", "MUSIC": "id2"}
        self.reporter.print_label_report(label_map)
        captured = capsys.readouterr()
        assert "LABEL REPORT" in captured.out

    def test_print_label_report_with_stats(self, capsys):
        label_map = {"INBOX": "id1"}
        stats = {"INBOX": 100, "MUSIC": 50}
        self.reporter.print_label_report(label_map, stats)
        captured = capsys.readouterr()
        assert "100" in captured.out

    def test_print_categorization_report(self, capsys):
        self.reporter.print_categorization_report(
            total_processed=500,
            categorized=400,
            uncategorized=100,
            label_counts={"MUSIC": 200, "PROJECTS": 100},
        )
        captured = capsys.readouterr()
        assert "500" in captured.out
        assert "CATEGORIZATION REPORT" in captured.out

    def test_print_migration_report(self, capsys):
        stats = {"labels_migrated": 10, "messages_moved": 500, "errors": 2}
        self.reporter.print_migration_report(stats)
        captured = capsys.readouterr()
        assert "MIGRATION REPORT" in captured.out

    def test_export_json(self):
        data = {"label_count": 50, "total_processed": 100}
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            self.reporter.export_json(data, f.name)
            with open(f.name) as rf:
                loaded = json.load(rf)
            assert "timestamp" in loaded
            assert loaded["label_count"] == 50
        os.unlink(f.name)

    def test_export_markdown(self):
        data = {"label_count": 50, "total_processed": 100, "categorized": 80, "uncategorized": 20}
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            self.reporter.export_markdown(data, f.name)
            with open(f.name) as rf:
                content = rf.read()
            assert "Gmail Organizer Report" in content
        os.unlink(f.name)

    def test_export_markdown_with_migration(self):
        data = {
            "label_count": 50,
            "migration": {"labels_migrated": 5, "messages_moved": 100, "errors": 0},
        }
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            self.reporter.export_markdown(data, f.name)
            with open(f.name) as rf:
                content = rf.read()
            assert "Migration" in content
        os.unlink(f.name)
