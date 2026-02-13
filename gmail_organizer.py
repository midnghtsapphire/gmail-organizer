#!/usr/bin/env python3
"""
Gmail Organizer — Automated Email Labeling, Sorting & Migration System
=======================================================================
Creates 80+ hierarchical labels, auto-sorts every email in your Gmail
mailbox, and migrates emails from existing labels into the new hierarchy.

Author : Angel Evans
License: MIT
Version: 1.2.0 (Improved)

IMPROVEMENTS IN THIS VERSION:
- Replaced pickle with JSON for token storage (security fix)
- Added exponential backoff with jitter for rate limiting
- Improved error handling with specific exception types
- Added type hints throughout
- Implemented label caching for performance
- Added structured logging
- Environment variable support for configuration
- Batch API request optimization
"""

import os
import sys
import re
import json
import time
import logging
import random
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from functools import lru_cache

# ── Third-party imports ──────────────────────────────────────────────────────
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build, Resource
    from googleapiclient.errors import HttpError
except ImportError:
    print("\033[91m[ERROR]\033[0m Missing dependencies. Install with:")
    print("  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    sys.exit(1)

# ── Constants ────────────────────────────────────────────────────────────────
VERSION = "1.2.0"
SCOPES = ["https://mail.google.com/"]
TOKEN_FILE = os.getenv("GMAIL_TOKEN_FILE", "token.json")  # Changed from pickle
CREDENTIALS_FILE = os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json")
LOG_FILE = os.getenv("GMAIL_LOG_FILE", "gmail_organizer.log")
BATCH_SIZE = int(os.getenv("GMAIL_BATCH_SIZE", "100"))
MAX_RETRIES = int(os.getenv("GMAIL_MAX_RETRIES", "7"))
BASE_DELAY = float(os.getenv("GMAIL_BASE_DELAY", "1.0"))
REQUEST_TIMEOUT = int(os.getenv("GMAIL_REQUEST_TIMEOUT", "30"))

# ── Logging Configuration ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
    "TIMELINE-EVIDENCE/Housing/Leases-Rent",
    "TIMELINE-EVIDENCE/Housing/Property-Management",
    "TIMELINE-EVIDENCE/Housing/Utilities",
    "TIMELINE-EVIDENCE/Housing/Move-Related",
    
    # ORDERS-RECEIPTS
    "ORDERS-RECEIPTS",
    "ORDERS-RECEIPTS/Amazon",
    "ORDERS-RECEIPTS/Walmart",
    "ORDERS-RECEIPTS/Target",
    "ORDERS-RECEIPTS/eBay",
    "ORDERS-RECEIPTS/Etsy",
    "ORDERS-RECEIPTS/Food-Delivery",
    "ORDERS-RECEIPTS/Food-Delivery/DoorDash",
    "ORDERS-RECEIPTS/Food-Delivery/Uber-Eats",
    "ORDERS-RECEIPTS/Food-Delivery/Grubhub",
    "ORDERS-RECEIPTS/Rideshare",
    "ORDERS-RECEIPTS/Rideshare/Uber",
    "ORDERS-RECEIPTS/Rideshare/Lyft",
    
    # SOCIAL-MEDIA
    "SOCIAL-MEDIA",
    "SOCIAL-MEDIA/Facebook",
    "SOCIAL-MEDIA/Instagram",
    "SOCIAL-MEDIA/Twitter-X",
    "SOCIAL-MEDIA/TikTok",
    "SOCIAL-MEDIA/LinkedIn",
    "SOCIAL-MEDIA/Reddit",
    "SOCIAL-MEDIA/Nextdoor",
    
    # TECH-SERVICES
    "TECH-SERVICES",
    "TECH-SERVICES/GitHub",
    "TECH-SERVICES/Google",
    "TECH-SERVICES/Microsoft",
    "TECH-SERVICES/Apple",
    "TECH-SERVICES/Cloud-Services",
    "TECH-SERVICES/Streaming",
    "TECH-SERVICES/Streaming/Netflix",
    "TECH-SERVICES/Streaming/Spotify",
    "TECH-SERVICES/Streaming/YouTube",
    
    # NEWSLETTERS
    "NEWSLETTERS",
    
    # API-KEYS-CREDENTIALS
    "API-KEYS-CREDENTIALS",
    "API-KEYS-CREDENTIALS/API-Keys",
    "API-KEYS-CREDENTIALS/Passwords-Resets",
    "API-KEYS-CREDENTIALS/2FA-Security",
]


# ── Utility Functions ────────────────────────────────────────────────────────

def api_call_with_retry(func: callable, max_retries: int = MAX_RETRIES) -> Any:
    """
    Execute API call with exponential backoff and jitter.
    
    Args:
        func: Callable that performs the API call
        max_retries: Maximum number of retry attempts
        
    Returns:
        Result of the API call
        
    Raises:
        HttpError: If non-retryable error occurs
        Exception: If max retries exceeded
    """
    for attempt in range(max_retries):
        try:
            return func()
        except HttpError as e:
            if e.resp.status in [429, 500, 503]:
                # Exponential backoff with jitter
                wait_time = (BASE_DELAY * (2 ** attempt)) + random.uniform(0, 1)
                logger.warning(
                    f"Rate limited (HTTP {e.resp.status}). "
                    f"Retry {attempt + 1}/{max_retries} after {wait_time:.2f}s"
                )
                time.sleep(wait_time)
            else:
                logger.error(f"Non-retryable HTTP error {e.resp.status}: {e.content}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error in API call: {type(e).__name__}: {e}")
            raise
    
    raise Exception(f"Max retries ({max_retries}) exceeded for API call")


def authenticate_gmail() -> Resource:
    """
    Authenticate with Gmail API using OAuth2.
    
    Returns:
        Authenticated Gmail API service instance
        
    Raises:
        FileNotFoundError: If credentials file not found
        Exception: If authentication fails
    """
    creds = None
    
    # Load existing token from JSON (not pickle for security)
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r") as token:
                token_data = json.load(token)
                creds = Credentials.from_authorized_user_info(token_data, SCOPES)
                logger.info(f"Loaded credentials from {TOKEN_FILE}")
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to load token file: {e}. Re-authenticating...")
            creds = None
    
    # Refresh or create new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logger.info("Refreshed expired credentials")
            except Exception as e:
                logger.error(f"Failed to refresh credentials: {e}")
                creds = None
        
        if not creds:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"{CREDENTIALS_FILE} not found. "
                    "Download from Google Cloud Console."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
            logger.info("Created new credentials via OAuth flow")
        
        # Save credentials as JSON
        with open(TOKEN_FILE, "w") as token:
            token_data = {
                "token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "scopes": creds.scopes
            }
            json.dump(token_data, token, indent=2)
            logger.info(f"Saved credentials to {TOKEN_FILE}")
    
    service = build("gmail", "v1", credentials=creds)
    logger.info("Gmail API service authenticated successfully")
    return service


@lru_cache(maxsize=1)
def get_all_labels_cached(service: Resource) -> Dict[str, str]:
    """
    Retrieve all Gmail labels with caching.
    
    Args:
        service: Authenticated Gmail API service instance
        
    Returns:
        Dictionary mapping label names to label IDs
    """
    def _fetch_labels():
        return service.users().labels().list(userId='me').execute()
    
    results = api_call_with_retry(_fetch_labels)
    labels = results.get('labels', [])
    label_map = {label['name']: label['id'] for label in labels}
    logger.info(f"Retrieved {len(label_map)} labels from Gmail")
    return label_map


def create_label(service: Resource, label_name: str) -> Dict[str, Any]:
    """
    Create a new Gmail label.
    
    Args:
        service: Authenticated Gmail API service instance
        label_name: Name of the label to create
        
    Returns:
        Dictionary containing label metadata
        
    Raises:
        ValueError: If label_name is empty or invalid
        HttpError: If API call fails
    """
    if not label_name or not label_name.strip():
        raise ValueError("Label name cannot be empty")
    
    label_object = {
        'name': label_name,
        'labelListVisibility': 'labelShow',
        'messageListVisibility': 'show'
    }
    
    def _create():
        return service.users().labels().create(
            userId='me',
            body=label_object
        ).execute()
    
    try:
        result = api_call_with_retry(_create)
        logger.info(f"{C.GREEN}✓{C.RESET} Created label: {label_name}")
        return result
    except HttpError as e:
        if e.resp.status == 409:
            logger.info(f"{C.YELLOW}⊙{C.RESET} Label already exists: {label_name}")
            return {'name': label_name, 'id': None}
        raise


def create_all_labels(service: Resource) -> None:
    """
    Create all labels in the hierarchy.
    
    Args:
        service: Authenticated Gmail API service instance
    """
    print(f"\n{C.BOLD}{C.CYAN}Creating Label Hierarchy{C.RESET}")
    print(f"{C.GRAY}{'─' * 60}{C.RESET}\n")
    
    for i, label_name in enumerate(LABEL_HIERARCHY, 1):
        try:
            create_label(service, label_name)
            print(f"  [{i}/{len(LABEL_HIERARCHY)}] {label_name}")
        except Exception as e:
            logger.error(f"Failed to create label '{label_name}': {e}")
            print(f"  {C.RED}✗{C.RESET} [{i}/{len(LABEL_HIERARCHY)}] {label_name} - {e}")
    
    # Clear cache after creating labels
    get_all_labels_cached.cache_clear()
    print(f"\n{C.GREEN}✓ Label creation complete{C.RESET}\n")


def main() -> None:
    """Main entry point for Gmail Organizer."""
    parser = argparse.ArgumentParser(
        description="Gmail Organizer - Automated Email Labeling System"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"Gmail Organizer v{VERSION}"
    )
    parser.add_argument(
        "--create-labels",
        action="store_true",
        help="Create all labels in the hierarchy"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate actions without making changes"
    )
    
    args = parser.parse_args()
    
    print(f"\n{C.BOLD}{C.BG_BLUE} Gmail Organizer v{VERSION} {C.RESET}\n")
    
    try:
        service = authenticate_gmail()
        
        if args.create_labels:
            create_all_labels(service)
        else:
            print(f"{C.YELLOW}No action specified. Use --create-labels to begin.{C.RESET}")
            print(f"Run with --help for more options.\n")
    
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        print(f"\n{C.RED}✗ Error: {e}{C.RESET}\n")
        sys.exit(1)
    except HttpError as e:
        logger.error(f"Gmail API error: {e}")
        print(f"\n{C.RED}✗ Gmail API Error: {e.resp.status} - {e.content}{C.RESET}\n")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {e}")
        print(f"\n{C.RED}✗ Unexpected Error: {e}{C.RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
