"""Chase credit card adapter."""

import pandas as pd

from accounts.adapters.credit.credit_card import CreditCard


class Chase(CreditCard):
    """Adapter for Chase credit card accounts."""
    
    def __init__(self, name: str) -> None:
        """Initialize Chase account with data normalization functions."""
        super().__init__(name)
        self.date_normalizer = lambda df: pd.to_datetime(df["Transaction Date"])
        self.amount_normalizer = lambda df: pd.to_numeric(df["Amount"])
        self.description_normalizer = lambda df: df["Description"]
