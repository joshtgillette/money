from accounts.adapters.account import Account
from abc import ABC

class CreditCard(Account, ABC):

    def __init__(self, name: str):
        super().__init__(name)
