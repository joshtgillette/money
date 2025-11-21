from tracking.category import Category
from accounts.adapters.bank.bank_account import BankAccount
import pandas as pd

class Interest(Category):

    def __init__(self, label):
        super().__init__(label)

    def filter_function(self, account: BankAccount, transaction: pd.Series):
        return account.is_transaction_interest(transaction)
