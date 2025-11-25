from datetime import datetime
import pandas as pd
from abc import ABC, abstractmethod

class Account(ABC):

    TRANSACTIONS_PATH = "transactions"

    def __init__(self, account_name: str, type: str = ""):
        self.name = f"{account_name} {type}".strip()
        self.raw_transactions = pd.DataFrame()
        self.transactions = pd.DataFrame(columns=[
            'date',
            'amount',
            'description',
        ])
        self.header_val = 0

    def load_transactions(self, dates: list[datetime]) -> pd.DataFrame:
        """Load transactions from a CSV file into a pandas DataFrame."""

        for date in dates:
            path = f"{self.TRANSACTIONS_PATH}/{date.strftime('%m%y')}/{self.name.lower()}.csv"
            try:
                self.raw_transactions = pd.concat([self.raw_transactions, pd.read_csv(path, header=self.header_val)], ignore_index=True)
            except FileNotFoundError:
                continue

    @abstractmethod
    def normalize(self):
        """Normalize raw transaction data to standard format.

        This method must be implemented by each account adapter
        to handle their unique CSV format and transform it into the
        standard format with columns: ['date', 'description', 'amount']
        """
        pass
