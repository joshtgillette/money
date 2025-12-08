import pandas as pd

from accounts.adapters.bank.bank_account import BankAccount
from tracking.category import Category


class Income(Category):
    def __init__(self, label):
        super().__init__(label)

    def filter_function(self, account: BankAccount, transaction: pd.Series):
        return account.is_transaction_income(transaction)
