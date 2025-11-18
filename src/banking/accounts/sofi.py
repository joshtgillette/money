from banking.accounts.bank_account import BankAccount
import pandas as pd

class SoFi(BankAccount):

    def __init__(self, type: str):
        super().__init__("SoFi", type)
        self.raw_transactions = pd.DataFrame()

    def normalize(self):
        """Convert SoFi's CSV format to standard transaction format."""
        if self.raw_transactions.empty:
            return

        self.transactions = pd.DataFrame({
            'date': pd.to_datetime(self.raw_transactions['Date']),
            'amount': pd.to_numeric(self.raw_transactions['Amount']),
            'description': self.raw_transactions['Description']
        }).sort_values('date').reset_index(drop=True)

        # Ignore Vault transactions, as they are one-sided transfers despite being
        # a zero-sum transfer with respect to the account. Should this be a category?
        self.transactions = self.transactions[~self.transactions['description'].str.contains('Vault')]

    def is_transaction_income(self, transaction: pd.Series) -> bool:
        """Determine if a normalized transaction is income."""
        return (super().is_transaction_income(transaction) and
                'COMCAST (CC) OF' in transaction.description)

    def is_transaction_interest(self, transaction: pd.Series) -> bool:
        """Determine if a normalized transaction is interest income."""
        return (super().is_transaction_interest(transaction) and
                'Interest earned' in transaction.description)
