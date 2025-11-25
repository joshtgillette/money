from accounts.adapters.account import Account
from abc import ABC

class CreditCard(Account, ABC):

    def __init__(self, bank_name: str, type: str = "Credit Card"):
        super().__init__(bank_name, type)
