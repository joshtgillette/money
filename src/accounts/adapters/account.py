from abc import ABC, abstractmethod
from typing import Any

import pandas as pd

from transaction import Transaction


class Account(ABC):
    def __init__(self, name: str):
        self.name = name
        self.raw_transactions = pd.DataFrame()
        self.transactions = pd.DataFrame()
        self.transaction_list: list[Transaction] = []
        self.header_val = 0

    def load_transactions(self, path):
        """Load transactions from a specific CSV file into a pandas DataFrame."""

        self.raw_transactions = pd.concat(
            [self.raw_transactions, pd.read_csv(path, header=self.header_val)],
            ignore_index=True,
        )

    @abstractmethod
    def normalize(self):
        """Normalize raw transaction data to standard format.

        This method must be implemented by each account adapter
        to handle their unique CSV format and transform it into the
        standard format with columns: ['date', 'description', 'amount']
        """
        pass

    def _sync_transaction_list(self):
        """Synchronize transaction_list with the DataFrame."""
        self.transaction_list = []
        for row in self.transactions.itertuples(index=True):
            transaction = Transaction(
                date=row.date,
                amount=row.amount,
                description=row.description,
                index=row.Index,
                is_transfer=row.is_transfer if hasattr(row, "is_transfer") else False,
            )
            # Copy any extra columns as attributes
            for attr in dir(row):
                if not attr.startswith("_") and attr not in [
                    "Index",
                    "date",
                    "amount",
                    "description",
                    "is_transfer",
                    "count",
                    "index",
                ]:
                    setattr(transaction, attr, getattr(row, attr))
            self.transaction_list.append(transaction)

    def is_return_candidate(self, transaction: Transaction) -> bool:
        return (
            transaction.amount > 0
            or (self.__class__.__name__ == "CreditCard" or transaction.amount < 0)
        ) and "return" in transaction.description.lower()

    def find_counter_return(self, return_transaction: Transaction) -> Transaction | None:
        for transaction in self.transaction_list:
            if (
                not transaction.is_transfer
                and transaction.amount == -return_transaction.amount
                and transaction.date <= return_transaction.date
            ):
                return transaction

        return None
