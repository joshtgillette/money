from datetime import datetime
from typing import Any


class Transaction:
    """A typed class representing a single financial transaction."""
    
    # Core attributes that should not be stored in _extra_attributes
    _CORE_ATTRS = frozenset(["date", "amount", "description", "Index", "is_transfer", "_extra_attributes"])

    def __init__(
        self,
        date: datetime,
        amount: float,
        description: str,
        index: int,
        is_transfer: bool = False,
    ):
        self.date = date
        self.amount = amount
        self.description = description
        self.Index = index  # Keep Index capitalized for compatibility with pandas itertuples
        self.is_transfer = is_transfer
        self._extra_attributes = {}  # For category flags and other dynamic attributes

    def __getattr__(self, name: str) -> Any:
        """Allow access to dynamically added category attributes."""
        if name in self._extra_attributes:
            return self._extra_attributes[name]
        raise AttributeError(
            f"'Transaction' object has no attribute '{name}'"
        )

    def __setattr__(self, name: str, value: Any) -> None:
        """Allow setting dynamically added category attributes."""
        if name in Transaction._CORE_ATTRS:
            super().__setattr__(name, value)
        else:
            if not hasattr(self, "_extra_attributes"):
                super().__setattr__("_extra_attributes", {})
            self._extra_attributes[name] = value

    def __repr__(self) -> str:
        return f"Transaction(date={self.date}, amount={self.amount}, description='{self.description}', Index={self.Index})"
