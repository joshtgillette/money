from accounts.adapters.bank.bank_account import BankAccount
import pandas as pd

class Apple(BankAccount):

    def __init__(self, type: str = ""):
        super().__init__("Apple", type)
        self.raw_transactions = pd.DataFrame()

    def normalize(self):
        """Convert Apple's CSV format to standard transaction format."""
        if self.raw_transactions.empty:
            return

        self.transactions = pd.DataFrame({
            'date': pd.to_datetime(self.raw_transactions['Transaction Date']),
            'amount': pd.to_numeric(
                self.raw_transactions['Amount']).where(
                    self.raw_transactions['Transaction Type'] == 'Credit',
                    -pd.to_numeric(self.raw_transactions['Amount'])
                ),
            'description': self.raw_transactions['Description']
        }).sort_values('date').reset_index(drop=True)

    def is_transaction_income(self, transaction: pd.Series) -> bool:
        """Determine if a normalized transaction is income."""
        return (super().is_transaction_income(transaction) and
                'ACH Transfer from COMCAST (CC) OF PAYROLL' in transaction.description)

    def is_transaction_interest(self, transaction: pd.Series) -> bool:
        """Determine if a normalized transaction is interest income."""
        return (super().is_transaction_interest(transaction) and
                'Interest Paid' in transaction.description)
