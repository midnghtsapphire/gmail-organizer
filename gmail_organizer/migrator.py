"""
Label Migration Module for Gmail Organizer v2
===============================================
Handles label creation, migration from old labels to new hierarchy,
and cleanup of empty/obsolete labels.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from .config import (
    LABEL_HIERARCHY,
    GmailOrganizerConfig,
    get_compiled_migration_map,
)
from .operations import GmailOperations
from .utils import C


class LabelArchitect:
    """
    Creates the label hierarchy in Gmail.
    Ensures all labels in the hierarchy exist.
    """

    def __init__(
        self,
        ops: GmailOperations,
        logger: Optional[logging.Logger] = None,
    ):
        self.ops = ops
        self.logger = logger or logging.getLogger(__name__)

    def build_hierarchy(self) -> Dict[str, str]:
        """
        Ensure all labels in the hierarchy exist.
        Returns mapping of label_name -> label_id.
        """
        existing = self.ops.list_labels()
        label_map: Dict[str, str] = dict(existing)
        created = 0

        for label_name in LABEL_HIERARCHY:
            if label_name not in label_map:
                try:
                    result = self.ops.create_label(label_name)
                    label_map[label_name] = result["id"]
                    created += 1
                    self.logger.info(f"{C.GREEN}Created label:{C.RESET} {label_name}")
                except Exception as e:
                    self.logger.error(f"Failed to create label '{label_name}': {e}")

        self.logger.info(
            f"Label hierarchy: {len(label_map)} total, {created} created"
        )
        return label_map


class LabelMigrator:
    """
    Migrates messages from old labels to new hierarchy labels.
    """

    def __init__(
        self,
        ops: GmailOperations,
        label_map: Dict[str, str],
        config: Optional[GmailOrganizerConfig] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.ops = ops
        self.label_map = label_map
        self.config = config or GmailOrganizerConfig()
        self.logger = logger or logging.getLogger(__name__)
        self._migration_map = get_compiled_migration_map()
        self._stats: Dict[str, int] = {
            "labels_migrated": 0,
            "messages_moved": 0,
            "errors": 0,
        }

    def find_migration_target(self, label_name: str) -> Optional[str]:
        """Find the new hierarchy label for an old label name."""
        for pattern, target in self._migration_map:
            if pattern.search(label_name):
                return target
        return None

    def migrate_all(self, dry_run: bool = True) -> Dict[str, int]:
        """
        Migrate all old labels to new hierarchy.
        Returns migration statistics.
        """
        existing = self.ops.list_labels()

        for label_name, label_id in existing.items():
            # Skip system labels and already-migrated labels
            if label_name in LABEL_HIERARCHY:
                continue
            if label_name.startswith(("CATEGORY_", "CHAT", "SENT", "INBOX",
                                      "TRASH", "DRAFT", "SPAM", "STARRED",
                                      "UNREAD", "IMPORTANT")):
                continue

            target = self.find_migration_target(label_name)
            if not target:
                continue

            target_id = self.label_map.get(target)
            if not target_id:
                self.logger.warning(f"Target label not found: {target}")
                continue

            self.logger.info(
                f"Migrating: {label_name} -> {target}"
            )

            if dry_run:
                self._stats["labels_migrated"] += 1
                continue

            try:
                self._migrate_label_messages(label_id, target_id)
                self._stats["labels_migrated"] += 1
            except Exception as e:
                self.logger.error(f"Migration error for {label_name}: {e}")
                self._stats["errors"] += 1

        return dict(self._stats)

    def _migrate_label_messages(
        self,
        source_label_id: str,
        target_label_id: str,
    ) -> int:
        """Move all messages from source label to target label."""
        moved = 0
        page_token = None

        while True:
            result = self.ops.list_messages(
                label_ids=[source_label_id],
                max_results=self.config.batch_size,
                page_token=page_token,
            )
            messages = result.get("messages", [])
            if not messages:
                break

            for msg in messages:
                try:
                    self.ops.modify_message(
                        msg["id"],
                        add_label_ids=[target_label_id],
                        remove_label_ids=[source_label_id],
                    )
                    moved += 1
                    self._stats["messages_moved"] += 1
                except Exception as e:
                    self.logger.error(f"Error moving message {msg['id']}: {e}")
                    self._stats["errors"] += 1

            page_token = result.get("nextPageToken")
            if not page_token:
                break

        return moved


class LabelCleaner:
    """
    Cleans up empty and obsolete labels.
    """

    def __init__(
        self,
        ops: GmailOperations,
        logger: Optional[logging.Logger] = None,
    ):
        self.ops = ops
        self.logger = logger or logging.getLogger(__name__)

    def cleanup_empty_labels(self, dry_run: bool = True) -> int:
        """Remove labels that have zero messages. Returns count removed."""
        labels = self.ops.list_labels_full()
        removed = 0

        for label in labels:
            label_id = label["id"]
            label_name = label.get("name", "")

            # Skip system labels
            if label.get("type") == "system":
                continue

            # Skip labels in our hierarchy
            if label_name in LABEL_HIERARCHY:
                continue

            try:
                info = self.ops.get_label_info(label_id)
                total = info.get("messagesTotal", 0)

                if total == 0:
                    self.logger.info(
                        f"{'[DRY RUN] ' if dry_run else ''}"
                        f"Removing empty label: {label_name}"
                    )
                    if not dry_run:
                        self.ops.delete_label(label_id)
                    removed += 1

            except Exception as e:
                self.logger.error(f"Error checking label {label_name}: {e}")

        return removed
