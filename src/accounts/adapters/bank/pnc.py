from accounts.adapters.bank.bank_account import BankAccount
import pandas as pd

class PNC(BankAccount):

    def __init__(self, type: str = ""):
        super().__init__("PNC", type)
        self.raw_transactions = pd.DataFrame()

    def normalize(self):
        """Convert PNC's CSV format to standard transaction format."""
        if self.raw_transactions.empty:
            return

        self.transactions = pd.DataFrame({
            'date': pd.to_datetime(self.raw_transactions['Transaction Date']),
            'amount': pd.to_numeric(self.raw_transactions['Amount'].str.replace(r'[\+\$\s]', '', regex=True)),
            'description': self.raw_transactions['Transaction Description']
        }).sort_values('date').reset_index(drop=True)

    def is_transaction_income(self, transaction: pd.Series) -> bool:
        """Determine if a normalized transaction is income."""
        return (super().is_transaction_income(transaction) and
                'COMCAST (CC) OF' in transaction.description)

    def is_transaction_interest(self, transaction: pd.Series) -> bool:
        """Determine if a normalized transaction is interest income."""
        return (super().is_transaction_interest(transaction) and
                'INTEREST PAYMENT' in transaction.description)