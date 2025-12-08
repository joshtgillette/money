from abc import ABC, abstractmethod

import pandas as pd


class Account(ABC):
    def __init__(self, name: str):
        self.name = name
        self.raw_transactions = pd.DataFrame()
        self.transactions = pd.DataFrame(
            columns=[
                "date",
                "amount",
                "description",
            ]
        )
        self.header_val = 0

    def load_transactions(self, path) -> pd.DataFrame:
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

    def is_return_candidate(self, transaction) -> bool:
        return (
            transaction.amount > 0
            or (self.__class__.__name__ == "CreditCard" or transaction.amount < 0)
        ) and "return" in transaction.description.lower()

    def find_counter_return(self, return_transaction) -> int:
        for transaction in self.transactions.itertuples(index=True):
            if (
                not self.transactions.loc[transaction.Index, "is_transfer"]
                and transaction.amount == -return_transaction.amount
                and transaction.date <= return_transaction.date
            ):
                return transaction

        return None
