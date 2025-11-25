from accounts.adapters.credit.credit_card import CreditCard
import pandas as pd

class Apple(CreditCard):

    def __init__(self):
        super().__init__("Apple")

    def normalize(self):
        """Convert Apple's CSV format to standard transaction format."""
        if self.raw_transactions.empty:
            return

        self.transactions = pd.DataFrame({
            'date': pd.to_datetime(self.raw_transactions['Transaction Date']),
            'amount': -pd.to_numeric(pd.to_numeric(self.raw_transactions['Amount (USD)'])),
            'description': self.raw_transactions['Description']
        }).sort_values('date').reset_index(drop=True)
