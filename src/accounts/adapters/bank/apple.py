"""Apple Savings account adapter."""

from typing import Callable

import pandas as pd

from accounts.adapters.bank.bank_account import BankAccount
from transaction import Transaction


class Apple(BankAccount):
    """Adapter for Apple Savings accounts."""

    def __init__(self, name: str) -> None:
        """Initialize Apple account with data normalization functions."""
        super().__init__(name)
        self.date_normalizer: Callable = lambda df: pd.to_datetime(
            df["Transaction Date"]
        )
        self.amount_normalizer: Callable = lambda df: pd.to_numeric(df["Amount"]) * df[
            "Transaction Type"
        ].eq("Credit").map({True: 1, False: -1})
        self.description_normalizer: Callable = lambda df: df["Description"]

    def is_transaction_paycheck(self, transaction: Transaction) -> bool:
        return transaction.description == "ACH Transfer from COMCAST (CC) OF PAYROLL"

    def is_transaction_interest(self, transaction: Transaction) -> bool:
        return transaction.description == "Interest Paid"
