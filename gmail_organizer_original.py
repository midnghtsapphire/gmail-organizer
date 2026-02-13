#!/usr/bin/env python3
"""
Gmail Organizer — Automated Email Labeling, Sorting & Migration System
=======================================================================
Creates 80+ hierarchical labels, auto-sorts every email in your Gmail
mailbox, and migrates emails from existing labels into the new hierarchy.

Author : Angel Evans
License: MIT
Version: 1.1.0
"""

import os
import sys
import re
import json
import time
import logging
import pickle
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── Third-party imports ──────────────────────────────────────────────────────
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("\033[91m[ERROR]\033[0m Missing dependencies. Install with:")
    print("  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    sys.exit(1)

# ── Constants ────────────────────────────────────────────────────────────────
VERSION = "1.1.0"
SCOPES = ["https://mail.google.com/"]
TOKEN_FILE = "token.pickle"
CREDENTIALS_FILE = "credentials.json"
LOG_FILE = "gmail_organizer.log"
BATCH_SIZE = 100  # messages per page
MAX_RETRIES = 7
BASE_DELAY = 1.0  # seconds

# ── ANSI Colors ──────────────────────────────────────────────────────────────
class C:
    """Terminal color codes."""
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    GRAY    = "\033[90m"
    BG_GREEN  = "\033[42m"
    BG_BLUE   = "\033[44m"
    BG_YELLOW = "\033[43m"
    BG_RED    = "\033[41m"
    BG_MAGENTA = "\033[45m"

# ── Complete Label Hierarchy ─────────────────────────────────────────────────
LABEL_HIERARCHY = [
    # TIMELINE-EVIDENCE
    "TIMELINE-EVIDENCE",
    "TIMELINE-EVIDENCE/Location-Activity",
    "TIMELINE-EVIDENCE/Location-Activity/Google-Maps",
    "TIMELINE-EVIDENCE/Location-Activity/Redfin-Property",
    "TIMELINE-EVIDENCE/Location-Activity/Travel-Transport",
    "TIMELINE-EVIDENCE/Location-Activity/Check-Ins",
    "TIMELINE-EVIDENCE/Communications-Sent",
    "TIMELINE-EVIDENCE/Communications-Sent/Self-Emails",
    "TIMELINE-EVIDENCE/Communications-Sent/To-Contacts",
    "TIMELINE-EVIDENCE/Communications-Sent/Replies",
    "TIMELINE-EVIDENCE/Legal-Court",
    "TIMELINE-EVIDENCE/Legal-Court/Case-Files",
    "TIMELINE-EVIDENCE/Legal-Court/Attorney-Correspondence",
    "TIMELINE-EVIDENCE/Legal-Court/Court-Notices",
    "TIMELINE-EVIDENCE/Government",
    "TIMELINE-EVIDENCE/Government/IRS",
    "TIMELINE-EVIDENCE/Government/SSA",
    "TIMELINE-EVIDENCE/Government/Medicaid-Medicare",
    "TIMELINE-EVIDENCE/Government/Other-Gov",
    "TIMELINE-EVIDENCE/Financial-Transactions",
    "TIMELINE-EVIDENCE/Financial-Transactions/Banking-Chase",
    "TIMELINE-EVIDENCE/Financial-Transactions/Credit-Cards",
    "TIMELINE-EVIDENCE/Financial-Transactions/Robinhood-Investments",
    "TIMELINE-EVIDENCE/Financial-Transactions/Payment-Processors",
    "TIMELINE-EVIDENCE/Financial-Transactions/Bills-Utilities",
    "TIMELINE-EVIDENCE/Medical",
    "TIMELINE-EVIDENCE/Medical/UC-Health",
    "TIMELINE-EVIDENCE/Medical/Colorado-In-Motion",
    "TIMELINE-EVIDENCE/Medical/Insurance",
    "TIMELINE-EVIDENCE/Medical/Appointments",
    "TIMELINE-EVIDENCE/Medical/Prescriptions",
    "TIMELINE-EVIDENCE/Housing",
    "TIMELINE-EVIDENCE/Housing/HQS-Inspections",
    "TIMELINE-EVIDENCE/Housing/Vouchers",
    "TIMELINE-EVIDENCE/Housing/Rent-Payments",
    "TIMELINE-EVIDENCE/Housing/Property-Search",
    # MUSIC
    "MUSIC",
    "MUSIC/Collaborations",
    "MUSIC/Collaborations/Caresse-Rae-Edna",
    "MUSIC/Collaborations/Other-Collabs",
    "MUSIC/Platforms",
    "MUSIC/Platforms/SoundCloud",
    "MUSIC/Platforms/Spotify",
    "MUSIC/Platforms/Suno",
    "MUSIC/Platforms/Donna",
    "MUSIC/Lyrics-Drafts",
    "MUSIC/Copyright-Legal",
    "MUSIC/Distribution",
    # PROJECTS
    "PROJECTS",
    "PROJECTS/SSRN-Academic",
    "PROJECTS/SSRN-Academic/Paper-Generation",
    "PROJECTS/SSRN-Academic/Submissions",
    "PROJECTS/SSRN-Academic/eJournals",
    "PROJECTS/YumYumCode",
    "PROJECTS/GitHub-Dev",
    "PROJECTS/Universal-OZ",
    "PROJECTS/MCT-InTheWild",
    "PROJECTS/Meetaudreyevans",
    "PROJECTS/Tiki-Washbot",
    "PROJECTS/Neurooz",
    "PROJECTS/Alt-Text-ADA",
    "PROJECTS/App-Ideas",
    "PROJECTS/Other-Projects",
    # JOB-SEARCH
    "JOB-SEARCH",
    "JOB-SEARCH/Applications",
    "JOB-SEARCH/Alerts",
    "JOB-SEARCH/Alerts/Indeed",
    "JOB-SEARCH/Alerts/LinkedIn",
    "JOB-SEARCH/Alerts/Other",
    "JOB-SEARCH/Responses",
    "JOB-SEARCH/Interviews",
    # API-KEYS-CREDENTIALS
    "API-KEYS-CREDENTIALS",
    "API-KEYS-CREDENTIALS/API-Keys",
    "API-KEYS-CREDENTIALS/Bot-Tokens",
    "API-KEYS-CREDENTIALS/Passwords",
    "API-KEYS-CREDENTIALS/Licenses",
    # CONTACTS
    "CONTACTS",
    "CONTACTS/Caresse-Lopez",
    "CONTACTS/Church-One20",
    "CONTACTS/Medical-Team",
    "CONTACTS/Legal-Team",
    "CONTACTS/Housing-Contacts",
    "CONTACTS/Other-Important",
    # ORDERS-RECEIPTS
    "ORDERS-RECEIPTS",
    "ORDERS-RECEIPTS/Amazon",
    "ORDERS-RECEIPTS/Google-Play",
    "ORDERS-RECEIPTS/eBay",
    "ORDERS-RECEIPTS/Etsy",
    "ORDERS-RECEIPTS/Subscriptions",
    "ORDERS-RECEIPTS/Other-Purchases",
    # NEWSLETTERS
    "NEWSLETTERS",
    "NEWSLETTERS/Tech",
    "NEWSLETTERS/Finance",
    "NEWSLETTERS/Business",
    "NEWSLETTERS/Other",
    # SOFTWARE-TRACKING
    "SOFTWARE-TRACKING",
    "SOFTWARE-TRACKING/Purchases",
    "SOFTWARE-TRACKING/Trials",
    "SOFTWARE-TRACKING/Licenses",
    "SOFTWARE-TRACKING/Cancellations",
    # SOCIAL-MEDIA
    "SOCIAL-MEDIA",
    "SOCIAL-MEDIA/TikTok",
    "SOCIAL-MEDIA/LinkedIn",
    "SOCIAL-MEDIA/Reddit",
    "SOCIAL-MEDIA/Nextdoor",
    "SOCIAL-MEDIA/Other",
    # FLAGGED-REVIEW
    "FLAGGED-REVIEW",
]

# ── Migration Mapping: Old Label Patterns → New Hierarchy ────────────────────
# Each entry: (pattern_to_match_old_label, new_hierarchy_label)
# Patterns are matched case-insensitively against existing label names.
# Order matters — first match wins for primary mapping.
MIGRATION_MAP = [
    # ── Legal ──
    (r"^legal$",                          "TIMELINE-EVIDENCE/Legal-Court"),
    (r"^legal[/\\]court",                 "TIMELINE-EVIDENCE/Legal-Court"),
    (r"^legal[/\\]attorney",              "TIMELINE-EVIDENCE/Legal-Court/Attorney-Correspondence"),
    (r"^legal[/\\]case",                  "TIMELINE-EVIDENCE/Legal-Court/Case-Files"),
    (r"^court",                           "TIMELINE-EVIDENCE/Legal-Court"),
    (r"^attorney",                        "TIMELINE-EVIDENCE/Legal-Court/Attorney-Correspondence"),
    # ── Financial ──
    (r"^financ",                          "TIMELINE-EVIDENCE/Financial-Transactions"),
    (r"^bank",                            "TIMELINE-EVIDENCE/Financial-Transactions/Banking-Chase"),
    (r"^chase",                           "TIMELINE-EVIDENCE/Financial-Transactions/Banking-Chase"),
    (r"^credit.?card",                    "TIMELINE-EVIDENCE/Financial-Transactions/Credit-Cards"),
    (r"^invest",                          "TIMELINE-EVIDENCE/Financial-Transactions/Robinhood-Investments"),
    (r"^robinhood",                       "TIMELINE-EVIDENCE/Financial-Transactions/Robinhood-Investments"),
    (r"^bills?$",                         "TIMELINE-EVIDENCE/Financial-Transactions/Bills-Utilities"),
    (r"^utilit",                          "TIMELINE-EVIDENCE/Financial-Transactions/Bills-Utilities"),
    (r"^payment",                         "TIMELINE-EVIDENCE/Financial-Transactions/Payment-Processors"),
    # ── Government ──
    (r"^gov",                             "TIMELINE-EVIDENCE/Government"),
    (r"^irs$",                            "TIMELINE-EVIDENCE/Government/IRS"),
    (r"^tax",                             "TIMELINE-EVIDENCE/Government/IRS"),
    (r"^ssa$",                            "TIMELINE-EVIDENCE/Government/SSA"),
    (r"^social.?security",               "TIMELINE-EVIDENCE/Government/SSA"),
    (r"^medicaid",                        "TIMELINE-EVIDENCE/Government/Medicaid-Medicare"),
    (r"^medicare",                        "TIMELINE-EVIDENCE/Government/Medicaid-Medicare"),
    # ── Medical ──
    (r"^medical",                         "TIMELINE-EVIDENCE/Medical"),
    (r"^health",                          "TIMELINE-EVIDENCE/Medical"),
    (r"^doctor",                          "TIMELINE-EVIDENCE/Medical"),
    (r"^uchealth",                        "TIMELINE-EVIDENCE/Medical/UC-Health"),
    (r"^prescription",                    "TIMELINE-EVIDENCE/Medical/Prescriptions"),
    (r"^appointment",                     "TIMELINE-EVIDENCE/Medical/Appointments"),
    (r"^insurance$",                      "TIMELINE-EVIDENCE/Medical/Insurance"),
    # ── Housing ──
    (r"^hous",                            "TIMELINE-EVIDENCE/Housing"),
    (r"^rent",                            "TIMELINE-EVIDENCE/Housing/Rent-Payments"),
    (r"^voucher",                         "TIMELINE-EVIDENCE/Housing/Vouchers"),
    (r"^hqs",                             "TIMELINE-EVIDENCE/Housing/HQS-Inspections"),
    (r"^inspect",                         "TIMELINE-EVIDENCE/Housing/HQS-Inspections"),
    (r"^property",                        "TIMELINE-EVIDENCE/Housing/Property-Search"),
    # ── Location / Travel ──
    (r"^travel",                          "TIMELINE-EVIDENCE/Location-Activity/Travel-Transport"),
    (r"^transport",                       "TIMELINE-EVIDENCE/Location-Activity/Travel-Transport"),
    (r"^location",                        "TIMELINE-EVIDENCE/Location-Activity"),
    (r"^maps?$",                          "TIMELINE-EVIDENCE/Location-Activity/Google-Maps"),
    (r"^redfin",                          "TIMELINE-EVIDENCE/Location-Activity/Redfin-Property"),
    # ── Music ──
    (r"^music$",                          "MUSIC"),
    (r"^music[/\\]",                      "MUSIC"),
    (r"^collab",                          "MUSIC/Collaborations"),
    (r"^soundcloud",                      "MUSIC/Platforms/SoundCloud"),
    (r"^spotify",                         "MUSIC/Platforms/Spotify"),
    (r"^suno",                            "MUSIC/Platforms/Suno"),
    (r"^lyrics",                          "MUSIC/Lyrics-Drafts"),
    (r"^copyright",                       "MUSIC/Copyright-Legal"),
    (r"^distribut",                       "MUSIC/Distribution"),
    # ── Projects ──
    (r"^project",                         "PROJECTS"),
    (r"^ssrn",                            "PROJECTS/SSRN-Academic"),
    (r"^academ",                          "PROJECTS/SSRN-Academic"),
    (r"^github",                          "PROJECTS/GitHub-Dev"),
    (r"^dev$",                            "PROJECTS/GitHub-Dev"),
    (r"^development",                     "PROJECTS/GitHub-Dev"),
    (r"^coding",                          "PROJECTS/GitHub-Dev"),
    (r"^code$",                           "PROJECTS/GitHub-Dev"),
    (r"^yumyum",                          "PROJECTS/YumYumCode"),
    (r"^tiki",                            "PROJECTS/Tiki-Washbot"),
    (r"^neurooz",                         "PROJECTS/Neurooz"),
    (r"^alt.?text",                       "PROJECTS/Alt-Text-ADA"),
    (r"^app.?idea",                       "PROJECTS/App-Ideas"),
    # ── Job Search ──
    (r"^job",                             "JOB-SEARCH"),
    (r"^work$",                           "JOB-SEARCH"),
    (r"^career",                          "JOB-SEARCH"),
    (r"^employ",                          "JOB-SEARCH"),
    (r"^application",                     "JOB-SEARCH/Applications"),
    (r"^interview",                       "JOB-SEARCH/Interviews"),
    (r"^indeed",                          "JOB-SEARCH/Alerts/Indeed"),
    (r"^linkedin[/\\]job",               "JOB-SEARCH/Alerts/LinkedIn"),
    (r"^job.?alert",                      "JOB-SEARCH/Alerts"),
    (r"^resume",                          "JOB-SEARCH/Applications"),
    # ── API / Credentials ──
    (r"^api",                             "API-KEYS-CREDENTIALS/API-Keys"),
    (r"^key",                             "API-KEYS-CREDENTIALS/API-Keys"),
    (r"^token",                           "API-KEYS-CREDENTIALS/Bot-Tokens"),
    (r"^password",                        "API-KEYS-CREDENTIALS/Passwords"),
    (r"^credential",                      "API-KEYS-CREDENTIALS"),
    (r"^license",                         "API-KEYS-CREDENTIALS/Licenses"),
    # ── Contacts ──
    (r"^contact",                         "CONTACTS"),
    (r"^caresse",                         "CONTACTS/Caresse-Lopez"),
    (r"^church",                          "CONTACTS/Church-One20"),
    (r"^one20",                           "CONTACTS/Church-One20"),
    # ── Orders / Receipts ──
    (r"^order",                           "ORDERS-RECEIPTS"),
    (r"^receipt",                         "ORDERS-RECEIPTS"),
    (r"^purchase",                        "ORDERS-RECEIPTS"),
    (r"^amazon",                          "ORDERS-RECEIPTS/Amazon"),
    (r"^ebay",                            "ORDERS-RECEIPTS/eBay"),
    (r"^etsy",                            "ORDERS-RECEIPTS/Etsy"),
    (r"^google.?play",                    "ORDERS-RECEIPTS/Google-Play"),
    (r"^subscript",                       "ORDERS-RECEIPTS/Subscriptions"),
    (r"^shopping",                        "ORDERS-RECEIPTS/Other-Purchases"),
    # ── Newsletters ──
    (r"^newsletter",                      "NEWSLETTERS"),
    (r"^digest",                          "NEWSLETTERS"),
    (r"^tech.?news",                      "NEWSLETTERS/Tech"),
    # ── Software ──
    (r"^software",                        "SOFTWARE-TRACKING"),
    (r"^trial",                           "SOFTWARE-TRACKING/Trials"),
    (r"^cancel",                          "SOFTWARE-TRACKING/Cancellations"),
    # ── Social Media ──
    (r"^social",                          "SOCIAL-MEDIA"),
    (r"^tiktok",                          "SOCIAL-MEDIA/TikTok"),
    (r"^linkedin$",                       "SOCIAL-MEDIA/LinkedIn"),
    (r"^reddit",                          "SOCIAL-MEDIA/Reddit"),
    (r"^nextdoor",                        "SOCIAL-MEDIA/Nextdoor"),
    # ── Catch-all ──
    (r"^important$",                      "FLAGGED-REVIEW"),
    (r"^review$",                         "FLAGGED-REVIEW"),
    (r"^todo$",                           "FLAGGED-REVIEW"),
    (r"^to.?do$",                         "FLAGGED-REVIEW"),
    (r"^flag",                            "FLAGGED-REVIEW"),
]

# ── Categorization Rules ─────────────────────────────────────────────────────
CATEGORIZATION_RULES = [
    # Self-emails (from AND to same address)
    {
        "name": "Self-Emails",
        "from_pattern": r"angelreporters@gmail\.com",
        "to_pattern": r"angelreporters@gmail\.com",
        "labels": ["TIMELINE-EVIDENCE/Communications-Sent/Self-Emails"],
    },
    # API keys / credentials sent to self
    {
        "name": "API-Keys-Credentials",
        "from_pattern": r"angelreporters",
        "subject_pattern": r"(?i)(api|token|key)",
        "labels": ["API-KEYS-CREDENTIALS/API-Keys"],
    },
    # Sent from angelreporters (but NOT to self — handled above)
    {
        "name": "Sent-To-Contacts",
        "from_pattern": r"angelreporters@gmail\.com",
        "labels": ["TIMELINE-EVIDENCE/Communications-Sent/To-Contacts"],
    },
    # Caresse Lopez
    {
        "name": "Caresse-Lopez",
        "from_pattern": r"lopez\.caresse@gmail\.com",
        "labels": ["CONTACTS/Caresse-Lopez", "MUSIC/Collaborations/Caresse-Rae-Edna"],
    },
    {
        "name": "Caresse-Lopez-To",
        "to_pattern": r"lopez\.caresse@gmail\.com",
        "labels": ["CONTACTS/Caresse-Lopez", "MUSIC/Collaborations/Caresse-Rae-Edna"],
    },
    # GitHub
    {
        "name": "GitHub",
        "from_pattern": r"github\.com",
        "labels": ["PROJECTS/GitHub-Dev"],
    },
    # SSRN
    {
        "name": "SSRN-From",
        "from_pattern": r"ssrn",
        "labels": ["PROJECTS/SSRN-Academic"],
    },
    {
        "name": "SSRN-Subject",
        "subject_pattern": r"(?i)ssrn",
        "labels": ["PROJECTS/SSRN-Academic"],
    },
    # Indeed job alerts
    {
        "name": "Indeed-Jobs",
        "from_pattern": r"indeed",
        "subject_pattern": r"(?i)job",
        "labels": ["JOB-SEARCH/Alerts/Indeed"],
    },
    # LinkedIn job alerts
    {
        "name": "LinkedIn-Jobs",
        "from_pattern": r"linkedin",
        "subject_pattern": r"(?i)job",
        "labels": ["JOB-SEARCH/Alerts/LinkedIn"],
    },
    # Amazon orders
    {
        "name": "Amazon-Orders",
        "from_pattern": r"amazon",
        "subject_pattern": r"(?i)(order|shipment)",
        "labels": ["ORDERS-RECEIPTS/Amazon"],
    },
    # Google Play receipts
    {
        "name": "Google-Play",
        "from_pattern": r"google",
        "subject_pattern": r"(?i)(receipt|purchase)",
        "labels": ["ORDERS-RECEIPTS/Google-Play"],
    },
    # Chase / Banking
    {
        "name": "Chase-Banking",
        "from_pattern": r"chase",
        "labels": ["TIMELINE-EVIDENCE/Financial-Transactions/Banking-Chase"],
    },
    {
        "name": "Bank-General",
        "from_pattern": r"bank",
        "labels": ["TIMELINE-EVIDENCE/Financial-Transactions/Banking-Chase"],
    },
    # Robinhood
    {
        "name": "Robinhood",
        "from_pattern": r"robinhood",
        "labels": ["TIMELINE-EVIDENCE/Financial-Transactions/Robinhood-Investments"],
    },
    # UC Health
    {
        "name": "UC-Health",
        "from_pattern": r"uchealth",
        "labels": ["TIMELINE-EVIDENCE/Medical/UC-Health"],
    },
    # IRS
    {
        "name": "IRS",
        "subject_pattern": r"(?i)\bIRS\b",
        "labels": ["TIMELINE-EVIDENCE/Government/IRS"],
    },
    # SSA / Social Security
    {
        "name": "SSA",
        "subject_pattern": r"(?i)(SSA|Social\s+Security)",
        "labels": ["TIMELINE-EVIDENCE/Government/SSA"],
    },
    # Medicaid / Medicare
    {
        "name": "Medicaid-Medicare",
        "subject_pattern": r"(?i)(medicaid|medicare)",
        "labels": ["TIMELINE-EVIDENCE/Government/Medicaid-Medicare"],
    },
    # Redfin
    {
        "name": "Redfin",
        "from_pattern": r"redfin",
        "labels": ["TIMELINE-EVIDENCE/Location-Activity/Redfin-Property"],
    },
    # HQS / Inspections
    {
        "name": "HQS-Inspections",
        "subject_pattern": r"(?i)(HQS|inspection)",
        "labels": ["TIMELINE-EVIDENCE/Housing/HQS-Inspections"],
    },
    # SoundCloud
    {
        "name": "SoundCloud",
        "from_pattern": r"soundcloud",
        "labels": ["MUSIC/Platforms/SoundCloud"],
    },
    # Spotify
    {
        "name": "Spotify",
        "from_pattern": r"spotify",
        "labels": ["MUSIC/Platforms/Spotify"],
    },
    # Church One20
    {
        "name": "Church-One20",
        "from_pattern": r"(one20|dusty)",
        "labels": ["CONTACTS/Church-One20"],
    },
    # TikTok
    {
        "name": "TikTok",
        "from_pattern": r"tiktok",
        "labels": ["SOCIAL-MEDIA/TikTok"],
    },
    # LinkedIn (general — after job-specific rule)
    {
        "name": "LinkedIn",
        "from_pattern": r"linkedin",
        "labels": ["SOCIAL-MEDIA/LinkedIn"],
    },
    # Reddit
    {
        "name": "Reddit",
        "from_pattern": r"reddit",
        "labels": ["SOCIAL-MEDIA/Reddit"],
    },
    # Nextdoor
    {
        "name": "Nextdoor",
        "from_pattern": r"nextdoor",
        "labels": ["SOCIAL-MEDIA/Nextdoor"],
    },
    # eBay
    {
        "name": "eBay",
        "from_pattern": r"ebay",
        "labels": ["ORDERS-RECEIPTS/eBay"],
    },
    # Etsy
    {
        "name": "Etsy",
        "from_pattern": r"etsy",
        "labels": ["ORDERS-RECEIPTS/Etsy"],
    },
    # Legal / Court
    {
        "name": "Legal-Court",
        "subject_pattern": r"(?i)(court|attorney|legal|subpoena)",
        "labels": ["TIMELINE-EVIDENCE/Legal-Court"],
    },
    # Newsletters catch-all (has:unsubscribe equivalent)
    {
        "name": "Newsletters",
        "has_unsubscribe": True,
        "labels": ["NEWSLETTERS"],
    },
]


# ── Logging Setup ────────────────────────────────────────────────────────────
def setup_logging(log_file: str = LOG_FILE) -> logging.Logger:
    """Configure dual logging: file + colored console."""
    logger = logging.getLogger("gmail_organizer")
    logger.setLevel(logging.DEBUG)
    # Prevent duplicate handlers on re-import
    if logger.handlers:
        return logger

    fh = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(ColorFormatter())
    logger.addHandler(ch)

    return logger


class ColorFormatter(logging.Formatter):
    """Colored log formatter for terminal output."""
    LEVEL_COLORS = {
        logging.DEBUG:    C.GRAY,
        logging.INFO:     C.CYAN,
        logging.WARNING:  C.YELLOW,
        logging.ERROR:    C.RED,
        logging.CRITICAL: C.RED + C.BOLD,
    }

    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, C.RESET)
        ts = datetime.now().strftime("%H:%M:%S")
        return f"{C.GRAY}{ts}{C.RESET} {color}{record.levelname:<8}{C.RESET} {record.getMessage()}"


# ── Gmail API Helpers ────────────────────────────────────────────────────────
def authenticate(credentials_file: str = CREDENTIALS_FILE,
                 token_file: str = TOKEN_FILE) -> Credentials:
    """Authenticate via OAuth2, opening browser on first run."""
    creds = None
    if os.path.exists(token_file):
        with open(token_file, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_file):
                print(f"\n{C.RED}{C.BOLD}[FATAL]{C.RESET} '{credentials_file}' not found!")
                print(f"  See {C.CYAN}credentials_setup.md{C.RESET} for setup instructions.\n")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, "wb") as f:
            pickle.dump(creds, f)
    return creds


def api_call_with_backoff(func, *args, max_retries=MAX_RETRIES, **kwargs):
    """Execute an API call with exponential backoff on rate-limit errors."""
    logger = logging.getLogger("gmail_organizer")
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except HttpError as e:
            if e.resp.status in (429, 500, 503):
                delay = BASE_DELAY * (2 ** attempt)
                logger.warning(
                    f"Rate limited (HTTP {e.resp.status}). "
                    f"Retry {attempt+1}/{max_retries} in {delay:.1f}s..."
                )
                time.sleep(delay)
            else:
                raise
    raise RuntimeError(f"API call failed after {max_retries} retries")


# ── Label Management ─────────────────────────────────────────────────────────
def get_existing_labels(service) -> dict:
    """Return dict mapping label name → label id for all existing labels."""
    results = api_call_with_backoff(
        service.users().labels().list(userId="me").execute
    )
    labels = results.get("labels", [])
    return {lbl["name"]: lbl["id"] for lbl in labels}


def get_existing_labels_full(service) -> list:
    """Return full label objects list from the API."""
    results = api_call_with_backoff(
        service.users().labels().list(userId="me").execute
    )
    return results.get("labels", [])


def create_labels(service, label_names: list, logger: logging.Logger) -> dict:
    """Create all labels from the hierarchy. Returns name→id mapping."""
    existing = get_existing_labels(service)
    label_map = dict(existing)
    created_count = 0
    skipped_count = 0

    print(f"\n{C.BG_BLUE}{C.WHITE}{C.BOLD} LABEL CREATION {C.RESET}")
    print(f"{C.CYAN}{'─' * 60}{C.RESET}")

    for label_name in label_names:
        if label_name in label_map:
            logger.debug(f"Label exists: {label_name}")
            skipped_count += 1
            continue

        body = {
            "name": label_name,
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show",
        }
        try:
            result = api_call_with_backoff(
                service.users().labels().create(userId="me", body=body).execute
            )
            label_map[label_name] = result["id"]
            created_count += 1
            logger.info(f"{C.GREEN}✓{C.RESET} Created: {C.BOLD}{label_name}{C.RESET}")
        except HttpError as e:
            if "already exists" in str(e).lower():
                logger.debug(f"Label already exists (race): {label_name}")
                skipped_count += 1
                existing = get_existing_labels(service)
                label_map.update(existing)
            else:
                logger.error(f"Failed to create label '{label_name}': {e}")

    print(f"\n{C.GREEN}{C.BOLD}Labels created: {created_count}{C.RESET}")
    print(f"{C.YELLOW}Labels skipped (already exist): {skipped_count}{C.RESET}")
    print(f"{C.CYAN}Total labels in hierarchy: {len(label_names)}{C.RESET}\n")

    return label_map


# ── Email Categorization ─────────────────────────────────────────────────────
def extract_header(headers: list, name: str) -> str:
    """Extract a header value from the message headers list."""
    for h in headers:
        if h["name"].lower() == name.lower():
            return h.get("value", "")
    return ""


def categorize_message(headers: list) -> list:
    """
    Determine which labels to apply based on message headers.
    Returns a list of label names. Multiple labels can be applied.
    """
    from_addr = extract_header(headers, "From").lower()
    to_addr = extract_header(headers, "To").lower()
    subject = extract_header(headers, "Subject")
    list_unsub = extract_header(headers, "List-Unsubscribe")

    matched_labels = []

    for rule in CATEGORIZATION_RULES:
        match = True

        if "from_pattern" in rule:
            if not re.search(rule["from_pattern"], from_addr, re.IGNORECASE):
                match = False

        if "to_pattern" in rule:
            if not re.search(rule["to_pattern"], to_addr, re.IGNORECASE):
                match = False

        if "subject_pattern" in rule:
            if not re.search(rule["subject_pattern"], subject):
                match = False

        if "has_unsubscribe" in rule and rule["has_unsubscribe"]:
            if not list_unsub:
                match = False

        if match:
            for lbl in rule["labels"]:
                if lbl not in matched_labels:
                    matched_labels.append(lbl)

    if not matched_labels:
        matched_labels.append("FLAGGED-REVIEW")

    return matched_labels


def apply_labels(service, message_id: str, label_ids: list, logger: logging.Logger,
                 remove_label_ids: list = None):
    """Apply label IDs to a message, optionally removing old labels."""
    body = {
        "addLabelIds": label_ids,
        "removeLabelIds": remove_label_ids or [],
    }
    try:
        api_call_with_backoff(
            service.users().messages().modify(
                userId="me", id=message_id, body=body
            ).execute
        )
    except HttpError as e:
        logger.error(f"Failed to label message {message_id}: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# ██  MIGRATION ENGINE  ██
# ══════════════════════════════════════════════════════════════════════════════

def map_old_label_to_new(old_label_name: str) -> Optional[str]:
    """
    Given an old label name, return the best matching new hierarchy label.
    Returns None if no mapping is found.
    """
    # Skip system labels
    system_prefixes = ("CATEGORY_", "IMPORTANT", "CHAT", "SENT", "INBOX",
                       "TRASH", "DRAFT", "SPAM", "STARRED", "UNREAD")
    if old_label_name.upper().startswith(system_prefixes):
        return None

    # Skip labels that are already part of our hierarchy
    hierarchy_set = set(LABEL_HIERARCHY)
    if old_label_name in hierarchy_set:
        return None

    # Check if it's a child of an existing hierarchy label
    for h_label in LABEL_HIERARCHY:
        if old_label_name.startswith(h_label + "/"):
            return None

    # Try pattern matching
    # Get the leaf name for matching (last segment if nested)
    leaf_name = old_label_name.rsplit("/", 1)[-1] if "/" in old_label_name else old_label_name

    for pattern, new_label in MIGRATION_MAP:
        if re.search(pattern, leaf_name, re.IGNORECASE):
            return new_label
        # Also try the full path
        if re.search(pattern, old_label_name, re.IGNORECASE):
            return new_label

    return None


def discover_migration_targets(service, logger: logging.Logger) -> list:
    """
    Scan all existing labels and build a migration plan.
    Returns list of dicts: {old_name, old_id, new_name, message_count}
    """
    all_labels = get_existing_labels_full(service)
    hierarchy_set = set(LABEL_HIERARCHY)
    migration_plan = []

    for lbl in all_labels:
        lbl_name = lbl["name"]
        lbl_id = lbl["id"]
        lbl_type = lbl.get("type", "user")

        # Skip system labels
        if lbl_type == "system":
            continue

        # Skip labels already in our hierarchy
        if lbl_name in hierarchy_set:
            continue

        # Skip labels that are children of our hierarchy
        is_child = False
        for h_label in LABEL_HIERARCHY:
            if lbl_name.startswith(h_label + "/"):
                is_child = True
                break
        if is_child:
            continue

        new_label = map_old_label_to_new(lbl_name)
        if new_label:
            # Get message count for this label
            try:
                label_info = api_call_with_backoff(
                    service.users().labels().get(userId="me", id=lbl_id).execute
                )
                msg_total = label_info.get("messagesTotal", 0)
            except Exception:
                msg_total = 0

            migration_plan.append({
                "old_name": lbl_name,
                "old_id": lbl_id,
                "new_name": new_label,
                "message_count": msg_total,
            })

    return migration_plan


def print_migration_plan(plan: list):
    """Print a colored migration plan table."""
    print(f"\n{C.BG_MAGENTA}{C.WHITE}{C.BOLD} MIGRATION PLAN {C.RESET}")
    print(f"{C.CYAN}{'─' * 80}{C.RESET}")

    if not plan:
        print(f"  {C.GREEN}No existing labels need migration.{C.RESET}")
        print(f"  All labels are either system labels or already in the new hierarchy.\n")
        return

    print(f"  {'Old Label':<30} {'→':^3} {'New Label':<35} {'Emails':>6}")
    print(f"  {'─'*30} {'─':^3} {'─'*35} {'─'*6}")

    total_emails = 0
    for entry in plan:
        old = entry["old_name"][:30]
        new = entry["new_name"][:35]
        count = entry["message_count"]
        total_emails += count
        color = C.GREEN if count > 0 else C.GRAY
        print(f"  {C.YELLOW}{old:<30}{C.RESET} {C.CYAN}→{C.RESET} {C.GREEN}{new:<35}{C.RESET} {color}{count:>6}{C.RESET}")

    print(f"\n  {C.BOLD}Total labels to migrate: {len(plan)}{C.RESET}")
    print(f"  {C.BOLD}Total emails to move:    {total_emails}{C.RESET}\n")


def execute_migration(service, plan: list, label_map: dict,
                      logger: logging.Logger, dry_run: bool = False) -> dict:
    """
    Execute the migration: for each old label, fetch all messages,
    apply the new label, and remove the old label.
    Returns migration stats.
    """
    stats = {
        "labels_migrated": 0,
        "emails_moved": 0,
        "errors": 0,
        "details": [],  # list of {old, new, count}
    }

    print(f"\n{C.BG_GREEN}{C.WHITE}{C.BOLD} EXECUTING MIGRATION {C.RESET}")
    if dry_run:
        print(f"  {C.YELLOW}{C.BOLD}⚠ DRY RUN — no changes will be made{C.RESET}")
    print(f"{C.CYAN}{'─' * 60}{C.RESET}")

    for i, entry in enumerate(plan):
        old_name = entry["old_name"]
        old_id = entry["old_id"]
        new_name = entry["new_name"]
        expected = entry["message_count"]

        new_id = label_map.get(new_name)
        if not new_id:
            logger.error(f"New label '{new_name}' not found in label_map — skipping")
            stats["errors"] += 1
            continue

        print(f"\n  {C.MAGENTA}[{i+1}/{len(plan)}]{C.RESET} "
              f"{C.YELLOW}{old_name}{C.RESET} → {C.GREEN}{new_name}{C.RESET} "
              f"({expected} emails)")

        # Fetch all messages with the old label
        moved_count = 0
        page_token = None

        while True:
            try:
                kwargs = {
                    "userId": "me",
                    "labelIds": [old_id],
                    "maxResults": BATCH_SIZE,
                }
                if page_token:
                    kwargs["pageToken"] = page_token

                results = api_call_with_backoff(
                    service.users().messages().list(**kwargs).execute
                )
            except Exception as e:
                logger.error(f"Failed to list messages for label '{old_name}': {e}")
                stats["errors"] += 1
                break

            messages = results.get("messages", [])
            if not messages:
                break

            for msg_stub in messages:
                msg_id = msg_stub["id"]
                if not dry_run:
                    apply_labels(
                        service, msg_id,
                        label_ids=[new_id],
                        logger=logger,
                        remove_label_ids=[old_id],
                    )
                moved_count += 1

                if moved_count % 50 == 0:
                    print(f"    {C.GRAY}...moved {moved_count} emails{C.RESET}")

            page_token = results.get("nextPageToken")
            if not page_token:
                break

        stats["emails_moved"] += moved_count
        stats["labels_migrated"] += 1
        stats["details"].append({
            "old": old_name,
            "new": new_name,
            "count": moved_count,
        })

        logger.info(f"Migrated {moved_count} emails: {old_name} → {new_name}")
        print(f"    {C.GREEN}✓ Moved {moved_count} emails{C.RESET}")

    return stats


def print_migration_report(stats: dict):
    """Print a detailed migration report."""
    print(f"\n{C.BG_YELLOW}{C.WHITE}{C.BOLD} MIGRATION REPORT {C.RESET}")
    print(f"{C.CYAN}{'─' * 80}{C.RESET}")

    if stats["details"]:
        print(f"\n  {'Old Label':<30} {'→':^3} {'New Label':<30} {'Moved':>6}")
        print(f"  {'─'*30} {'─':^3} {'─'*30} {'─'*6}")

        for d in stats["details"]:
            old = d["old"][:30]
            new = d["new"][:30]
            count = d["count"]
            color = C.GREEN if count > 0 else C.GRAY
            print(f"  {C.YELLOW}{old:<30}{C.RESET} {C.CYAN}→{C.RESET} "
                  f"{C.GREEN}{new:<30}{C.RESET} {color}{count:>6}{C.RESET}")

    print(f"\n  {C.GREEN}{C.BOLD}Labels migrated : {stats['labels_migrated']}{C.RESET}")
    print(f"  {C.GREEN}{C.BOLD}Emails moved    : {stats['emails_moved']}{C.RESET}")
    print(f"  {C.RED}Errors          : {stats['errors']}{C.RESET}")
    print(f"{C.CYAN}{'─' * 80}{C.RESET}\n")


def cleanup_empty_labels(service, plan: list, logger: logging.Logger,
                         dry_run: bool = False) -> int:
    """
    Offer to remove old labels that are now empty after migration.
    Returns count of labels removed.
    """
    print(f"\n{C.BG_RED}{C.WHITE}{C.BOLD} CLEANUP: EMPTY OLD LABELS {C.RESET}")
    print(f"{C.CYAN}{'─' * 60}{C.RESET}")

    empty_labels = []
    for entry in plan:
        try:
            label_info = api_call_with_backoff(
                service.users().labels().get(
                    userId="me", id=entry["old_id"]
                ).execute
            )
            msg_total = label_info.get("messagesTotal", 0)
            if msg_total == 0:
                empty_labels.append(entry)
        except HttpError as e:
            if e.resp.status == 404:
                continue  # already deleted
            logger.warning(f"Could not check label '{entry['old_name']}': {e}")

    if not empty_labels:
        print(f"  {C.GREEN}No empty old labels to clean up.{C.RESET}\n")
        return 0

    print(f"  Found {C.BOLD}{len(empty_labels)}{C.RESET} empty old labels:\n")
    for lbl in empty_labels:
        print(f"    {C.YELLOW}• {lbl['old_name']}{C.RESET}")

    if dry_run:
        print(f"\n  {C.YELLOW}DRY RUN — would delete {len(empty_labels)} labels.{C.RESET}\n")
        return 0

    # In non-interactive mode, skip deletion (safety first)
    # Labels are left in place — user can delete manually or re-run with --cleanup
    print(f"\n  {C.YELLOW}Old labels preserved (not deleted).{C.RESET}")
    print(f"  {C.GRAY}To remove them, use --cleanup flag after confirming migration.{C.RESET}\n")
    return 0


def force_cleanup_empty_labels(service, plan: list, logger: logging.Logger) -> int:
    """Actually delete empty old labels. Called with --cleanup flag."""
    removed = 0
    for entry in plan:
        try:
            label_info = api_call_with_backoff(
                service.users().labels().get(
                    userId="me", id=entry["old_id"]
                ).execute
            )
            msg_total = label_info.get("messagesTotal", 0)
            if msg_total == 0:
                api_call_with_backoff(
                    service.users().labels().delete(
                        userId="me", id=entry["old_id"]
                    ).execute
                )
                logger.info(f"Deleted empty label: {entry['old_name']}")
                print(f"  {C.RED}✗{C.RESET} Deleted: {C.YELLOW}{entry['old_name']}{C.RESET}")
                removed += 1
        except HttpError as e:
            if e.resp.status == 404:
                continue
            logger.warning(f"Could not delete label '{entry['old_name']}': {e}")

    print(f"\n  {C.GREEN}{C.BOLD}Removed {removed} empty labels.{C.RESET}\n")
    return removed


# ── Main Processing ──────────────────────────────────────────────────────────
def process_all_emails(service, label_map: dict, logger: logging.Logger,
                       dry_run: bool = False, max_messages: int = 0):
    """Fetch and categorize ALL emails in the mailbox."""
    print(f"\n{C.BG_GREEN}{C.WHITE}{C.BOLD} EMAIL PROCESSING {C.RESET}")
    print(f"{C.CYAN}{'─' * 60}{C.RESET}")

    stats = {
        "total_processed": 0,
        "total_labeled": 0,
        "total_errors": 0,
        "label_counts": {},
        "flagged_review": 0,
    }

    page_token = None
    page_num = 0

    while True:
        page_num += 1
        logger.info(f"Fetching page {page_num} of messages...")

        try:
            kwargs = {"userId": "me", "maxResults": BATCH_SIZE}
            if page_token:
                kwargs["pageToken"] = page_token

            results = api_call_with_backoff(
                service.users().messages().list(**kwargs).execute
            )
        except Exception as e:
            logger.error(f"Failed to list messages: {e}")
            break

        messages = results.get("messages", [])
        if not messages:
            logger.info("No more messages to process.")
            break

        for i, msg_stub in enumerate(messages):
            msg_id = msg_stub["id"]
            stats["total_processed"] += 1
            count = stats["total_processed"]

            if count % 50 == 0 or count == 1:
                print(
                    f"  {C.MAGENTA}▸{C.RESET} Processing message "
                    f"{C.BOLD}{count}{C.RESET}..."
                )

            try:
                msg = api_call_with_backoff(
                    service.users().messages().get(
                        userId="me", id=msg_id, format="metadata",
                        metadataHeaders=["From", "To", "Subject", "List-Unsubscribe"]
                    ).execute
                )
            except Exception as e:
                logger.error(f"Failed to fetch message {msg_id}: {e}")
                stats["total_errors"] += 1
                continue

            headers = msg.get("payload", {}).get("headers", [])
            matched_labels = categorize_message(headers)

            label_ids = []
            for lbl_name in matched_labels:
                lid = label_map.get(lbl_name)
                if lid:
                    label_ids.append(lid)
                    stats["label_counts"][lbl_name] = stats["label_counts"].get(lbl_name, 0) + 1
                else:
                    logger.warning(f"Label '{lbl_name}' not found in label_map")

            if "FLAGGED-REVIEW" in matched_labels:
                stats["flagged_review"] += 1

            from_val = extract_header(headers, "From")[:50]
            subj_val = extract_header(headers, "Subject")[:50]
            logger.debug(
                f"[{count}] From: {from_val} | Subject: {subj_val} "
                f"→ {matched_labels}"
            )

            if label_ids and not dry_run:
                apply_labels(service, msg_id, label_ids, logger)
                stats["total_labeled"] += 1

            if max_messages > 0 and count >= max_messages:
                logger.info(f"Reached max_messages limit ({max_messages}). Stopping.")
                return stats

        page_token = results.get("nextPageToken")
        if not page_token:
            break

    return stats


def print_summary(stats: dict):
    """Print a colorful summary of processing results."""
    print(f"\n{C.BG_YELLOW}{C.WHITE}{C.BOLD} PROCESSING SUMMARY {C.RESET}")
    print(f"{C.CYAN}{'─' * 60}{C.RESET}")
    print(f"  {C.GREEN}Total processed :{C.RESET} {C.BOLD}{stats['total_processed']}{C.RESET}")
    print(f"  {C.GREEN}Total labeled   :{C.RESET} {C.BOLD}{stats['total_labeled']}{C.RESET}")
    print(f"  {C.YELLOW}Flagged review  :{C.RESET} {C.BOLD}{stats['flagged_review']}{C.RESET}")
    print(f"  {C.RED}Errors          :{C.RESET} {C.BOLD}{stats['total_errors']}{C.RESET}")

    if stats["label_counts"]:
        print(f"\n  {C.CYAN}{C.BOLD}Label Distribution:{C.RESET}")
        sorted_labels = sorted(stats["label_counts"].items(), key=lambda x: -x[1])
        for label, count in sorted_labels:
            bar = "█" * min(count, 40)
            print(f"    {C.BLUE}{label:<55}{C.RESET} {C.GREEN}{count:>5}{C.RESET} {C.MAGENTA}{bar}{C.RESET}")

    print(f"\n{C.CYAN}{'─' * 60}{C.RESET}")
    print(f"  {C.GREEN}{C.BOLD}✓ Complete!{C.RESET} Log saved to {C.CYAN}{LOG_FILE}{C.RESET}\n")


# ── Banner ───────────────────────────────────────────────────────────────────
def print_banner():
    """Print the application banner."""
    banner = f"""
{C.CYAN}{C.BOLD}╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   ██████╗ ███╗   ███╗ █████╗ ██╗██╗                     ║
║  ██╔════╝ ████╗ ████║██╔══██╗██║██║                     ║
║  ██║  ███╗██╔████╔██║███████║██║██║                     ║
║  ██║   ██║██║╚██╔╝██║██╔══██║██║██║                     ║
║  ╚██████╔╝██║ ╚═╝ ██║██║  ██║██║███████╗                ║
║   ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝                ║
║                                                          ║
║   {C.WHITE}O R G A N I Z E R{C.CYAN}   v{VERSION}                         ║
║   {C.GRAY}Automated Email Labeling, Sorting & Migration{C.CYAN}          ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝{C.RESET}
"""
    print(banner)


# ── CLI Entry Point ──────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Gmail Organizer — Automated Email Labeling, Sorting & Migration"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would happen without making any changes"
    )
    parser.add_argument(
        "--labels-only", action="store_true",
        help="Only create labels, don't process emails"
    )
    parser.add_argument(
        "--migrate", action="store_true",
        help="Migration mode: map existing labels to new hierarchy and move emails"
    )
    parser.add_argument(
        "--cleanup", action="store_true",
        help="After migration, delete old labels that are now empty"
    )
    parser.add_argument(
        "--max-messages", type=int, default=0,
        help="Maximum number of messages to process (0 = all)"
    )
    parser.add_argument(
        "--credentials", type=str, default=CREDENTIALS_FILE,
        help=f"Path to OAuth credentials JSON (default: {CREDENTIALS_FILE})"
    )
    parser.add_argument(
        "--token", type=str, default=TOKEN_FILE,
        help=f"Path to token pickle file (default: {TOKEN_FILE})"
    )
    parser.add_argument(
        "--version", action="version", version=f"Gmail Organizer v{VERSION}"
    )
    args = parser.parse_args()

    # Setup
    print_banner()
    logger = setup_logging()
    logger.info(f"Gmail Organizer v{VERSION} starting...")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"Mode: {'MIGRATE' if args.migrate else 'NORMAL'}"
                f"{' (DRY RUN)' if args.dry_run else ''}")

    if args.dry_run:
        print(f"  {C.YELLOW}{C.BOLD}⚠ DRY RUN MODE — no changes will be made{C.RESET}\n")
        logger.info("DRY RUN MODE enabled")

    # Authenticate
    print(f"{C.CYAN}Authenticating with Gmail API...{C.RESET}")
    creds = authenticate(args.credentials, args.token)
    service = build("gmail", "v1", credentials=creds)
    logger.info("Authentication successful")
    print(f"{C.GREEN}✓ Authenticated successfully{C.RESET}\n")

    # Create labels (always — ensures hierarchy exists)
    label_map = create_labels(service, LABEL_HIERARCHY, logger)
    logger.info(f"Label map contains {len(label_map)} labels")

    if args.labels_only:
        print(f"\n{C.GREEN}{C.BOLD}✓ Labels created. Exiting (--labels-only).{C.RESET}\n")
        return

    # ── MIGRATION MODE ───────────────────────────────────────────────────
    if args.migrate:
        print(f"\n{C.BG_MAGENTA}{C.WHITE}{C.BOLD} MIGRATION MODE ACTIVATED {C.RESET}\n")
        logger.info("Starting migration: discovering existing labels...")

        # Step 1: Discover what needs to be migrated
        migration_plan = discover_migration_targets(service, logger)
        print_migration_plan(migration_plan)

        if migration_plan:
            # Step 2: Execute migration
            migration_stats = execute_migration(
                service, migration_plan, label_map, logger,
                dry_run=args.dry_run
            )
            print_migration_report(migration_stats)

            # Save migration report to JSON
            report_file = "migration_report.json"
            with open(report_file, "w") as f:
                json.dump(migration_stats, f, indent=2)
            logger.info(f"Migration report saved to {report_file}")

            # Step 3: Cleanup check
            if args.cleanup and not args.dry_run:
                force_cleanup_empty_labels(service, migration_plan, logger)
            else:
                cleanup_empty_labels(
                    service, migration_plan, logger, dry_run=args.dry_run
                )

        # Step 4: After migration, run normal categorization on remaining
        print(f"\n{C.CYAN}Now running normal categorization on all emails...{C.RESET}")

    # ── NORMAL PROCESSING ────────────────────────────────────────────────
    stats = process_all_emails(
        service, label_map, logger,
        dry_run=args.dry_run,
        max_messages=args.max_messages,
    )

    # Summary
    print_summary(stats)

    # Save stats to JSON
    stats_file = "organizer_stats.json"
    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=2)
    logger.info(f"Stats saved to {stats_file}")


if __name__ == "__main__":
    main()
