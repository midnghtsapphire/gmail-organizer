"""Tests for gmail_organizer.utils module."""

import logging
import pytest

from gmail_organizer.utils import C, setup_logging, extract_header, print_banner


class TestColorCodes:
    def test_reset(self):
        assert C.RESET == "\033[0m"

    def test_all_strings(self):
        for attr in dir(C):
            if not attr.startswith("_"):
                assert isinstance(getattr(C, attr), str)


class TestExtractHeader:
    def test_extract_from(self):
        headers = [
            {"name": "From", "value": "test@example.com"},
            {"name": "Subject", "value": "Hello"},
        ]
        assert extract_header(headers, "From") == "test@example.com"

    def test_extract_subject(self):
        headers = [{"name": "Subject", "value": "Test Subject"}]
        assert extract_header(headers, "Subject") == "Test Subject"

    def test_case_insensitive(self):
        headers = [{"name": "FROM", "value": "test@example.com"}]
        assert extract_header(headers, "from") == "test@example.com"

    def test_missing_header(self):
        headers = [{"name": "From", "value": "test@example.com"}]
        assert extract_header(headers, "X-Custom") == ""

    def test_empty_headers(self):
        assert extract_header([], "From") == ""

    def test_empty_value(self):
        headers = [{"name": "From", "value": ""}]
        assert extract_header(headers, "From") == ""


class TestSetupLogging:
    def test_returns_logger(self):
        logger = setup_logging("test_gmail_logger")
        assert isinstance(logger, logging.Logger)

    def test_has_handlers(self):
        logger = setup_logging("test_gmail_logger2")
        assert len(logger.handlers) > 0

    def test_idempotent(self):
        logger1 = setup_logging("test_gmail_logger3")
        count = len(logger1.handlers)
        logger2 = setup_logging("test_gmail_logger3")
        assert len(logger2.handlers) == count


class TestPrintBanner:
    def test_banner(self, capsys):
        print_banner("2.0.0")
        captured = capsys.readouterr()
        assert "2.0.0" in captured.out
