"""
Gmail Organizer v2 — CLI Entry Point
======================================
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime

from .config import VERSION, GmailOrganizerConfig
from .utils import C, print_banner, setup_logging, extract_header
from .auth import GmailAuthenticator
from .operations import GmailOperations
from .categorizer import EmailCategorizer
from .migrator import LabelArchitect, LabelMigrator, LabelCleaner
from .reporter import ReportGenerator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gmail Organizer v2 — Automated Email Labeling, Sorting & Migration",
    )
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Preview changes without applying (default)")
    parser.add_argument("--execute", action="store_true",
                        help="Actually apply changes")
    parser.add_argument("--labels-only", action="store_true",
                        help="Only create label hierarchy")
    parser.add_argument("--migrate", action="store_true",
                        help="Migrate old labels to new hierarchy")
    parser.add_argument("--cleanup", action="store_true",
                        help="Clean up empty labels")
    parser.add_argument("--max-messages", type=int, default=500,
                        help="Max messages to process (0=all)")
    parser.add_argument("--credentials", type=str, default="credentials.json")
    parser.add_argument("--token", type=str, default="token.pickle")
    parser.add_argument("--config", type=str, default=None)
    parser.add_argument("--output-dir", type=str, default=".")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--version", action="version",
                        version=f"Gmail Organizer v{VERSION}")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.config:
        config = GmailOrganizerConfig.from_json(args.config)
    else:
        config = GmailOrganizerConfig()

    config.credentials_file = args.credentials
    config.token_file = args.token
    config.dry_run = not args.execute
    config.max_messages = args.max_messages

    print_banner(VERSION)
    logger = setup_logging()
    logger.info(f"Gmail Organizer v{VERSION} starting...")
    logger.info(f"Mode: {'EXECUTE' if args.execute else 'DRY RUN'}")

    if config.dry_run:
        print(f"  {C.YELLOW}{C.BOLD}DRY RUN MODE — no changes will be made{C.RESET}\n")

    # Authenticate
    print(f"{C.CYAN}Authenticating with Gmail API...{C.RESET}")
    auth = GmailAuthenticator(
        credentials_file=config.credentials_file,
        token_file=config.token_file,
        logger=logger,
    )
    creds = auth.authenticate()
    ops = GmailOperations(creds, config, logger)
    print(f"{C.GREEN}Authenticated successfully{C.RESET}\n")

    # Build label hierarchy
    print(f"{C.CYAN}Building label hierarchy...{C.RESET}")
    architect = LabelArchitect(ops, logger)
    label_map = architect.build_hierarchy()
    print(f"{C.GREEN}Label hierarchy ready ({len(label_map)} labels){C.RESET}\n")

    reporter = ReportGenerator(logger)

    if args.labels_only:
        reporter.print_label_report(label_map)
        print(f"{C.GREEN}{C.BOLD}Label hierarchy built. Exiting.{C.RESET}\n")
        return

    # Migrate old labels
    if args.migrate:
        print(f"{C.CYAN}Migrating old labels...{C.RESET}")
        migrator = LabelMigrator(ops, label_map, config, logger)
        migration_stats = migrator.migrate_all(dry_run=config.dry_run)
        reporter.print_migration_report(migration_stats)

    # Cleanup empty labels
    if args.cleanup:
        print(f"{C.CYAN}Cleaning up empty labels...{C.RESET}")
        cleaner = LabelCleaner(ops, logger)
        removed = cleaner.cleanup_empty_labels(dry_run=config.dry_run)
        print(f"{C.GREEN}Removed {removed} empty labels{C.RESET}\n")

    # Categorize messages
    if not args.migrate and not args.cleanup:
        print(f"{C.CYAN}Categorizing messages...{C.RESET}")
        categorizer = EmailCategorizer(logger)
        label_counts: Counter = Counter()
        total_processed = 0
        categorized = 0
        uncategorized = 0

        page_token = None
        remaining = config.max_messages or float("inf")

        while remaining > 0:
            batch_size = min(int(remaining), config.batch_size)
            result = ops.list_messages(max_results=batch_size, page_token=page_token)
            messages = result.get("messages", [])
            if not messages:
                break

            for msg_stub in messages:
                try:
                    msg = ops.get_message(
                        msg_stub["id"],
                        format="metadata",
                        metadata_headers=["From", "To", "Subject", "List-Unsubscribe"],
                    )
                    headers = msg.get("payload", {}).get("headers", [])
                    labels = categorizer.categorize(headers)

                    total_processed += 1

                    if labels and labels != ["FLAGGED-REVIEW"]:
                        categorized += 1
                    else:
                        uncategorized += 1

                    for lbl_name in labels:
                        label_counts[lbl_name] += 1
                        lbl_id = label_map.get(lbl_name)
                        if lbl_id and not config.dry_run:
                            ops.modify_message(msg_stub["id"], add_label_ids=[lbl_id])

                except Exception as e:
                    logger.error(f"Error processing message {msg_stub['id']}: {e}")

                remaining -= 1
                if remaining <= 0:
                    break

            page_token = result.get("nextPageToken")
            if not page_token:
                break

            if total_processed % 100 == 0:
                print(f"  {C.MAGENTA}Processed {total_processed} messages...{C.RESET}")

        reporter.print_categorization_report(
            total_processed, categorized, uncategorized, dict(label_counts)
        )

    # Export reports
    report_data = {
        "label_count": len(label_map),
        "total_processed": total_processed if not args.migrate else 0,
        "categorized": categorized if not args.migrate else 0,
        "uncategorized": uncategorized if not args.migrate else 0,
    }
    reporter.export_json(report_data, f"{args.output_dir}/gmail_organizer_report.json")
    reporter.export_markdown(report_data, f"{args.output_dir}/gmail_organizer_report.md")

    print(f"{C.GREEN}{C.BOLD}Complete!{C.RESET} Reports saved.\n")


if __name__ == "__main__":
    main()
