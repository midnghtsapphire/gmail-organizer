"""
Report Generator Module for Gmail Organizer v2
================================================
Generates scan reports, migration summaries, and analytics.
"""

from __future__ import annotations

import json
import logging
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional

from .utils import C


class ReportGenerator:
    """Generates comprehensive reports for Gmail Organizer operations."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

    def print_label_report(
        self,
        label_map: Dict[str, str],
        label_stats: Optional[Dict[str, int]] = None,
    ) -> None:
        """Print formatted label report to console."""
        print(f"\n{C.BG_BLUE}{C.WHITE}{C.BOLD} LABEL REPORT {C.RESET}")
        print(f"{C.CYAN}{'─' * 60}{C.RESET}")
        print(f"  {C.GREEN}Total labels:{C.RESET} {C.BOLD}{len(label_map)}{C.RESET}")

        if label_stats:
            for name, count in sorted(
                label_stats.items(), key=lambda x: x[1], reverse=True
            )[:20]:
                bar = "█" * min(count // 10 + 1, 30)
                print(
                    f"  {C.BLUE}{name:<40}{C.RESET} "
                    f"{C.GREEN}{count:>6}{C.RESET} {C.MAGENTA}{bar}{C.RESET}"
                )

        print(f"{C.CYAN}{'─' * 60}{C.RESET}\n")

    def print_categorization_report(
        self,
        total_processed: int,
        categorized: int,
        uncategorized: int,
        label_counts: Dict[str, int],
    ) -> None:
        """Print categorization summary."""
        print(f"\n{C.BG_GREEN}{C.WHITE}{C.BOLD} CATEGORIZATION REPORT {C.RESET}")
        print(f"{C.CYAN}{'─' * 60}{C.RESET}")
        print(f"  {C.GREEN}Total processed  :{C.RESET} {C.BOLD}{total_processed}{C.RESET}")
        print(f"  {C.GREEN}Categorized      :{C.RESET} {C.BOLD}{categorized}{C.RESET}")
        print(f"  {C.YELLOW}Uncategorized    :{C.RESET} {C.BOLD}{uncategorized}{C.RESET}")

        if label_counts:
            print(f"\n  {C.CYAN}{C.BOLD}Top Labels Applied:{C.RESET}")
            for name, count in sorted(
                label_counts.items(), key=lambda x: x[1], reverse=True
            )[:15]:
                print(f"    {C.BLUE}{name:<40}{C.RESET} {C.GREEN}{count:>5}{C.RESET}")

        print(f"{C.CYAN}{'─' * 60}{C.RESET}\n")

    def print_migration_report(self, stats: Dict[str, int]) -> None:
        """Print migration summary."""
        print(f"\n{C.BG_YELLOW}{C.WHITE}{C.BOLD} MIGRATION REPORT {C.RESET}")
        print(f"{C.CYAN}{'─' * 60}{C.RESET}")
        print(f"  {C.GREEN}Labels migrated  :{C.RESET} {C.BOLD}{stats.get('labels_migrated', 0)}{C.RESET}")
        print(f"  {C.GREEN}Messages moved   :{C.RESET} {C.BOLD}{stats.get('messages_moved', 0)}{C.RESET}")
        print(f"  {C.RED}Errors           :{C.RESET} {C.BOLD}{stats.get('errors', 0)}{C.RESET}")
        print(f"{C.CYAN}{'─' * 60}{C.RESET}\n")

    def export_json(
        self,
        data: Dict[str, Any],
        path: str = "gmail_organizer_report.json",
    ) -> None:
        """Export report data to JSON."""
        data["timestamp"] = datetime.now().isoformat()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        self.logger.info(f"Report exported to {path}")

    def export_markdown(
        self,
        data: Dict[str, Any],
        path: str = "gmail_organizer_report.md",
    ) -> None:
        """Export report as Markdown."""
        lines = [
            "# Gmail Organizer Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]

        if "label_count" in data:
            lines.extend([
                "## Label Summary",
                "",
                f"| Metric | Value |",
                f"|--------|-------|",
                f"| Total Labels | {data.get('label_count', 0)} |",
                f"| Messages Processed | {data.get('total_processed', 0)} |",
                f"| Categorized | {data.get('categorized', 0)} |",
                f"| Uncategorized | {data.get('uncategorized', 0)} |",
                "",
            ])

        if "migration" in data:
            m = data["migration"]
            lines.extend([
                "## Migration Summary",
                "",
                f"| Metric | Value |",
                f"|--------|-------|",
                f"| Labels Migrated | {m.get('labels_migrated', 0)} |",
                f"| Messages Moved | {m.get('messages_moved', 0)} |",
                f"| Errors | {m.get('errors', 0)} |",
                "",
            ])

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        self.logger.info(f"Markdown report exported to {path}")
