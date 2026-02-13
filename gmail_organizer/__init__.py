"""
Gmail Organizer v2
====================
Automated Email Labeling, Sorting & Migration Tool.

Modular package structure implementing all Venice AI code review recommendations:
- Encrypted credential storage
- Token bucket rate limiting
- Compiled regex patterns with case-insensitive matching
- Comprehensive error handling with exponential backoff
- No archiving — all labels active with detailed hierarchy
"""

from .config import (
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
from .utils import C, setup_logging, extract_header, print_banner
from .auth import GmailAuthenticator
from .categorizer import EmailCategorizer
from .operations import (
    TokenBucketRateLimiter,
    GmailOperations,
    api_call_with_backoff,
)
from .migrator import LabelArchitect, LabelMigrator, LabelCleaner
from .reporter import ReportGenerator

__version__ = VERSION
__all__ = [
    "VERSION", "APP_NAME", "SCOPES", "LABEL_HIERARCHY",
    "CATEGORIZATION_RULES", "MIGRATION_MAP", "GmailOrganizerConfig",
    "get_compiled_rules", "get_compiled_migration_map",
    "C", "setup_logging", "extract_header", "print_banner",
    "GmailAuthenticator",
    "EmailCategorizer",
    "TokenBucketRateLimiter", "GmailOperations", "api_call_with_backoff",
    "LabelArchitect", "LabelMigrator", "LabelCleaner",
    "ReportGenerator",
]
