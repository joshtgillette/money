from pathlib import Path
from typing import Dict

import pandas as pd

from accounts.banker import Banker
from transaction import Transaction


class TagManager:
    """Manages transaction tagging by loading and applying tags from CSV files."""

    TAGS_PATH: Path = Path("tagged")

    def __init__(self, banker: Banker) -> None:
        """Initialize the tagger with a banker instance."""
        self.banker: Banker = banker
        self.tags: Dict[str, str] = {}  # hash -> pipe-separated tags

    def get_all_tags(self) -> set[str]:
        """Extract all unique tags from stored tag mappings."""
        return {
            tag.strip()
            for tags in self.tags.values()
            for tag in tags.split("|")
            if tag.strip()
        }

    def load_existing_tags(self, tagging_path: Path) -> None:
        """Load previously saved tags from CSV files in the specified path."""
        for csv_path in self.banker.discover_csvs(tagging_path):
            transactions: Dict[int, Transaction] = self.banker.load_transactions(
                pd.read_csv(csv_path)
            )
            for _, transaction in transactions.items():
                if not transaction.get_tags():
                    continue

                self.tags[transaction.hash()] = transaction.get_tags()

    def apply_tags(self) -> None:
        """Apply loaded tags to matching transactions in the banker's accounts."""
        for _, transaction in self.banker:
            tags: str | None = self.tags.get(transaction.hash(), None)
            if not tags:
                continue

            transaction.set_tags(tags)
