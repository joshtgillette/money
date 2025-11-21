from accounts.adapters.credit.credit_account import CreditAccount
import pandas as pd

class Chase(CreditAccount):

    def __init__(self):
        super().__init__("Chase Credit Card")

    def normalize(self):
        """Convert Chase's CSV format to standard transaction format."""
        if self.raw_transactions.empty:
            return

        self.transactions = pd.DataFrame({
            'date': pd.to_datetime(self.raw_transactions['Transaction Date']),
            'amount': pd.to_numeric(pd.to_numeric(self.raw_transactions['Amount'])),
            'description': self.raw_transactions['Description']
        }).sort_values('date').reset_index(drop=True)
