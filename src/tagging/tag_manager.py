from pathlib import Path
from typing import Callable, Dict

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
        self.taggers = taggers

    def get_all_tags(self, ignore_tag_source=False) -> set[str]:
        """Extract all unique tags from stored tag mappings."""
        return set(
            (tag.strip().lower() if ignore_tag_source else tag.strip())
            for _, transaction in self.banker
            for tag in transaction.get_tags()
            if tag.strip()
        )

    def get_existing_tags(self, tagging_path: Path) -> Dict[str, str]:
        """Load previously saved tags from CSV files in the specified path."""
        existing_tags: Dict[str, str] = {}
        for csv_path in self.banker.discover_csvs(tagging_path):
            transactions: Dict[int, Transaction] = self.banker.load_transactions(
                pd.read_csv(csv_path)
            )
            for _, transaction in transactions.items():
                tags_val: str = transaction.get_tags_val()
                if not tags_val:
                    continue

                existing_tags[transaction.hash()] = tags_val

        return existing_tags

    def apply_tags(self, existing_tags) -> None:
        """Apply loaded tags to matching transactions in the banker's accounts."""
        for _, transaction in self.banker:
            tags: str | None = existing_tags.get(transaction.hash(), None)
            if not tags:
                continue

            transaction.set_tags(tags)

    def auto_tag(self) -> None:
        for tag in self.get_all_tags():
            if tag.islower():
                continue

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
