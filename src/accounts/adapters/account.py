from abc import ABC, abstractmethod
from typing import Any, Optional, Dict

import pandas as pd

from transaction import Transaction


class Account(ABC):
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.raw_transactions: pd.DataFrame = pd.DataFrame()
        self.transactions: Dict[int, Transaction] = {}  # Map index to Transaction objects
        self.header_val: int = 0

    def load_transactions(self, path: str) -> None:
        """Load transactions from a specific CSV file into a pandas DataFrame."""

        self.raw_transactions = pd.concat(
            [self.raw_transactions, pd.read_csv(path, header=self.header_val)],
            ignore_index=True,
        )

    @abstractmethod
    def normalize(self) -> None:
        """Normalize raw transaction data to standard format.

        This method must be implemented by each account adapter
        to handle their unique CSV format and transform it into
        Transaction objects stored in self.transactions dict.
        """
        pass

    def _build_transactions_from_dataframe(self, df: pd.DataFrame) -> None:
        """Helper method to build transactions dict from a normalized DataFrame.
        
        The DataFrame should have columns: date, amount, description, and optionally is_transfer.
        """
        self.transactions = {}
        has_is_transfer: bool = 'is_transfer' in df.columns
        for index, row in df.iterrows():
            transaction: Transaction = Transaction(
                date=row['date'],
                amount=row['amount'],
                description=row['description'],
                index=index,
                is_transfer=row['is_transfer'] if has_is_transfer else False,
            )
            self.transactions[index] = transaction

    def is_return_candidate(self, transaction: Transaction) -> bool:
        return (
            transaction.amount > 0
            or (self.__class__.__name__ == "CreditCard" or transaction.amount < 0)
        ) and "return" in transaction.description.lower()

    def find_counter_return(self, return_transaction: Transaction) -> Optional[Transaction]:
        for transaction in self.transactions.values():
            if (
                not transaction.is_transfer
                and transaction.amount == -return_transaction.amount
                and transaction.date <= return_transaction.date
            ):
                return transaction

        return None
