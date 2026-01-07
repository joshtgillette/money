from abc import ABC, abstractmethod

from accounts.adapters.account import Account
from accounts.banker import Banker
from transaction import Transaction


class Category(ABC):
    def __init__(self, label):
        self.label = label

    def apply_filter(self, banker: Banker):
        """Filter income transactions from all accounts."""

        # Initialize the category column
        for account in banker.accounts:
            account.transactions[self.label] = False
            for transaction in account.transaction_list:
                setattr(transaction, self.label, False)

        # Apply the filter function to each transaction
        for account, transaction in banker:
            try:
                result = self.filter_function(account, transaction)
                account.transactions.loc[transaction.Index, self.label] = result
                setattr(transaction, self.label, result)
            except AttributeError:
                continue

    @abstractmethod
    def filter_function(self, account: Account, transaction: Transaction) -> bool:
        """Override this method to provide filter function"""
        pass
