from accounts.adapters.account import Account
from tracking.category import Category
from transaction import Transaction


class Jody(Category):
    def __init__(self, label):
        super().__init__(label)

    def filter_function(self, account: Account, transaction: Transaction) -> bool:
        return transaction.description == "Deposit Internet Transfer from 708226014 CK"
