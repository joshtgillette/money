"""Apple Card credit card adapter."""

import pandas as pd

from accounts.adapters.credit.credit_card import CreditCard


class Apple(CreditCard):
    """Adapter for Apple Card credit card accounts."""

    def __init__(self, name: str) -> None:
        """Initialize Apple Card account with data normalization functions."""
        super().__init__(name)
        self.date_normalizer = lambda df: pd.to_datetime(df["Transaction Date"])
        self.amount_normalizer = lambda df: pd.to_numeric(df["Amount (USD)"]) * -1
        self.description_normalizer = lambda df: df["Description"]
