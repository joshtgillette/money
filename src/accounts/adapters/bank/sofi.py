import pandas as pd

from accounts.adapters.bank.bank_account import BankAccount


class SoFi(BankAccount):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.date_normalizer = lambda df: pd.to_datetime(df["Date"])
        self.amount_normalizer = lambda df: pd.to_numeric(df["Amount"])
        self.description_normalizer = lambda df: df["Description"]
