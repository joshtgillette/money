"""Manages multiple bank accounts and provides transaction operations."""

import os
from pathlib import Path
from typing import Callable, Dict, Iterator, List, Tuple, cast

import pandas as pd

from accounts.adapters.account import Account
from transaction import Transaction


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
            account.transactions = self.load_transactions(
                account.normalize_source_transactions()
            )

    @staticmethod
    def discover_csvs(path: Path) -> List[Path]:
        """Recursively discover all CSV files in the given path."""
        return list(path.rglob("*.csv"))

    @staticmethod
    def load_transactions(transactions_data: pd.DataFrame) -> Dict[int, Transaction]:
        """Parse transaction data from a DataFrame into Transaction objects."""
        transactions: Dict[int, Transaction] = {}
        for row in transactions_data.itertuples():
            index = cast(int, row.Index)
            tags = getattr(row, "tags", None)
            transactions[index] = Transaction(
                index=index,
                account_name=cast(str, row.account),
                date=pd.to_datetime(row.date),  # type: ignore[call-overload]
                amount=cast(float, row.amount),
                description=cast(str, row.description),
                tags=cast(str, tags) if pd.notna(tags) else "",
            )

        return transactions

    def __iter__(self) -> Iterator[Tuple[Account, Transaction]]:
        for _, account in self.accounts.items():
            for transaction in account.transactions.values():
                yield account, transaction

    def filter_transactions(
        self, *predicates: Callable[[Transaction], bool]
    ) -> List[Transaction]:
        """Filter transactions across all accounts using provided predicate functions."""
        return [
            transaction
            for _, transaction in self
            if not predicates or all(pred(transaction) for pred in predicates)
        ]

    def write_transactions(
        self,
        transactions: List[Transaction],
        path: Path,
        columns: List[str] = ["account", "date", "amount", "description", "tags"],
        by_month: bool = False,
    ) -> None:
        """Write transactions to CSV files, optionally grouped by month."""
        transaction_data = pd.DataFrame(
            [transaction.to_dict() for transaction in transactions]
        ).sort_values("date")
        if not by_month:
            # Write all transactions
            path = path.with_suffix(".csv")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            transaction_data.to_csv(path, columns=columns, index=False)
            return

        # Write transactions by month
        for month, group in transaction_data.groupby(
            transaction_data["date"].dt.to_period("M")
        ):
            monthly_path = path / f"{pd.Period(month).strftime('%m%y')}.csv"
            os.makedirs(os.path.dirname(monthly_path), exist_ok=True)
            group.to_csv(
                monthly_path,
                columns=columns,
                index=False,
            )
