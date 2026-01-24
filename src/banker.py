"""Manages multiple bank accounts and provides transaction operations."""

import os
from pathlib import Path
from typing import Dict, List, cast

import pandas as pd

from account import Account


class Banker:
    """Manages financial accounts and provides operations for transaction handling."""

    def __init__(self, *accounts: Account) -> None:
        """Initialize the banker with a collection of financial accounts."""
        self.accounts: Dict[str, Account] = {
            account.name.lower(): account for account in accounts
        }

    def load_account_transactions(self, source_transactions_path: Path) -> None:
        """Load and normalize transactions from source CSV files for all accounts."""
        for csv_path in self.discover_csvs(source_transactions_path):
            account = self.accounts.get(csv_path.name.replace(".csv", ""), None)
            if not account:
                continue

            account.add_source_transactions(csv_path)

        # Normalize source transactions to a common format and load
        for _, account in self.accounts.items():
            account.normalize_source_transactions()

    @staticmethod
    def discover_csvs(path: Path) -> List[Path]:
        """Recursively discover all CSV files in the given path."""
        return list(path.rglob("*.csv"))

    def __iter__(self):
        for account in self.accounts.values():
            for transaction in account.transactions.itertuples(index=True):
                yield account, transaction

    def filter_transactions(self, *predicates):
        # Add account name to each transaction
        for account in self.accounts.values():
            account.transactions["account"] = account.name

        # Collect transactions based on predicates
        return pd.DataFrame(
            [
                transaction
                for _, transaction in self
                if not predicates or all(pred(transaction) for pred in predicates)
            ]
        )

    def write_transactions(
        self,
        transactions: pd.DataFrame,
        path: Path,
        columns: List[str] = ["account", "date", "amount", "description"],
        by_month: bool = False,
    ) -> None:
        """Write transactions to CSV files, optionally grouped by month."""
        transactions = transactions.sort_values("date", ascending=False)
        if not by_month:
            # Write all transactions
            path = path.with_suffix(".csv")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            transactions.to_csv(path, columns=columns, index=False)
            return

        # Write transactions by month
        for month, group in transactions.groupby(
            transactions["date"].dt.to_period("M")
        ):
            monthly_path = path / f"{cast(pd.Period, month).strftime('%m%y')}.csv"
            os.makedirs(os.path.dirname(monthly_path), exist_ok=True)
            group.to_csv(
                monthly_path,
                columns=columns,
                index=False,
            )
