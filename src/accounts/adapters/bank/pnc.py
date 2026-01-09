import pandas as pd

from accounts.adapters.bank.bank_account import BankAccount
from transaction import Transaction


class PNC(BankAccount):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.date_normalizer = lambda df: pd.to_datetime(df["Transaction Date"])
        self.amount_normalizer = lambda df: pd.to_numeric(
            df["Amount"].str.replace(r"[\+\$\s]", "", regex=True)
        )
        self.description_normalizer = lambda df: df["Transaction Description"]

    def is_transaction_income(self, transaction: Transaction) -> bool:
        """Determine if a normalized transaction is income."""
        return (
            super().is_transaction_income(transaction)
            and "COMCAST (CC) OF" in transaction.description
        )

    def is_transaction_interest(self, transaction: Transaction) -> bool:
        """Determine if a normalized transaction is interest income."""
        return (
            super().is_transaction_interest(transaction)
            and "INTEREST PAYMENT" in transaction.description
        )
