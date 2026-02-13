"""Tests for gmail_organizer.categorizer module."""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from gmail_organizer.categorizer import EmailCategorizer


class TestEmailCategorizer:
    def setup_method(self):
        self.cat = EmailCategorizer()

    def test_self_email(self):
        headers = [
            {"name": "From", "value": "angelreporters@gmail.com"},
            {"name": "To", "value": "angelreporters@gmail.com"},
            {"name": "Subject", "value": "Note to self"},
        ]
        labels = self.cat.categorize(headers)
        assert any("Self-Emails" in l for l in labels)

    def test_github_email(self):
        headers = [
            {"name": "From", "value": "notifications@github.com"},
            {"name": "Subject", "value": "PR merged"},
        ]
        labels = self.cat.categorize(headers)
        assert any("GitHub" in l for l in labels)

    def test_ssrn_email(self):
        headers = [
            {"name": "From", "value": "noreply@ssrn.com"},
            {"name": "Subject", "value": "New paper"},
        ]
        labels = self.cat.categorize(headers)
        assert any("SSRN" in l for l in labels)

    def test_indeed_job(self):
        headers = [
            {"name": "From", "value": "alert@indeed.com"},
            {"name": "Subject", "value": "New job matches"},
        ]
        labels = self.cat.categorize(headers)
        assert any("Indeed" in l for l in labels)

    def test_amazon_order(self):
        headers = [
            {"name": "From", "value": "ship-confirm@amazon.com"},
            {"name": "Subject", "value": "Your order has shipped"},
        ]
        labels = self.cat.categorize(headers)
        assert any("Amazon" in l for l in labels)

    def test_chase_banking(self):
        headers = [
            {"name": "From", "value": "no-reply@chase.com"},
            {"name": "Subject", "value": "Account alert"},
        ]
        labels = self.cat.categorize(headers)
        assert any("Chase" in l or "Banking" in l for l in labels)

    def test_robinhood(self):
        headers = [
            {"name": "From", "value": "notifications@robinhood.com"},
            {"name": "Subject", "value": "Trade confirmed"},
        ]
        labels = self.cat.categorize(headers)
        assert any("Robinhood" in l for l in labels)

    def test_uchealth(self):
        headers = [
            {"name": "From", "value": "noreply@uchealth.org"},
            {"name": "Subject", "value": "Appointment reminder"},
        ]
        labels = self.cat.categorize(headers)
        assert any("UC-Health" in l for l in labels)

    def test_soundcloud(self):
        headers = [
            {"name": "From", "value": "no-reply@soundcloud.com"},
            {"name": "Subject", "value": "New follower"},
        ]
        labels = self.cat.categorize(headers)
        assert any("SoundCloud" in l for l in labels)

    def test_tiktok(self):
        headers = [
            {"name": "From", "value": "noreply@tiktok.com"},
            {"name": "Subject", "value": "New notification"},
        ]
        labels = self.cat.categorize(headers)
        assert any("TikTok" in l for l in labels)

    def test_newsletter_with_unsubscribe(self):
        headers = [
            {"name": "From", "value": "newsletter@techcrunch.com"},
            {"name": "Subject", "value": "Daily digest"},
            {"name": "List-Unsubscribe", "value": "<mailto:unsub@techcrunch.com>"},
        ]
        labels = self.cat.categorize(headers)
        assert any("NEWSLETTERS" in l for l in labels)

    def test_uncategorized_goes_to_flagged(self):
        headers = [
            {"name": "From", "value": "unknown@random-domain-xyz.com"},
            {"name": "Subject", "value": "Random subject"},
        ]
        labels = self.cat.categorize(headers)
        assert "FLAGGED-REVIEW" in labels

    def test_case_insensitive_from(self):
        headers = [
            {"name": "From", "value": "Notifications@GITHUB.COM"},
            {"name": "Subject", "value": "PR"},
        ]
        labels = self.cat.categorize(headers)
        assert any("GitHub" in l for l in labels)

    def test_legal_subject(self):
        headers = [
            {"name": "From", "value": "someone@lawfirm.com"},
            {"name": "Subject", "value": "Court hearing notice"},
        ]
        labels = self.cat.categorize(headers)
        assert any("Legal" in l or "Court" in l for l in labels)

    def test_irs_subject(self):
        headers = [
            {"name": "From", "value": "noreply@irs.gov"},
            {"name": "Subject", "value": "IRS Notice"},
        ]
        labels = self.cat.categorize(headers)
        assert any("IRS" in l for l in labels)

    def test_caresse_lopez(self):
        headers = [
            {"name": "From", "value": "lopez.caresse@gmail.com"},
            {"name": "Subject", "value": "Hey"},
        ]
        labels = self.cat.categorize(headers)
        assert any("Caresse" in l for l in labels)

    def test_empty_headers(self):
        labels = self.cat.categorize([])
        assert "FLAGGED-REVIEW" in labels

    def test_multiple_labels(self):
        headers = [
            {"name": "From", "value": "lopez.caresse@gmail.com"},
            {"name": "Subject", "value": "Song collaboration"},
        ]
        labels = self.cat.categorize(headers)
        # Should get both Caresse and Music labels
        assert len(labels) >= 1

    @given(st.text(min_size=1, max_size=50), st.text(min_size=1, max_size=50))
    @settings(max_examples=20)
    def test_never_returns_empty(self, from_addr, subject):
        headers = [
            {"name": "From", "value": from_addr},
            {"name": "Subject", "value": subject},
        ]
        labels = self.cat.categorize(headers)
        assert len(labels) >= 1
