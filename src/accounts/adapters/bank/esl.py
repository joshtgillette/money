import pandas as pd

from accounts.adapters.bank.bank_account import BankAccount


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
