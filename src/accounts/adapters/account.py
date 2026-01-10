from abc import ABC
from pathlib import Path
from typing import Callable, Dict, Optional

import pandas as pd

from transaction import Transaction


class Account(ABC):
    def __init__(self, name: str) -> None:
        self.name: str = name

        self.source_transactions: pd.DataFrame = pd.DataFrame()
        self.header_val: int | None = 0

        self.date_normalizer: Callable
        self.amount_normalizer: Callable
        self.description_normalizer: Callable

        self.transactions: Dict[int, Transaction] = {}

    def add_source_transactions(self, csv_path: Path) -> None:
        """Load transactions from a specific CSV file into a pandas DataFrame."""

        self.source_transactions = pd.concat(
            [self.source_transactions, pd.read_csv(csv_path, header=self.header_val)],
            ignore_index=True,
        )

    def normalize_source_transactions(self):
        return self.source_transactions.assign(
            date=self.date_normalizer,
            amount=self.amount_normalizer,
            description=self.description_normalizer,
        )

    def is_return_candidate(self, transaction: Transaction) -> bool:
        return (
            transaction.amount > 0
            or (self.__class__.__name__ == "CreditCard" or transaction.amount < 0)
        ) and "return" in transaction.description.lower()

    def find_counter_return(
        self, return_transaction: Transaction
    ) -> Optional[Transaction]:
        for transaction in self.transactions.values():
            if (
                not transaction.is_transfer
                and transaction.amount == -return_transaction.amount
                and transaction.date <= return_transaction.date
            ):
                return transaction

        return None
