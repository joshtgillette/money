from accounts.adapters.credit.credit_account import CreditAccount
import pandas as pd

class WellsFargo(CreditAccount):

    def __init__(self):
        super().__init__("Wells Fargo Credit Card")

    def normalize(self):
        """Convert Wells Fargo's CSV format to standard transaction format."""
        if self.raw_transactions.empty:
            return

        self.transactions = pd.DataFrame({
            'date': pd.to_datetime(self.raw_transactions.iloc[:, 0]),
            'amount': pd.to_numeric(pd.to_numeric(self.raw_transactions.iloc[:, 1])),
            'description': self.raw_transactions.iloc[:, 4]
        }).sort_values('date').reset_index(drop=True)
