import pandas as pd

from accounts.adapters.account import Account
from tracking.category import Category


class Transfer(Category):
    def __init__(self, label):
        super().__init__(label)

    def filter_function(self, account: Account, transaction: pd.Series) -> bool:
        return transaction.is_transfer
