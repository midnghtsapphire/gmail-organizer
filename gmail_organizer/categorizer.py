"""
Email Categorizer Module for Gmail Organizer v2
=================================================
Email classification using compiled regex patterns.
All matching is case-insensitive.
"""

from __future__ import annotations

import logging
import re
from typing import Dict, List, Optional

from .config import get_compiled_rules
from .utils import extract_header


class EmailCategorizer:
    """
    Categorizes emails into labels based on compiled regex rules.
    All matching is case-insensitive.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self._rules = get_compiled_rules()

    def categorize(self, headers: list) -> List[str]:
        """
        Determine which labels to apply based on message headers.
        Returns a list of label names. Multiple labels can be applied.
        """
        from_addr = extract_header(headers, "From").lower()
        to_addr = extract_header(headers, "To").lower()
        subject = extract_header(headers, "Subject")
        list_unsub = extract_header(headers, "List-Unsubscribe")

        matched_labels: List[str] = []

        for rule in self._rules:
            match = True

            if "_from_re" in rule:
                if not rule["_from_re"].search(from_addr):
                    match = False

            if "_to_re" in rule:
                if not rule["_to_re"].search(to_addr):
                    match = False

            if "_subject_re" in rule:
                if not rule["_subject_re"].search(subject):
                    match = False

            if rule.get("has_unsubscribe"):
                if not list_unsub:
                    match = False

            if match:
                for lbl in rule["labels"]:
                    if lbl not in matched_labels:
                        matched_labels.append(lbl)

        if not matched_labels:
            matched_labels.append("FLAGGED-REVIEW")

        return matched_labels
