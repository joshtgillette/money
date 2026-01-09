import pandas as pd

from accounts.adapters.credit.credit_card import CreditCard


class Apple(CreditCard):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.date_normalizer = lambda df: pd.to_datetime(df["Transaction Date"])
        self.amount_normalizer = lambda df: pd.to_numeric(df["Amount (USD)"]) * -1
        self.description_normalizer = lambda df: df["Description"]
