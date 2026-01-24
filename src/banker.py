"""Manages multiple bank accounts and provides transaction operations."""

from pathlib import Path
from typing import Dict

from account import Account


class Banker:
    """Manages financial accounts and provides operations for transaction handling."""

    def __init__(self, *adapters: Account) -> None:
        """Initialize the banker with a collection of financial accounts."""
        self.accounts: Dict[str, Account] = {
            account.name.lower(): account for account in adapters
        }

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

        print(
            f"loaded {sum([len(account.transactions) for account in self.accounts.values()])}"
            f" transactions across {len(self.accounts)} accounts"
        )
