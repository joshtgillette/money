from accounts.adapters.account import Account
from tracking.category import Category
from transaction import Transaction


class Transfer(Category):
    def __init__(self, label: str) -> None:
        super().__init__(label)

    def filter_function(self, account: Account, transaction: Transaction) -> bool:
        return transaction.is_transfer
