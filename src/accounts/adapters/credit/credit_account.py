from accounts.adapters.account import Account
from abc import ABC

class CreditAccount(Account, ABC):

    def __init__(self, bank_name: str, type: str = ""):
        super().__init__(bank_name, type)
