from accounts.adapters.account import Account
import pandas as pd
from abc import ABC, abstractmethod

class BankAccount(Account, ABC):

    def __init__(self, name: str):
        super().__init__(name)

    @abstractmethod
    def is_transaction_income(self, transaction: pd.Series) -> bool:
        """Determine if a normalized transaction is income.

        This method must be implemented by each bank-specific subclass
        to identify income transactions based on their unique
        characteristics.
        """

        return transaction.amount > 0

    @abstractmethod
    def is_transaction_interest(self, transaction: pd.Series) -> bool:
        """Determine if a normalized transaction is interest income.

        This method must be implemented by each bank-specific subclass
        to identify interest income transactions based on their unique
        characteristics.
        """

        return (transaction.amount > 0 and
                "interest" in transaction.description.lower())
