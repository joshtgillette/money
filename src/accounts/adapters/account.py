"""Base account class for financial institutions."""

from abc import ABC
from pathlib import Path
from typing import Callable, Dict, Optional

import pandas as pd

from transaction import Transaction


class Account(ABC):
    """Abstract base class for financial accounts with transaction normalization."""

    def __init__(self, name: str) -> None:
        """Initialize an account with a name and empty transaction storage."""
        self.name: str = name

        self.source_transactions: pd.DataFrame = pd.DataFrame()
        self.header_val: int | None = 0

        self.date_normalizer: Callable[[pd.DataFrame], pd.Series]
        self.amount_normalizer: Callable[[pd.DataFrame], pd.Series]
        self.description_normalizer: Callable[[pd.DataFrame], pd.Series]

        self.transactions: Dict[int, Transaction] = {}

    def add_source_transactions(self, csv_path: Path) -> None:
        """Load and concatenate transactions from a CSV file."""

        self.source_transactions = pd.concat(
            [self.source_transactions, pd.read_csv(csv_path, header=self.header_val)],
            ignore_index=True,
        )

    def normalize_source_transactions(self) -> pd.DataFrame:
        """Apply account-specific normalizers to transform source data into standard format."""
        return self.source_transactions.assign(
            date=self.date_normalizer,
            amount=self.amount_normalizer,
            description=self.description_normalizer,
        )

    def is_return_candidate(self, transaction: Transaction) -> bool:
        """Determine if a transaction could be a return or refund."""
        return (
            transaction.amount > 0
            or (self.__class__.__name__ == "CreditCard" or transaction.amount < 0)
        ) and "return" in transaction.description.lower()

    def find_counter_return(
        self, return_transaction: Transaction
    ) -> Optional[Transaction]:
        """Find the original transaction that this return is refunding."""
        for transaction in self.transactions.values():
            if (
                not transaction.is_transfer
                and transaction.amount == -return_transaction.amount
                and transaction.date <= return_transaction.date
            ):
                return transaction

        return None
