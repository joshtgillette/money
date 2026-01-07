from accounts.adapters.account import Account
from tracking.category import Category
from transaction import Transaction


class Invest(Category):
    def __init__(self, label):
        super().__init__(label)

    def filter_function(self, account: Account, transaction: Transaction) -> bool:
        return transaction.description == "FID BKG SVC LLC"
