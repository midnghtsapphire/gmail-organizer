#!/usr/bin/env python3
"""
Unit Tests for Gmail Organizer
===============================
Tests label creation logic, categorization rules, rate limit handling,
migration mapping, and utility functions.

Run with: python -m pytest test_gmail_organizer.py -v
"""

import os
import sys
import json
import time
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from io import StringIO

# Import the module under test
import gmail_organizer as go


class TestLabelHierarchy(unittest.TestCase):
    """Tests for the label hierarchy definition."""

    def test_label_count_minimum(self):
        """Verify at least 80 labels are defined."""
        self.assertGreaterEqual(len(go.LABEL_HIERARCHY), 80)

    def test_all_labels_are_strings(self):
        for label in go.LABEL_HIERARCHY:
            self.assertIsInstance(label, str)

    def test_no_duplicate_labels(self):
        seen = set()
        for label in go.LABEL_HIERARCHY:
            self.assertNotIn(label, seen, f"Duplicate label: {label}")
            seen.add(label)

    def test_parent_labels_exist(self):
        label_set = set(go.LABEL_HIERARCHY)
        for label in go.LABEL_HIERARCHY:
            if "/" in label:
                parent = label.rsplit("/", 1)[0]
                self.assertIn(parent, label_set,
                              f"Parent '{parent}' missing for '{label}'")

    def test_top_level_categories(self):
        expected_top = [
            "TIMELINE-EVIDENCE", "MUSIC", "PROJECTS", "JOB-SEARCH",
            "API-KEYS-CREDENTIALS", "CONTACTS", "ORDERS-RECEIPTS",
            "NEWSLETTERS", "SOFTWARE-TRACKING", "SOCIAL-MEDIA",
            "FLAGGED-REVIEW",
        ]
        for cat in expected_top:
            self.assertIn(cat, go.LABEL_HIERARCHY)

    def test_specific_deep_labels(self):
        deep_labels = [
            "TIMELINE-EVIDENCE/Location-Activity/Google-Maps",
            "TIMELINE-EVIDENCE/Financial-Transactions/Robinhood-Investments",
            "MUSIC/Collaborations/Caresse-Rae-Edna",
            "PROJECTS/SSRN-Academic/eJournals",
            "JOB-SEARCH/Alerts/Indeed",
        ]
        for label in deep_labels:
            self.assertIn(label, go.LABEL_HIERARCHY)

    def test_labels_ordered_parent_before_child(self):
        seen = set()
        for label in go.LABEL_HIERARCHY:
            if "/" in label:
                parent = label.rsplit("/", 1)[0]
                self.assertIn(parent, seen,
                              f"Parent '{parent}' not listed before child '{label}'")
            seen.add(label)


class TestExtractHeader(unittest.TestCase):
    """Tests for the extract_header utility."""

    def test_extract_existing_header(self):
        headers = [
            {"name": "From", "value": "test@example.com"},
            {"name": "Subject", "value": "Hello World"},
        ]
        self.assertEqual(go.extract_header(headers, "From"), "test@example.com")

    def test_extract_case_insensitive(self):
        headers = [{"name": "FROM", "value": "test@example.com"}]
        self.assertEqual(go.extract_header(headers, "from"), "test@example.com")

    def test_extract_missing_header(self):
        headers = [{"name": "From", "value": "test@example.com"}]
        self.assertEqual(go.extract_header(headers, "Subject"), "")

    def test_extract_empty_headers(self):
        self.assertEqual(go.extract_header([], "From"), "")


class TestCategorizationRules(unittest.TestCase):
    """Tests for email categorization logic."""

    def _make_headers(self, from_addr="", to_addr="", subject="",
                      list_unsub=""):
        headers = []
        if from_addr:
            headers.append({"name": "From", "value": from_addr})
        if to_addr:
            headers.append({"name": "To", "value": to_addr})
        if subject:
            headers.append({"name": "Subject", "value": subject})
        if list_unsub:
            headers.append({"name": "List-Unsubscribe", "value": list_unsub})
        return headers

    def test_self_email(self):
        headers = self._make_headers(
            from_addr="angelreporters@gmail.com",
            to_addr="angelreporters@gmail.com",
            subject="Note to self"
        )
        labels = go.categorize_message(headers)
        self.assertIn("TIMELINE-EVIDENCE/Communications-Sent/Self-Emails", labels)

    def test_sent_to_contacts(self):
        headers = self._make_headers(
            from_addr="angelreporters@gmail.com",
            to_addr="someone@example.com",
            subject="Hello"
        )
        labels = go.categorize_message(headers)
        self.assertIn("TIMELINE-EVIDENCE/Communications-Sent/To-Contacts", labels)

    def test_caresse_lopez_from(self):
        headers = self._make_headers(from_addr="lopez.caresse@gmail.com")
        labels = go.categorize_message(headers)
        self.assertIn("CONTACTS/Caresse-Lopez", labels)
        self.assertIn("MUSIC/Collaborations/Caresse-Rae-Edna", labels)

    def test_caresse_lopez_to(self):
        headers = self._make_headers(
            from_addr="angelreporters@gmail.com",
            to_addr="lopez.caresse@gmail.com"
        )
        labels = go.categorize_message(headers)
        self.assertIn("CONTACTS/Caresse-Lopez", labels)

    def test_github(self):
        headers = self._make_headers(from_addr="notifications@github.com")
        labels = go.categorize_message(headers)
        self.assertIn("PROJECTS/GitHub-Dev", labels)

    def test_ssrn_from(self):
        headers = self._make_headers(from_addr="noreply@ssrn.com")
        labels = go.categorize_message(headers)
        self.assertIn("PROJECTS/SSRN-Academic", labels)

    def test_ssrn_subject(self):
        headers = self._make_headers(
            from_addr="someone@example.com",
            subject="Your SSRN paper was downloaded"
        )
        labels = go.categorize_message(headers)
        self.assertIn("PROJECTS/SSRN-Academic", labels)

    def test_indeed_jobs(self):
        headers = self._make_headers(
            from_addr="alert@indeed.com",
            subject="New job matches for you"
        )
        labels = go.categorize_message(headers)
        self.assertIn("JOB-SEARCH/Alerts/Indeed", labels)

    def test_linkedin_jobs(self):
        headers = self._make_headers(
            from_addr="jobs-noreply@linkedin.com",
            subject="Job recommendation"
        )
        labels = go.categorize_message(headers)
        self.assertIn("JOB-SEARCH/Alerts/LinkedIn", labels)

    def test_amazon_orders(self):
        headers = self._make_headers(
            from_addr="ship-confirm@amazon.com",
            subject="Your Amazon.com order has shipped"
        )
        labels = go.categorize_message(headers)
        self.assertIn("ORDERS-RECEIPTS/Amazon", labels)

    def test_chase_banking(self):
        headers = self._make_headers(from_addr="no-reply@alertsp.chase.com")
        labels = go.categorize_message(headers)
        self.assertIn("TIMELINE-EVIDENCE/Financial-Transactions/Banking-Chase", labels)

    def test_robinhood(self):
        headers = self._make_headers(from_addr="noreply@robinhood.com")
        labels = go.categorize_message(headers)
        self.assertIn("TIMELINE-EVIDENCE/Financial-Transactions/Robinhood-Investments", labels)

    def test_uchealth(self):
        headers = self._make_headers(from_addr="noreply@uchealth.org")
        labels = go.categorize_message(headers)
        self.assertIn("TIMELINE-EVIDENCE/Medical/UC-Health", labels)

    def test_irs_subject(self):
        headers = self._make_headers(
            from_addr="someone@irs.gov", subject="IRS Notice"
        )
        labels = go.categorize_message(headers)
        self.assertIn("TIMELINE-EVIDENCE/Government/IRS", labels)

    def test_ssa_subject(self):
        headers = self._make_headers(subject="Your Social Security Statement")
        labels = go.categorize_message(headers)
        self.assertIn("TIMELINE-EVIDENCE/Government/SSA", labels)

    def test_medicaid_subject(self):
        headers = self._make_headers(subject="Medicaid renewal notice")
        labels = go.categorize_message(headers)
        self.assertIn("TIMELINE-EVIDENCE/Government/Medicaid-Medicare", labels)

    def test_redfin(self):
        headers = self._make_headers(from_addr="listings@redfin.com")
        labels = go.categorize_message(headers)
        self.assertIn("TIMELINE-EVIDENCE/Location-Activity/Redfin-Property", labels)

    def test_hqs_inspection(self):
        headers = self._make_headers(subject="HQS Inspection Scheduled")
        labels = go.categorize_message(headers)
        self.assertIn("TIMELINE-EVIDENCE/Housing/HQS-Inspections", labels)

    def test_soundcloud(self):
        headers = self._make_headers(from_addr="noreply@soundcloud.com")
        labels = go.categorize_message(headers)
        self.assertIn("MUSIC/Platforms/SoundCloud", labels)

    def test_spotify(self):
        headers = self._make_headers(from_addr="no-reply@spotify.com")
        labels = go.categorize_message(headers)
        self.assertIn("MUSIC/Platforms/Spotify", labels)

    def test_tiktok(self):
        headers = self._make_headers(from_addr="noreply@tiktok.com")
        labels = go.categorize_message(headers)
        self.assertIn("SOCIAL-MEDIA/TikTok", labels)

    def test_reddit(self):
        headers = self._make_headers(from_addr="noreply@reddit.com")
        labels = go.categorize_message(headers)
        self.assertIn("SOCIAL-MEDIA/Reddit", labels)

    def test_nextdoor(self):
        headers = self._make_headers(from_addr="reply@nextdoor.com")
        labels = go.categorize_message(headers)
        self.assertIn("SOCIAL-MEDIA/Nextdoor", labels)

    def test_ebay(self):
        headers = self._make_headers(from_addr="ebay@ebay.com")
        labels = go.categorize_message(headers)
        self.assertIn("ORDERS-RECEIPTS/eBay", labels)

    def test_etsy(self):
        headers = self._make_headers(from_addr="transaction@etsy.com")
        labels = go.categorize_message(headers)
        self.assertIn("ORDERS-RECEIPTS/Etsy", labels)

    def test_legal_court(self):
        headers = self._make_headers(subject="Court hearing scheduled")
        labels = go.categorize_message(headers)
        self.assertIn("TIMELINE-EVIDENCE/Legal-Court", labels)

    def test_api_keys_credentials(self):
        headers = self._make_headers(
            from_addr="angelreporters@gmail.com",
            to_addr="angelreporters@gmail.com",
            subject="API key for project"
        )
        labels = go.categorize_message(headers)
        self.assertIn("API-KEYS-CREDENTIALS/API-Keys", labels)

    def test_newsletter_unsubscribe(self):
        headers = self._make_headers(
            from_addr="unknown@newsletter.example.com",
            subject="Weekly digest",
            list_unsub="<https://example.com/unsub>"
        )
        labels = go.categorize_message(headers)
        self.assertIn("NEWSLETTERS", labels)

    def test_flagged_review_fallback(self):
        headers = self._make_headers(
            from_addr="random@unknown-domain.xyz",
            subject="Random subject with no keywords"
        )
        labels = go.categorize_message(headers)
        self.assertIn("FLAGGED-REVIEW", labels)

    def test_multiple_labels_applied(self):
        headers = self._make_headers(
            from_addr="angelreporters@gmail.com",
            to_addr="angelreporters@gmail.com",
            subject="API token backup"
        )
        labels = go.categorize_message(headers)
        self.assertIn("TIMELINE-EVIDENCE/Communications-Sent/Self-Emails", labels)
        self.assertIn("API-KEYS-CREDENTIALS/API-Keys", labels)

    def test_church_one20(self):
        headers = self._make_headers(from_addr="pastor@one20church.org")
        labels = go.categorize_message(headers)
        self.assertIn("CONTACTS/Church-One20", labels)

    def test_google_play_receipt(self):
        headers = self._make_headers(
            from_addr="googleplay-noreply@google.com",
            subject="Your Google Play receipt"
        )
        labels = go.categorize_message(headers)
        self.assertIn("ORDERS-RECEIPTS/Google-Play", labels)


class TestRateLimitBackoff(unittest.TestCase):
    """Tests for exponential backoff logic."""

    @patch("gmail_organizer.time.sleep")
    def test_backoff_retries_on_429(self, mock_sleep):
        mock_resp = MagicMock()
        mock_resp.status = 429
        error = go.HttpError(mock_resp, b"Rate limit exceeded")

        call_count = 0
        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise error
            return "success"

        result = go.api_call_with_backoff(flaky_func, max_retries=5)
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("gmail_organizer.time.sleep")
    def test_backoff_raises_after_max_retries(self, mock_sleep):
        mock_resp = MagicMock()
        mock_resp.status = 429
        error = go.HttpError(mock_resp, b"Rate limit exceeded")

        def always_fail():
            raise error

        with self.assertRaises(RuntimeError):
            go.api_call_with_backoff(always_fail, max_retries=3)

    def test_non_retryable_error_raises_immediately(self):
        mock_resp = MagicMock()
        mock_resp.status = 404
        error = go.HttpError(mock_resp, b"Not found")

        def fail_404():
            raise error

        with self.assertRaises(go.HttpError):
            go.api_call_with_backoff(fail_404, max_retries=5)

    @patch("gmail_organizer.time.sleep")
    def test_backoff_retries_on_500(self, mock_sleep):
        mock_resp = MagicMock()
        mock_resp.status = 500
        error = go.HttpError(mock_resp, b"Server error")

        call_count = 0
        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise error
            return "ok"

        result = go.api_call_with_backoff(flaky_func, max_retries=5)
        self.assertEqual(result, "ok")

    @patch("gmail_organizer.time.sleep")
    def test_backoff_retries_on_503(self, mock_sleep):
        mock_resp = MagicMock()
        mock_resp.status = 503
        error = go.HttpError(mock_resp, b"Service unavailable")

        call_count = 0
        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise error
            return "ok"

        result = go.api_call_with_backoff(flaky_func, max_retries=5)
        self.assertEqual(result, "ok")


class TestColorFormatter(unittest.TestCase):
    """Tests for the colored log formatter."""

    def test_formatter_produces_output(self):
        import logging
        formatter = go.ColorFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="Test message", args=(), exc_info=None
        )
        output = formatter.format(record)
        self.assertIn("Test message", output)
        self.assertIn("INFO", output)


class TestCategorizationRulesStructure(unittest.TestCase):
    """Tests for the structure of categorization rules."""

    def test_all_rules_have_names(self):
        for rule in go.CATEGORIZATION_RULES:
            self.assertIn("name", rule)

    def test_all_rules_have_labels(self):
        for rule in go.CATEGORIZATION_RULES:
            self.assertIn("labels", rule)
            self.assertIsInstance(rule["labels"], list)
            self.assertGreater(len(rule["labels"]), 0)

    def test_all_rule_labels_in_hierarchy(self):
        hierarchy_set = set(go.LABEL_HIERARCHY)
        for rule in go.CATEGORIZATION_RULES:
            for label in rule["labels"]:
                self.assertIn(label, hierarchy_set,
                              f"Rule '{rule['name']}' references unknown label: {label}")

    def test_rule_count(self):
        self.assertGreaterEqual(len(go.CATEGORIZATION_RULES), 20)


class TestConstants(unittest.TestCase):
    """Tests for application constants."""

    def test_scopes(self):
        self.assertIn("https://mail.google.com/", go.SCOPES)

    def test_version_format(self):
        parts = go.VERSION.split(".")
        self.assertEqual(len(parts), 3)
        for p in parts:
            self.assertTrue(p.isdigit())

    def test_batch_size_reasonable(self):
        self.assertGreater(go.BATCH_SIZE, 0)
        self.assertLessEqual(go.BATCH_SIZE, 500)


# ══════════════════════════════════════════════════════════════════════════════
# MIGRATION TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestMigrationMapping(unittest.TestCase):
    """Tests for the map_old_label_to_new function."""

    def test_legal_maps_to_legal_court(self):
        result = go.map_old_label_to_new("Legal")
        self.assertEqual(result, "TIMELINE-EVIDENCE/Legal-Court")

    def test_legal_case_insensitive(self):
        result = go.map_old_label_to_new("legal")
        self.assertEqual(result, "TIMELINE-EVIDENCE/Legal-Court")

    def test_music_maps_to_music(self):
        result = go.map_old_label_to_new("Music")
        self.assertEqual(result, "MUSIC")

    def test_work_maps_to_job_search(self):
        result = go.map_old_label_to_new("Work")
        self.assertEqual(result, "JOB-SEARCH")

    def test_jobs_maps_to_job_search(self):
        result = go.map_old_label_to_new("Jobs")
        self.assertEqual(result, "JOB-SEARCH")

    def test_career_maps_to_job_search(self):
        result = go.map_old_label_to_new("Career")
        self.assertEqual(result, "JOB-SEARCH")

    def test_bank_maps_to_banking(self):
        result = go.map_old_label_to_new("Banking")
        self.assertEqual(result, "TIMELINE-EVIDENCE/Financial-Transactions/Banking-Chase")

    def test_chase_maps_to_banking_chase(self):
        result = go.map_old_label_to_new("Chase")
        self.assertEqual(result, "TIMELINE-EVIDENCE/Financial-Transactions/Banking-Chase")

    def test_robinhood_maps_correctly(self):
        result = go.map_old_label_to_new("Robinhood")
        self.assertEqual(result, "TIMELINE-EVIDENCE/Financial-Transactions/Robinhood-Investments")

    def test_github_maps_to_github_dev(self):
        result = go.map_old_label_to_new("GitHub")
        self.assertEqual(result, "PROJECTS/GitHub-Dev")

    def test_ssrn_maps_to_ssrn_academic(self):
        result = go.map_old_label_to_new("SSRN")
        self.assertEqual(result, "PROJECTS/SSRN-Academic")

    def test_amazon_maps_to_orders(self):
        result = go.map_old_label_to_new("Amazon")
        self.assertEqual(result, "ORDERS-RECEIPTS/Amazon")

    def test_ebay_maps_to_orders(self):
        result = go.map_old_label_to_new("eBay")
        self.assertEqual(result, "ORDERS-RECEIPTS/eBay")

    def test_tiktok_maps_to_social(self):
        result = go.map_old_label_to_new("TikTok")
        self.assertEqual(result, "SOCIAL-MEDIA/TikTok")

    def test_reddit_maps_to_social(self):
        result = go.map_old_label_to_new("Reddit")
        self.assertEqual(result, "SOCIAL-MEDIA/Reddit")

    def test_newsletter_maps(self):
        result = go.map_old_label_to_new("Newsletters")
        self.assertEqual(result, "NEWSLETTERS")

    def test_medical_maps(self):
        result = go.map_old_label_to_new("Medical")
        self.assertEqual(result, "TIMELINE-EVIDENCE/Medical")

    def test_tax_maps_to_irs(self):
        result = go.map_old_label_to_new("Tax")
        self.assertEqual(result, "TIMELINE-EVIDENCE/Government/IRS")

    def test_rent_maps_to_housing(self):
        result = go.map_old_label_to_new("Rent")
        self.assertEqual(result, "TIMELINE-EVIDENCE/Housing/Rent-Payments")

    def test_travel_maps_correctly(self):
        result = go.map_old_label_to_new("Travel")
        self.assertEqual(result, "TIMELINE-EVIDENCE/Location-Activity/Travel-Transport")

    def test_soundcloud_maps(self):
        result = go.map_old_label_to_new("SoundCloud")
        self.assertEqual(result, "MUSIC/Platforms/SoundCloud")

    def test_spotify_maps(self):
        result = go.map_old_label_to_new("Spotify")
        self.assertEqual(result, "MUSIC/Platforms/Spotify")

    def test_system_labels_return_none(self):
        """System labels should not be mapped."""
        self.assertIsNone(go.map_old_label_to_new("INBOX"))
        self.assertIsNone(go.map_old_label_to_new("SENT"))
        self.assertIsNone(go.map_old_label_to_new("TRASH"))
        self.assertIsNone(go.map_old_label_to_new("SPAM"))
        self.assertIsNone(go.map_old_label_to_new("DRAFT"))
        self.assertIsNone(go.map_old_label_to_new("STARRED"))
        self.assertIsNone(go.map_old_label_to_new("UNREAD"))
        self.assertIsNone(go.map_old_label_to_new("IMPORTANT"))
        self.assertIsNone(go.map_old_label_to_new("CATEGORY_SOCIAL"))
        self.assertIsNone(go.map_old_label_to_new("CATEGORY_PROMOTIONS"))

    def test_existing_hierarchy_labels_return_none(self):
        """Labels already in our hierarchy should not be re-mapped."""
        self.assertIsNone(go.map_old_label_to_new("TIMELINE-EVIDENCE"))
        self.assertIsNone(go.map_old_label_to_new("MUSIC"))
        self.assertIsNone(go.map_old_label_to_new("FLAGGED-REVIEW"))
        self.assertIsNone(go.map_old_label_to_new("PROJECTS/GitHub-Dev"))

    def test_nested_old_label_maps_by_leaf(self):
        """Old nested labels should map by their leaf segment."""
        result = go.map_old_label_to_new("Old/Legal")
        self.assertEqual(result, "TIMELINE-EVIDENCE/Legal-Court")

    def test_interview_maps(self):
        result = go.map_old_label_to_new("Interviews")
        self.assertEqual(result, "JOB-SEARCH/Interviews")

    def test_subscription_maps(self):
        result = go.map_old_label_to_new("Subscriptions")
        self.assertEqual(result, "ORDERS-RECEIPTS/Subscriptions")

    def test_password_maps(self):
        result = go.map_old_label_to_new("Passwords")
        self.assertEqual(result, "API-KEYS-CREDENTIALS/Passwords")

    def test_unknown_label_returns_none(self):
        """Labels with no matching pattern should return None."""
        result = go.map_old_label_to_new("RandomXYZ123")
        self.assertIsNone(result)

    def test_caresse_maps(self):
        result = go.map_old_label_to_new("Caresse")
        self.assertEqual(result, "CONTACTS/Caresse-Lopez")

    def test_church_maps(self):
        result = go.map_old_label_to_new("Church")
        self.assertEqual(result, "CONTACTS/Church-One20")


class TestMigrationMapStructure(unittest.TestCase):
    """Tests for the MIGRATION_MAP structure."""

    def test_migration_map_not_empty(self):
        self.assertGreater(len(go.MIGRATION_MAP), 50)

    def test_all_migration_targets_in_hierarchy(self):
        """Every target label in MIGRATION_MAP must exist in LABEL_HIERARCHY."""
        hierarchy_set = set(go.LABEL_HIERARCHY)
        for pattern, target in go.MIGRATION_MAP:
            self.assertIn(target, hierarchy_set,
                          f"Migration target '{target}' not in hierarchy (pattern: {pattern})")

    def test_migration_map_entries_are_tuples(self):
        for entry in go.MIGRATION_MAP:
            self.assertIsInstance(entry, tuple)
            self.assertEqual(len(entry), 2)

    def test_migration_patterns_are_valid_regex(self):
        import re
        for pattern, target in go.MIGRATION_MAP:
            try:
                re.compile(pattern)
            except re.error as e:
                self.fail(f"Invalid regex pattern '{pattern}': {e}")


class TestApplyLabelsSignature(unittest.TestCase):
    """Test that apply_labels supports remove_label_ids parameter."""

    def test_apply_labels_accepts_remove_param(self):
        """apply_labels should accept remove_label_ids keyword."""
        import inspect
        sig = inspect.signature(go.apply_labels)
        params = list(sig.parameters.keys())
        self.assertIn("remove_label_ids", params)


if __name__ == "__main__":
    unittest.main()
