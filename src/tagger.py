from pathlib import Path
from typing import Dict

import pandas as pd

from accounts.banker import Banker
from transaction import Transaction


class Tagger:
    """Manages transaction tags loaded from CSV files."""

    TAGS_PATH: Path = Path("tagged")

    def __init__(self, banker: Banker) -> None:
        self.banker = banker
        self.tags: Dict[str, str] = {}  # hash -> comma-separated tags (lowercase)

    def get_all_tags(self):
        return {
            tag.strip()
            for tags in self.tags.values()
            for tag in tags.split("|")
            if tag.strip()
        }

    def load_existing_tags(self, tagging_path: Path) -> None:
        for csv_path in self.banker.discover_csvs(tagging_path):
            transactions: Dict[int, Transaction] = self.banker.load_transactions(
                pd.read_csv(csv_path)
            )
            for _, transaction in transactions.items():
                if not transaction._tags:
                    continue

                self.tags[transaction.hash()] = transaction.get_tags()

    def apply_tags(self) -> None:
        for _, transaction in self.banker:
            tags: str | None = self.tags.get(transaction.hash(), None)
            if not tags:
                continue

            transaction.set_tags(tags)
