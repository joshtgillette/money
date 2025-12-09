import pandas as pd

from accounts.adapters.account import Account
from accounts.adapters.bank.bank_account import BankAccount
from tracking.category import Category


class Interest(Category):
    def __init__(self, label):
        super().__init__(label)

    def filter_function(self, account: Account, transaction: pd.Series) -> bool:
        if not isinstance(account, BankAccount):
            return False

        return account.is_transaction_interest(transaction)
