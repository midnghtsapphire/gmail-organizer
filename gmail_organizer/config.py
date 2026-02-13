"""
Configuration Module for Gmail Organizer v2
=============================================
Externalized label hierarchy, categorization rules, migration maps.
All magic strings externalized. JSON-loadable config with dataclass.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

VERSION = "2.0.0"
APP_NAME = "Gmail Organizer"
SCOPES = ["https://mail.google.com/"]

# ---------------------------------------------------------------------------
# Label Hierarchy — NO ARCHIVING, ALL ACTIVE
# ---------------------------------------------------------------------------
LABEL_HIERARCHY: List[str] = [
    # ── Timeline Evidence ──
    "TIMELINE-EVIDENCE",
    "TIMELINE-EVIDENCE/Communications-Sent",
    "TIMELINE-EVIDENCE/Communications-Sent/Self-Emails",
    "TIMELINE-EVIDENCE/Communications-Sent/To-Contacts",
    "TIMELINE-EVIDENCE/Financial-Transactions",
    "TIMELINE-EVIDENCE/Financial-Transactions/Banking-Chase",
    "TIMELINE-EVIDENCE/Financial-Transactions/Robinhood-Investments",
    "TIMELINE-EVIDENCE/Financial-Transactions/Venmo-CashApp",
    "TIMELINE-EVIDENCE/Financial-Transactions/Crypto",
    "TIMELINE-EVIDENCE/Location-Activity",
    "TIMELINE-EVIDENCE/Location-Activity/Google-Maps",
    "TIMELINE-EVIDENCE/Location-Activity/Redfin-Property",
    "TIMELINE-EVIDENCE/Location-Activity/Travel-Transport",
    "TIMELINE-EVIDENCE/Medical",
    "TIMELINE-EVIDENCE/Medical/UC-Health",
    "TIMELINE-EVIDENCE/Medical/Insurance-Claims",
    "TIMELINE-EVIDENCE/Medical/Prescriptions",
    "TIMELINE-EVIDENCE/Government",
    "TIMELINE-EVIDENCE/Government/IRS",
    "TIMELINE-EVIDENCE/Government/SSA",
    "TIMELINE-EVIDENCE/Government/Medicaid-Medicare",
    "TIMELINE-EVIDENCE/Government/SNAP-Benefits",
    "TIMELINE-EVIDENCE/Government/Unemployment",
    "TIMELINE-EVIDENCE/Housing",
    "TIMELINE-EVIDENCE/Housing/Rent-Payments",
    "TIMELINE-EVIDENCE/Housing/Lease-Agreements",
    "TIMELINE-EVIDENCE/Housing/HQS-Inspections",
    "TIMELINE-EVIDENCE/Housing/Utilities",
    "TIMELINE-EVIDENCE/Legal-Court",
    # ── Music ──
    "MUSIC",
    "MUSIC/Platforms",
    "MUSIC/Platforms/SoundCloud",
    "MUSIC/Platforms/Spotify",
    "MUSIC/Platforms/Apple-Music",
    "MUSIC/Platforms/YouTube-Music",
    "MUSIC/Platforms/TikTok-Sounds",
    "MUSIC/Distribution",
    "MUSIC/Distribution/DistroKid",
    "MUSIC/Distribution/TuneCore",
    "MUSIC/Distribution/CDBaby",
    "MUSIC/Collaborations",
    "MUSIC/Collaborations/Caresse-Rae-Edna",
    "MUSIC/Copyright-Legal",
    "MUSIC/Copyright-Legal/ASCAP-BMI",
    "MUSIC/Copyright-Legal/Registrations",
    "MUSIC/Royalties",
    "MUSIC/Prompts-Templates",
    # ── Projects ──
    "PROJECTS",
    "PROJECTS/SSRN-Academic",
    "PROJECTS/SSRN-Academic/eJournals",
    "PROJECTS/SSRN-Academic/Downloads",
    "PROJECTS/GitHub-Dev",
    "PROJECTS/YumYumCode",
    "PROJECTS/Tiki-Washbot",
    "PROJECTS/Neurooz",
    "PROJECTS/Alt-Text-ADA",
    "PROJECTS/App-Ideas",
    "PROJECTS/Meetaudreyevans",
    "PROJECTS/Mechatronopolis",
    "PROJECTS/Qahwa-Coffee",
    "PROJECTS/Tiki-Wiki-Coffee",
    "PROJECTS/Emergency-Response",
    "PROJECTS/Pet-Insurance-App",
    "PROJECTS/Universal-OZ",
    # ── Job Search ──
    "JOB-SEARCH",
    "JOB-SEARCH/Applications",
    "JOB-SEARCH/Interviews",
    "JOB-SEARCH/Alerts",
    "JOB-SEARCH/Alerts/Indeed",
    "JOB-SEARCH/Alerts/LinkedIn",
    "JOB-SEARCH/Alerts/Glassdoor",
    "JOB-SEARCH/Offers",
    "JOB-SEARCH/Rejections",
    # ── API Keys / Credentials ──
    "API-KEYS-CREDENTIALS",
    "API-KEYS-CREDENTIALS/API-Keys",
    "API-KEYS-CREDENTIALS/Bot-Tokens",
    "API-KEYS-CREDENTIALS/Passwords",
    "API-KEYS-CREDENTIALS/Licenses",
    # ── Contacts ──
    "CONTACTS",
    "CONTACTS/Caresse-Lopez",
    "CONTACTS/Church-One20",
    "CONTACTS/Family",
    "CONTACTS/Professional",
    # ── Orders / Receipts ──
    "ORDERS-RECEIPTS",
    "ORDERS-RECEIPTS/Amazon",
    "ORDERS-RECEIPTS/eBay",
    "ORDERS-RECEIPTS/Etsy",
    "ORDERS-RECEIPTS/Google-Play",
    "ORDERS-RECEIPTS/Subscriptions",
    "ORDERS-RECEIPTS/Other-Purchases",
    # ── Newsletters ──
    "NEWSLETTERS",
    "NEWSLETTERS/Tech",
    "NEWSLETTERS/Music-Industry",
    "NEWSLETTERS/Business",
    # ── Software Tracking ──
    "SOFTWARE-TRACKING",
    "SOFTWARE-TRACKING/Trials",
    "SOFTWARE-TRACKING/Cancellations",
    "SOFTWARE-TRACKING/Updates",
    # ── Social Media ──
    "SOCIAL-MEDIA",
    "SOCIAL-MEDIA/TikTok",
    "SOCIAL-MEDIA/LinkedIn",
    "SOCIAL-MEDIA/Reddit",
    "SOCIAL-MEDIA/Nextdoor",
    "SOCIAL-MEDIA/Instagram",
    "SOCIAL-MEDIA/Facebook",
    # ── Flagged Review ──
    "FLAGGED-REVIEW",
]

# ---------------------------------------------------------------------------
# Migration Map — old label patterns → new hierarchy (compiled regex)
# ---------------------------------------------------------------------------
MIGRATION_MAP: List[Tuple[str, str]] = [
    # Legal
    (r"^legal", "TIMELINE-EVIDENCE/Legal-Court"),
    (r"^court", "TIMELINE-EVIDENCE/Legal-Court"),
    (r"^attorney", "TIMELINE-EVIDENCE/Legal-Court"),
    # Financial
    (r"^bank", "TIMELINE-EVIDENCE/Financial-Transactions/Banking-Chase"),
    (r"^chase", "TIMELINE-EVIDENCE/Financial-Transactions/Banking-Chase"),
    (r"^robinhood", "TIMELINE-EVIDENCE/Financial-Transactions/Robinhood-Investments"),
    (r"^venmo", "TIMELINE-EVIDENCE/Financial-Transactions/Venmo-CashApp"),
    (r"^cashapp", "TIMELINE-EVIDENCE/Financial-Transactions/Venmo-CashApp"),
    (r"^crypto", "TIMELINE-EVIDENCE/Financial-Transactions/Crypto"),
    # Medical
    (r"^medical", "TIMELINE-EVIDENCE/Medical"),
    (r"^health", "TIMELINE-EVIDENCE/Medical"),
    (r"^uchealth", "TIMELINE-EVIDENCE/Medical/UC-Health"),
    (r"^doctor", "TIMELINE-EVIDENCE/Medical"),
    (r"^prescri", "TIMELINE-EVIDENCE/Medical/Prescriptions"),
    # Government
    (r"^tax", "TIMELINE-EVIDENCE/Government/IRS"),
    (r"^irs", "TIMELINE-EVIDENCE/Government/IRS"),
    (r"^ssa", "TIMELINE-EVIDENCE/Government/SSA"),
    (r"^social.?security", "TIMELINE-EVIDENCE/Government/SSA"),
    (r"^medicaid", "TIMELINE-EVIDENCE/Government/Medicaid-Medicare"),
    (r"^medicare", "TIMELINE-EVIDENCE/Government/Medicaid-Medicare"),
    (r"^snap", "TIMELINE-EVIDENCE/Government/SNAP-Benefits"),
    (r"^unemploy", "TIMELINE-EVIDENCE/Government/Unemployment"),
    # Housing
    (r"^rent", "TIMELINE-EVIDENCE/Housing/Rent-Payments"),
    (r"^lease", "TIMELINE-EVIDENCE/Housing/Lease-Agreements"),
    (r"^hqs", "TIMELINE-EVIDENCE/Housing/HQS-Inspections"),
    (r"^inspect", "TIMELINE-EVIDENCE/Housing/HQS-Inspections"),
    (r"^utilit", "TIMELINE-EVIDENCE/Housing/Utilities"),
    (r"^electric", "TIMELINE-EVIDENCE/Housing/Utilities"),
    (r"^water.?bill", "TIMELINE-EVIDENCE/Housing/Utilities"),
    # Music
    (r"^music", "MUSIC"),
    (r"^song", "MUSIC"),
    (r"^soundcloud", "MUSIC/Platforms/SoundCloud"),
    (r"^spotify", "MUSIC/Platforms/Spotify"),
    (r"^apple.?music", "MUSIC/Platforms/Apple-Music"),
    (r"^distrokid", "MUSIC/Distribution/DistroKid"),
    (r"^tunecore", "MUSIC/Distribution/TuneCore"),
    (r"^royalt", "MUSIC/Royalties"),
    (r"^copyright", "MUSIC/Copyright-Legal"),
    (r"^distribut", "MUSIC/Distribution"),
    # Projects
    (r"^project", "PROJECTS"),
    (r"^ssrn", "PROJECTS/SSRN-Academic"),
    (r"^academ", "PROJECTS/SSRN-Academic"),
    (r"^github", "PROJECTS/GitHub-Dev"),
    (r"^dev$", "PROJECTS/GitHub-Dev"),
    (r"^development", "PROJECTS/GitHub-Dev"),
    (r"^coding", "PROJECTS/GitHub-Dev"),
    (r"^code$", "PROJECTS/GitHub-Dev"),
    (r"^yumyum", "PROJECTS/YumYumCode"),
    (r"^tiki", "PROJECTS/Tiki-Washbot"),
    (r"^neurooz", "PROJECTS/Neurooz"),
    (r"^alt.?text", "PROJECTS/Alt-Text-ADA"),
    (r"^app.?idea", "PROJECTS/App-Ideas"),
    # Job Search
    (r"^job", "JOB-SEARCH"),
    (r"^work$", "JOB-SEARCH"),
    (r"^career", "JOB-SEARCH"),
    (r"^employ", "JOB-SEARCH"),
    (r"^application", "JOB-SEARCH/Applications"),
    (r"^interview", "JOB-SEARCH/Interviews"),
    (r"^indeed", "JOB-SEARCH/Alerts/Indeed"),
    (r"^linkedin[/\\]job", "JOB-SEARCH/Alerts/LinkedIn"),
    (r"^job.?alert", "JOB-SEARCH/Alerts"),
    (r"^resume", "JOB-SEARCH/Applications"),
    # API / Credentials
    (r"^api", "API-KEYS-CREDENTIALS/API-Keys"),
    (r"^key", "API-KEYS-CREDENTIALS/API-Keys"),
    (r"^token", "API-KEYS-CREDENTIALS/Bot-Tokens"),
    (r"^password", "API-KEYS-CREDENTIALS/Passwords"),
    (r"^credential", "API-KEYS-CREDENTIALS"),
    (r"^license", "API-KEYS-CREDENTIALS/Licenses"),
    # Contacts
    (r"^contact", "CONTACTS"),
    (r"^caresse", "CONTACTS/Caresse-Lopez"),
    (r"^church", "CONTACTS/Church-One20"),
    (r"^one20", "CONTACTS/Church-One20"),
    # Orders / Receipts
    (r"^order", "ORDERS-RECEIPTS"),
    (r"^receipt", "ORDERS-RECEIPTS"),
    (r"^purchase", "ORDERS-RECEIPTS"),
    (r"^amazon", "ORDERS-RECEIPTS/Amazon"),
    (r"^ebay", "ORDERS-RECEIPTS/eBay"),
    (r"^etsy", "ORDERS-RECEIPTS/Etsy"),
    (r"^google.?play", "ORDERS-RECEIPTS/Google-Play"),
    (r"^subscript", "ORDERS-RECEIPTS/Subscriptions"),
    (r"^shopping", "ORDERS-RECEIPTS/Other-Purchases"),
    # Newsletters
    (r"^newsletter", "NEWSLETTERS"),
    (r"^digest", "NEWSLETTERS"),
    (r"^tech.?news", "NEWSLETTERS/Tech"),
    # Software
    (r"^software", "SOFTWARE-TRACKING"),
    (r"^trial", "SOFTWARE-TRACKING/Trials"),
    (r"^cancel", "SOFTWARE-TRACKING/Cancellations"),
    # Social Media
    (r"^social", "SOCIAL-MEDIA"),
    (r"^tiktok", "SOCIAL-MEDIA/TikTok"),
    (r"^linkedin$", "SOCIAL-MEDIA/LinkedIn"),
    (r"^reddit", "SOCIAL-MEDIA/Reddit"),
    (r"^nextdoor", "SOCIAL-MEDIA/Nextdoor"),
    # Catch-all
    (r"^important$", "FLAGGED-REVIEW"),
    (r"^review$", "FLAGGED-REVIEW"),
    (r"^todo$", "FLAGGED-REVIEW"),
    (r"^to.?do$", "FLAGGED-REVIEW"),
    (r"^flag", "FLAGGED-REVIEW"),
]

# ---------------------------------------------------------------------------
# Categorization Rules
# ---------------------------------------------------------------------------
CATEGORIZATION_RULES: List[Dict[str, Any]] = [
    {"name": "Self-Emails", "from_pattern": r"angelreporters@gmail\.com",
     "to_pattern": r"angelreporters@gmail\.com",
     "labels": ["TIMELINE-EVIDENCE/Communications-Sent/Self-Emails"]},
    {"name": "API-Keys-Credentials", "from_pattern": r"angelreporters",
     "subject_pattern": r"(?i)(api|token|key)",
     "labels": ["API-KEYS-CREDENTIALS/API-Keys"]},
    {"name": "Sent-To-Contacts", "from_pattern": r"angelreporters@gmail\.com",
     "labels": ["TIMELINE-EVIDENCE/Communications-Sent/To-Contacts"]},
    {"name": "Caresse-Lopez", "from_pattern": r"lopez\.caresse@gmail\.com",
     "labels": ["CONTACTS/Caresse-Lopez", "MUSIC/Collaborations/Caresse-Rae-Edna"]},
    {"name": "Caresse-Lopez-To", "to_pattern": r"lopez\.caresse@gmail\.com",
     "labels": ["CONTACTS/Caresse-Lopez", "MUSIC/Collaborations/Caresse-Rae-Edna"]},
    {"name": "GitHub", "from_pattern": r"github\.com",
     "labels": ["PROJECTS/GitHub-Dev"]},
    {"name": "SSRN-From", "from_pattern": r"ssrn",
     "labels": ["PROJECTS/SSRN-Academic"]},
    {"name": "SSRN-Subject", "subject_pattern": r"(?i)ssrn",
     "labels": ["PROJECTS/SSRN-Academic"]},
    {"name": "Indeed-Jobs", "from_pattern": r"indeed",
     "subject_pattern": r"(?i)job",
     "labels": ["JOB-SEARCH/Alerts/Indeed"]},
    {"name": "LinkedIn-Jobs", "from_pattern": r"linkedin",
     "subject_pattern": r"(?i)job",
     "labels": ["JOB-SEARCH/Alerts/LinkedIn"]},
    {"name": "Amazon-Orders", "from_pattern": r"amazon",
     "subject_pattern": r"(?i)(order|shipment)",
     "labels": ["ORDERS-RECEIPTS/Amazon"]},
    {"name": "Google-Play", "from_pattern": r"google",
     "subject_pattern": r"(?i)(receipt|purchase)",
     "labels": ["ORDERS-RECEIPTS/Google-Play"]},
    {"name": "Chase-Banking", "from_pattern": r"chase",
     "labels": ["TIMELINE-EVIDENCE/Financial-Transactions/Banking-Chase"]},
    {"name": "Bank-General", "from_pattern": r"bank",
     "labels": ["TIMELINE-EVIDENCE/Financial-Transactions/Banking-Chase"]},
    {"name": "Robinhood", "from_pattern": r"robinhood",
     "labels": ["TIMELINE-EVIDENCE/Financial-Transactions/Robinhood-Investments"]},
    {"name": "UC-Health", "from_pattern": r"uchealth",
     "labels": ["TIMELINE-EVIDENCE/Medical/UC-Health"]},
    {"name": "IRS", "subject_pattern": r"(?i)\bIRS\b",
     "labels": ["TIMELINE-EVIDENCE/Government/IRS"]},
    {"name": "SSA", "subject_pattern": r"(?i)(SSA|Social\s+Security)",
     "labels": ["TIMELINE-EVIDENCE/Government/SSA"]},
    {"name": "Medicaid-Medicare", "subject_pattern": r"(?i)(medicaid|medicare)",
     "labels": ["TIMELINE-EVIDENCE/Government/Medicaid-Medicare"]},
    {"name": "Redfin", "from_pattern": r"redfin",
     "labels": ["TIMELINE-EVIDENCE/Location-Activity/Redfin-Property"]},
    {"name": "HQS-Inspections", "subject_pattern": r"(?i)(HQS|inspection)",
     "labels": ["TIMELINE-EVIDENCE/Housing/HQS-Inspections"]},
    {"name": "SoundCloud", "from_pattern": r"soundcloud",
     "labels": ["MUSIC/Platforms/SoundCloud"]},
    {"name": "Spotify", "from_pattern": r"spotify",
     "labels": ["MUSIC/Platforms/Spotify"]},
    {"name": "Church-One20", "from_pattern": r"(one20|dusty)",
     "labels": ["CONTACTS/Church-One20"]},
    {"name": "TikTok", "from_pattern": r"tiktok",
     "labels": ["SOCIAL-MEDIA/TikTok"]},
    {"name": "LinkedIn", "from_pattern": r"linkedin",
     "labels": ["SOCIAL-MEDIA/LinkedIn"]},
    {"name": "Reddit", "from_pattern": r"reddit",
     "labels": ["SOCIAL-MEDIA/Reddit"]},
    {"name": "Nextdoor", "from_pattern": r"nextdoor",
     "labels": ["SOCIAL-MEDIA/Nextdoor"]},
    {"name": "eBay", "from_pattern": r"ebay",
     "labels": ["ORDERS-RECEIPTS/eBay"]},
    {"name": "Etsy", "from_pattern": r"etsy",
     "labels": ["ORDERS-RECEIPTS/Etsy"]},
    {"name": "Legal-Court", "subject_pattern": r"(?i)(court|attorney|legal|subpoena)",
     "labels": ["TIMELINE-EVIDENCE/Legal-Court"]},
    {"name": "Newsletters", "has_unsubscribe": True,
     "labels": ["NEWSLETTERS"]},
]

# Pre-compile all rule patterns
_COMPILED_RULES: List[Dict[str, Any]] = []


def get_compiled_rules() -> List[Dict[str, Any]]:
    """Get categorization rules with compiled regex patterns."""
    global _COMPILED_RULES
    if _COMPILED_RULES:
        return _COMPILED_RULES

    for rule in CATEGORIZATION_RULES:
        compiled = dict(rule)
        if "from_pattern" in rule:
            compiled["_from_re"] = re.compile(rule["from_pattern"], re.IGNORECASE)
        if "to_pattern" in rule:
            compiled["_to_re"] = re.compile(rule["to_pattern"], re.IGNORECASE)
        if "subject_pattern" in rule:
            compiled["_subject_re"] = re.compile(rule["subject_pattern"], re.IGNORECASE)
        _COMPILED_RULES.append(compiled)

    return _COMPILED_RULES


# Pre-compile migration map patterns
_COMPILED_MIGRATION: List[Tuple[re.Pattern, str]] = []


def get_compiled_migration_map() -> List[Tuple[re.Pattern, str]]:
    """Get migration map with compiled regex patterns."""
    global _COMPILED_MIGRATION
    if _COMPILED_MIGRATION:
        return _COMPILED_MIGRATION

    for pattern, target in MIGRATION_MAP:
        _COMPILED_MIGRATION.append((re.compile(pattern, re.IGNORECASE), target))

    return _COMPILED_MIGRATION


# ---------------------------------------------------------------------------
# GmailOrganizerConfig dataclass
# ---------------------------------------------------------------------------
@dataclass
class GmailOrganizerConfig:
    """Central configuration for the Gmail Organizer."""

    batch_size: int = 100
    max_retries: int = 7
    base_delay: float = 1.0
    api_calls_per_second: int = 10
    credentials_file: str = "credentials.json"
    token_file: str = "token.pickle"
    log_file: str = "gmail_organizer.log"
    dry_run: bool = False
    max_messages: int = 0
    labels_only: bool = False
    migrate: bool = False
    cleanup: bool = False

    @classmethod
    def from_json(cls, path: str) -> "GmailOrganizerConfig":
        """Load configuration from a JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def to_json(self, path: str) -> None:
        """Save configuration to a JSON file."""
        from dataclasses import asdict
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)
