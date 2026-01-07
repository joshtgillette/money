import pandas as pd
from typing import Optional

from accounts.adapters.credit.credit_card import CreditCard


class Apple(CreditCard):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    def normalize(self) -> None:
        """Convert Apple's CSV format to standard transaction format."""
        if self.raw_transactions.empty:
            return

        self._build_transactions_from_dataframe(
            pd.DataFrame(
                {
                    "date": pd.to_datetime(self.raw_transactions["Transaction Date"]),
                    "amount": pd.Series(
                        pd.to_numeric(self.raw_transactions["Amount (USD)"])
                    )
                    * -1,
                    "description": self.raw_transactions["Description"],
                }
            )
            .sort_values("date")
            .reset_index(drop=True)
        )
