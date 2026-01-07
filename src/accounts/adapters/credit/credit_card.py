from abc import ABC

from accounts.adapters.account import Account


class CreditCard(Account, ABC):
    def __init__(self, name: str) -> None:
        super().__init__(name)
