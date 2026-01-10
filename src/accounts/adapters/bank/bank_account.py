"""Base class for bank accounts."""

from abc import ABC

from accounts.adapters.account import Account


class BankAccount(Account, ABC):
    """Abstract base class for traditional bank checking and savings accounts."""
    
    def __init__(self, name: str) -> None:
        """Initialize a bank account with the given name."""
        super().__init__(name)
