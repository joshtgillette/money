"""Wells Fargo credit card adapter."""

import pandas as pd

from accounts.adapters.credit.credit_card import CreditCard


class WellsFargo(CreditCard):
    """Adapter for Wells Fargo credit card accounts."""

    def __init__(self, name: str) -> None:
        """Initialize Wells Fargo account with data normalization functions."""
        super().__init__(name)
        self.header_val = None  # Wells Fargo does not provide CSV header
        self.date_normalizer = lambda df: pd.to_datetime(df.iloc[:, 0])
        self.amount_normalizer = lambda df: pd.to_numeric(df.iloc[:, 1])
        self.description_normalizer = lambda df: df.iloc[:, 4]
