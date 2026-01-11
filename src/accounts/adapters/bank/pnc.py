"""PNC bank account adapter."""

import pandas as pd

from accounts.adapters.bank.bank_account import BankAccount
from transaction import Transaction


class PNC(BankAccount):
    """Adapter for PNC checking and savings accounts."""

    def __init__(self, name: str) -> None:
        """Initialize PNC account with data normalization functions."""
        super().__init__(name)
        self.date_normalizer = lambda df: pd.to_datetime(df["Transaction Date"])
        self.amount_normalizer = lambda df: pd.to_numeric(
            df["Amount"].str.replace(r"[\+\$\s]", "", regex=True)
        )
        self.description_normalizer = lambda df: df["Transaction Description"]

    def is_transaction_income(self, transaction: Transaction) -> bool:
        return (
            transaction.description
            == "COMCAST (CC) OF PAYROLL ACH CREDIT xxxxxxxxxx6072"
        )
