"""Base class for credit card accounts."""

from abc import ABC

from accounts.adapters.account import Account


class CreditCard(Account, ABC):
    """Abstract base class for credit card accounts."""

    def __init__(self, name: str) -> None:
        """Initialize a credit card account with the given name."""
        super().__init__(name)
