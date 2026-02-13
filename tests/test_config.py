"""Tests for gmail_organizer.config module."""

import json
import os
import tempfile
import pytest

from gmail_organizer.config import (
    VERSION,
    APP_NAME,
    SCOPES,
    LABEL_HIERARCHY,
    CATEGORIZATION_RULES,
    MIGRATION_MAP,
    GmailOrganizerConfig,
    get_compiled_rules,
    get_compiled_migration_map,
)


class TestConstants:
    def test_version_format(self):
        parts = VERSION.split(".")
        assert len(parts) == 3

    def test_app_name(self):
        assert len(APP_NAME) > 0

    def test_scopes(self):
        assert isinstance(SCOPES, list)
        assert len(SCOPES) > 0

    def test_label_hierarchy_no_archive(self):
        for label in LABEL_HIERARCHY:
            lower = label.lower()
            assert "archive" not in lower
            assert "old-project" not in lower

    def test_label_hierarchy_has_key_labels(self):
        names = set(LABEL_HIERARCHY)
        assert "TIMELINE-EVIDENCE" in names
        assert "MUSIC" in names
        assert "PROJECTS" in names
        assert "JOB-SEARCH" in names
        assert "FLAGGED-REVIEW" in names

    def test_categorization_rules_structure(self):
        assert isinstance(CATEGORIZATION_RULES, list)
        for rule in CATEGORIZATION_RULES:
            assert "name" in rule
            assert "labels" in rule
            assert isinstance(rule["labels"], list)

    def test_migration_map_structure(self):
        assert isinstance(MIGRATION_MAP, list)
        for pattern, target in MIGRATION_MAP:
            assert isinstance(pattern, str)
            assert isinstance(target, str)


class TestCompiledRules:
    def test_get_compiled_rules(self):
        rules = get_compiled_rules()
        assert isinstance(rules, list)
        assert len(rules) > 0
        for rule in rules:
            assert "name" in rule
            assert "labels" in rule

    def test_compiled_rules_have_regex(self):
        rules = get_compiled_rules()
        has_regex = False
        for rule in rules:
            if "_from_re" in rule or "_to_re" in rule or "_subject_re" in rule:
                has_regex = True
                break
        assert has_regex

    def test_get_compiled_migration_map(self):
        mmap = get_compiled_migration_map()
        assert isinstance(mmap, list)
        assert len(mmap) > 0
        for pattern, target in mmap:
            assert hasattr(pattern, "search")  # compiled regex


class TestGmailOrganizerConfig:
    def test_defaults(self):
        config = GmailOrganizerConfig()
        assert config.batch_size == 100
        assert config.max_retries == 7
        assert config.dry_run is False

    def test_custom(self):
        config = GmailOrganizerConfig(batch_size=50, dry_run=True)
        assert config.batch_size == 50
        assert config.dry_run is True

    def test_from_json(self):
        data = {"batch_size": 200, "max_retries": 3}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            f.flush()
            config = GmailOrganizerConfig.from_json(f.name)
        assert config.batch_size == 200
        assert config.max_retries == 3
        os.unlink(f.name)

    def test_from_json_ignores_unknown(self):
        data = {"batch_size": 50, "unknown": "val"}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            f.flush()
            config = GmailOrganizerConfig.from_json(f.name)
        assert config.batch_size == 50
        os.unlink(f.name)

    def test_to_json(self):
        config = GmailOrganizerConfig(batch_size=77)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            config.to_json(f.name)
            with open(f.name) as rf:
                data = json.load(rf)
        assert data["batch_size"] == 77
        os.unlink(f.name)
