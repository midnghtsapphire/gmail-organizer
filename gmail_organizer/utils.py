"""
Utility Functions for Gmail Organizer v2
==========================================
Color output, logging setup, and helper functions.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime


class C:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    BG_BLUE = "\033[44m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_MAGENTA = "\033[45m"
    BG_RED = "\033[41m"


class ColorFormatter(logging.Formatter):
    """Colored log formatter for terminal output."""
    LEVEL_COLORS = {
        logging.DEBUG:    C.GRAY,
        logging.INFO:     C.CYAN,
        logging.WARNING:  C.YELLOW,
        logging.ERROR:    C.RED,
        logging.CRITICAL: C.RED + C.BOLD,
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.LEVEL_COLORS.get(record.levelno, C.RESET)
        ts = datetime.now().strftime("%H:%M:%S")
        return (
            f"{C.GRAY}{ts}{C.RESET} "
            f"{color}{record.levelname:<8}{C.RESET} "
            f"{record.getMessage()}"
        )


def setup_logging(
    name: str = "gmail_organizer",
    log_file: str = "gmail_organizer.log",
) -> logging.Logger:
    """Configure dual logging: file + colored console."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
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


def extract_header(headers: list, name: str) -> str:
    """Extract a header value from the message headers list (case-insensitive)."""
    name_lower = name.lower()
    for h in headers:
        if h.get("name", "").lower() == name_lower:
            return h.get("value", "")
    return ""


def print_banner(version: str) -> None:
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
║   {C.WHITE}O R G A N I Z E R{C.CYAN}   v{version}                         ║
║   {C.GRAY}Automated Email Labeling, Sorting & Migration{C.CYAN}          ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝{C.RESET}
"""
    print(banner)
