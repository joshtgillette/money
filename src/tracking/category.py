from abc import ABC, abstractmethod
import pandas as pd
from banking.banker import Banker

class Category(ABC):

    def __init__(self, label):
        self.label = label
        self.transactions = pd.DataFrame()

    def filter(self, banker: Banker):
        """Filter income transactions from all accounts."""
        filtered_transactions = []
        for account, transaction in banker:
            if self.filter_function(account, transaction):
                filtered_transactions.append(transaction)

        if filtered_transactions:
            self.transactions = pd.DataFrame(filtered_transactions)

    @abstractmethod
    def filter_function(self, transactions: pd.DataFrame):
        """Override this method to provide filter function"""
        pass
