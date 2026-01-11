"""SoFi bank account adapter."""

import pandas as pd

from accounts.adapters.bank.bank_account import BankAccount
from transaction import Transaction


class SoFi(BankAccount):
    """Adapter for SoFi checking and savings accounts."""

    def __init__(self, name: str) -> None:
        """Initialize SoFi account with data normalization functions."""
        super().__init__(name)
        self.date_normalizer = lambda df: pd.to_datetime(df["Date"])
        self.amount_normalizer = lambda df: pd.to_numeric(df["Amount"])
        self.description_normalizer = lambda df: df["Description"]

    def is_transaction_income(self, transaction: Transaction) -> bool:
        return transaction.description == "COMCAST (CC) OF"
