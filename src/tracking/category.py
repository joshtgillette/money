from abc import ABC, abstractmethod
import pandas as pd
from banking.banker import Banker

class Category(ABC):

    def __init__(self, label):
        self.label = label

    def apply_filter(self, banker: Banker):
        """Filter income transactions from all accounts."""

        # Initialize the category column
        for account in banker.accounts:
            account.transactions[self.label] = False

        # Apply the filter function to each transaction
        for account, transaction in banker:
            if self.filter_function(account, transaction):
                account.transactions.loc[transaction.Index, self.label] = True

    @abstractmethod
    def filter_function(self, transactions: pd.DataFrame):
        """Override this method to provide filter function"""
        pass
