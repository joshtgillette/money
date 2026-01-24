"""Base account class for financial institutions."""

from pathlib import Path
from typing import Callable, Dict

import pandas as pd

from transaction import Transaction


class Account:
    """Abstract base class for financial accounts with transaction normalization."""

    def __init__(
        self,
        name: str,
        date_normalizer: Callable[[pd.DataFrame], pd.Series],
        amount_normalizer: Callable[[pd.DataFrame], pd.Series],
        description_normalizer: Callable[[pd.DataFrame], pd.Series],
        header_val: int | None = 0,
    ) -> None:
        """Initialize an account with normalizers and transaction storage.

        Args:
            name: Account name
            date_normalizer: Function to normalize date column
            amount_normalizer: Function to normalize amount column
            description_normalizer: Function to normalize description column
            header_val: Row number to use as header when reading CSV (default 0, can be None)
        """
        self.name: str = name
        self.date_normalizer: Callable[[pd.DataFrame], pd.Series] = date_normalizer
        self.amount_normalizer: Callable[[pd.DataFrame], pd.Series] = amount_normalizer
        self.description_normalizer: Callable[[pd.DataFrame], pd.Series] = (
            description_normalizer
        )
        self.header_val: int | None = header_val

        self.source_transactions: pd.DataFrame = pd.DataFrame()
        self.transactions: Dict[int, Transaction] = {}

    def add_source_transactions(self, csv_path: Path) -> None:
        """Load and concatenate transactions from a CSV file.

        Args:
            csv_path: Path to the CSV file containing transaction data
        """

        self.source_transactions = pd.concat(
            [self.source_transactions, pd.read_csv(csv_path, header=self.header_val)],
            ignore_index=True,
        )

    def normalize_source_transactions(self) -> pd.DataFrame:
        """Apply account-specific normalizers to transform source data into standard format.

        Returns:
            DataFrame with normalized transaction data in standard format
        """
        return self.source_transactions.assign(
            account=self.name,
            date=self.date_normalizer(self.source_transactions),
            amount=self.amount_normalizer(self.source_transactions),
            description=self.description_normalizer(self.source_transactions),
        ).loc[:, ["account", "date", "amount", "description"]]
