"""Manages multiple bank accounts and provides transaction operations."""

import json
from pathlib import Path
from typing import Any, Dict, Iterator, List, cast

import pandas as pd

from account import Account


class Banker:
    """Manages financial accounts and provides operations for transaction handling."""

    BOOK_PATH: Path = Path("book.json")

    def __init__(self, *adapters: Account) -> None:
        """Initialize the banker with a collection of financial accounts."""
        self.accounts: Dict[str, Account] = {
            account.name.lower(): account for account in adapters
        }
        self.transactions: pd.DataFrame

    def load_account_transactions(self, source_transactions_path: Path) -> None:
        """Load and normalize transactions from source CSV files for all accounts."""
        for csv_path in list(source_transactions_path.rglob("*.csv")):
            account = self.accounts.get(csv_path.name.replace(".csv", ""), None)
            if not account:
                continue

            account.add_source_transactions(csv_path)

        # Remove accounts without source transactions
        self.accounts = {
            name: account
            for name, account in self.accounts.items()
            if len(account.source_transactions)
        }

        # Normalize transactions to standard format
        for account in self.accounts.values():
            account.normalize_source_transactions()

        # Get aggregated transactions
        self.transactions = pd.DataFrame(
            [
                transaction
                for account in self.accounts.values()
                for transaction in account.transactions.itertuples(index=True)
            ]
        ).sort_values("date", ascending=False)

        print(
            f"loaded {sum([len(account.transactions) for account in self.accounts.values()])}"
            f" transactions across {len(self.accounts)} accounts"
        )

    def __iter__(self) -> Iterator[str]:
        for transaction in self.transactions.itertuples(index=True):
            transaction = cast(Any, transaction)
            yield (
                f"{transaction.account} on {pd.to_datetime(transaction.date).strftime('%B %d, %Y')} for "
                f"{'-' if transaction.amount < 0 else ''}${abs(transaction.amount):,.2f} - {transaction.description}"
            )

    def write_book(self, transaction: str, tags: List[str]) -> None:
        # Get up-to-date book
        book = self.read_book()

        # Update transaction tags from hash
        book.update({transaction: book.get(transaction, []) + tags})

        # Perform file write
        with open(self.BOOK_PATH, "w") as book_file:
            json.dump(book, book_file, indent=2)

    def read_book(self) -> Dict:
        book = {}
        try:
            # Perform file read
            with open(self.BOOK_PATH, "r+") as book_file:
                book = json.load(book_file)
        except FileNotFoundError:
            pass

        return book

    def get_existing_tags_for_transaction(self, transaction) -> List[str]:
        return self.read_book().get(transaction, [])
