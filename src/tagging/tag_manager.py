from pathlib import Path
from typing import Callable, Dict, List

import pandas as pd

from accounts.adapters.account import Account
from accounts.banker import Banker
from tagging.transfer_tagger import TransferTagger
from transaction import Transaction


class TagManager:
    """Manages transaction tagging by loading and applying tags from CSV files."""

    TAGGED_PATH: Path = Path("tagged")

    def __init__(
        self,
        banker: Banker,
        taggers: Dict[str, Callable[[Account, Transaction], bool] | TransferTagger],
    ) -> None:
        """Initialize the tagger with a banker instance and tag evaluation functions."""
        self.banker: Banker = banker
        self.tags: Dict[str, str] = {}  # hash -> pipe-separated tags
        self.taggers = taggers

    def get_all_tags(self) -> set[str]:
        """Extract all unique tags from stored tag mappings."""
        return set(
            tag.strip()
            for _, transaction in self.banker
            for tag in transaction.get_tags()
            if tag.strip()
        )

    def load_existing_tags(self, tagging_path: Path) -> None:
        """Load previously saved tags from CSV files in the specified path."""
        for csv_path in self.banker.discover_csvs(tagging_path):
            transactions: Dict[int, Transaction] = self.banker.load_transactions(
                pd.read_csv(csv_path)
            )
            for _, transaction in transactions.items():
                tags_val: str = transaction.get_tags_val()
                if not tags_val:
                    continue

                self.tags[transaction.hash()] = tags_val

    def apply_tags(self) -> None:
        """Apply loaded tags to matching transactions in the banker's accounts."""
        for _, transaction in self.banker:
            tags: str | None = self.tags.get(transaction.hash(), None)
            if not tags:
                continue

            transaction.set_tags(tags)

    def auto_tag(self) -> None:
        for tag in self.taggers.keys():
            for account, transaction in self.banker:
                transaction._tags.pop(tag, None)

        for tag, evaluator in self.taggers.items():
            if isinstance(evaluator, TransferTagger):
                evaluator.identify_transfers()
                continue

            for account, transaction in self.banker:
                # Do not auto tag transactions with existing manual tag (denoted by lowercase)
                if any(t.islower() for t in transaction.get_tags()) or not evaluator(
                    account, transaction
                ):
                    continue

                setattr(transaction, tag, True)

    def remove_tags(self, tags: List[str]) -> None:
        for tag in tags:
            for account, transaction in self.banker:
                transaction._tags.pop(tag, None)

            self.tags = dict(filter(lambda item: item[1] != tag, self.tags.items()))
