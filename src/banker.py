"""Manages multiple bank accounts and provides transaction operations."""

import json
from pathlib import Path
from typing import Callable, Dict, Iterator, List

import pandas as pd

from account import Account
from transaction import Transaction


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
        """Load and normalize transactions from source CSV files for all accounts.

        Args:
            source_transactions_path: Path to directory containing CSV transaction files.
        """

        for csv_path in list(source_transactions_path.rglob("*.csv")):
            account: Account | None = self.accounts.get(
                csv_path.name.replace(".csv", ""), None
            )
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

        print(
            "\n"
            f"loaded {sum([len(account.transactions) for account in self.accounts.values()])}"
            f" transactions across {len(self.accounts)} accounts"
        )

    def filter_transactions(
        self,
        *predicates: Callable[[Transaction], bool],
        reversed: bool = False,
    ) -> List[Transaction]:
        """Filter transactions across all accounts using provided predicate functions.

        Args:
            *predicates: Variable number of predicate functions that take a Transaction and return bool.
            reversed: If True, sort transactions in reverse chronological order (newest first).

        Returns:
            List of filtered and sorted Transaction objects.
        """

        return sorted(
            [
                transaction
                for transaction in self
                if not predicates or all(pred(transaction) for pred in predicates)
            ],
            key=lambda t: t.date,
            reverse=reversed,
        )

    def __iter__(self) -> Iterator[Transaction]:
        """Iterate over all transactions across all accounts.

        Yields:
            Transaction objects with tags loaded from the book.
        """

        for account in self.accounts.values():
            for transaction_df in account.transactions.itertuples(index=False):
                transaction: Transaction = Transaction(transaction_df)
                transaction.set_tags(
                    self.get_existing_tags_for_transaction(transaction)
                )
                yield transaction

    def write_book(self, transaction: Transaction, tags: List[str]) -> None:
        """Write tags for a transaction to the book (persistent storage).

        Args:
            transaction: The transaction to tag.
            tags: List of tag strings to add to this transaction.
        """

        # Get up-to-date book
        book: Dict[str, List[str]] = self.read_book()

        # Update transaction tags from hash
        book.setdefault(transaction.hash(), []).extend(tags)

        # Perform file write
        with open(self.BOOK_PATH, "w") as book_file:
            json.dump(book, book_file, indent=2)

    def read_book(self) -> Dict[str, List[str]]:
        """Read the book (transaction tags) from persistent storage.

        Returns:
            Dictionary mapping transaction hashes to lists of tag strings.
        """

        book: Dict[str, List[str]] = {}
        try:
            # Perform file read
            with open(self.BOOK_PATH, "r+") as book_file:
                book = json.load(book_file)
        except FileNotFoundError:
            pass

        return book

    def get_existing_tags_for_transaction(self, transaction: Transaction) -> List[str]:
        """Get all existing tags for a specific transaction.

        Args:
            transaction: The transaction to get tags for.

        Returns:
            List of tag strings associated with this transaction.
        """

        return self.read_book().get(transaction.hash(), [])

    def get_all_tags(self) -> set[str]:
        """Get all unique tags used across all transactions.

        Returns:
            Set of all unique tag strings (lowercased) used in the book.
        """

        return {
            value.lower() for values in self.read_book().values() for value in values
        }
