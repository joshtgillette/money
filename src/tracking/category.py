from abc import ABC, abstractmethod

import pandas as pd

from accounts.banker import Banker


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
            try:
                account.transactions.loc[transaction.Index, self.label] = (
                    self.filter_function(account, transaction)
                )
            except AttributeError:
                continue

    @abstractmethod
    def filter_function(self, transactions: pd.DataFrame):
        """Override this method to provide filter function"""
        pass
