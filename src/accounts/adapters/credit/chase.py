import pandas as pd

from accounts.adapters.credit.credit_card import CreditCard


class Chase(CreditCard):
    def __init__(self, name: str):
        super().__init__(name)

    def normalize(self):
        """Convert Chase's CSV format to standard transaction format."""
        if self.raw_transactions.empty:
            return

        df = (
            pd.DataFrame(
                {
                    "date": pd.to_datetime(self.raw_transactions["Transaction Date"]),
                    "amount": pd.to_numeric(
                        pd.to_numeric(self.raw_transactions["Amount"])
                    ),
                    "description": self.raw_transactions["Description"],
                }
            )
            .sort_values("date")
            .reset_index(drop=True)
        )
        
        self._build_transactions_from_dataframe(df)
