import pandas as pd

from accounts.adapters.bank.bank_account import BankAccount
from transaction import Transaction


class ESL(BankAccount):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.date_normalizer = lambda df: pd.to_datetime(df["Date"])
        self.amount_normalizer = lambda df: pd.to_numeric(df["Amount Credit"]).fillna(
            0
        ) + pd.to_numeric(df["Amount Debit"]).fillna(0)
        self.description_normalizer = (
            lambda df: df["Description"] + " " + df["Memo"].fillna("").str.strip()
        )

    def is_transaction_income(self, transaction: Transaction) -> bool:
        """Determine if a normalized transaction is income."""
        return False

    def is_transaction_interest(self, transaction: Transaction) -> bool:
        """Determine if a normalized transaction is interest income."""
        return False
