import pandas as pd

from accounts.adapters.credit.credit_card import CreditCard


class WellsFargo(CreditCard):
    def __init__(self, name: str):
        super().__init__(name)
        self.header_val = None  # Wells Fargo does not provide CSV header

    def normalize(self):
        """Convert Wells Fargo's CSV format to standard transaction format."""
        if self.raw_transactions.empty:
            return

        df = (
            pd.DataFrame(
                {
                    "date": pd.to_datetime(self.raw_transactions.iloc[:, 0]),
                    "amount": pd.to_numeric(
                        pd.to_numeric(self.raw_transactions.iloc[:, 1])
                    ),
                    "description": self.raw_transactions.iloc[:, 4],
                }
            )
            .sort_values("date")
            .reset_index(drop=True)
        )
        
        self._build_transactions_from_dataframe(df)
