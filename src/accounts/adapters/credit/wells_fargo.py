import pandas as pd

from accounts.adapters.credit.credit_card import CreditCard


class WellsFargo(CreditCard):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.header_val = None  # Wells Fargo does not provide CSV header
        self.date_normalizer = lambda df: pd.to_datetime(df.iloc[:, 0])
        self.amount_normalizer = lambda df: pd.to_numeric(df.iloc[:, 1])
        self.description_normalizer = lambda df: df.iloc[:, 4]
