import hashlib
from datetime import datetime
from typing import Any, Dict

import pandas as pd


class Transaction:
    __slots__ = (
        "index",
        "date",
        "amount",
        "description",
        "account",
        "_tags",
    )

    def __init__(
        self,
        index: int,
        date: datetime,
        amount: float,
        description: str,
        tags: str = "",
    ) -> None:
        self.index: int = index
        self.date: datetime = date
        self.amount: float = amount
        self.description: str = description
        self._tags: Dict[str, bool] = {}  # For tags
        self.set_tags(tags)

    def set_tags(self, tags):
        if tags and pd.notna(tags):
            for tag in tags.split("|"):
                tag = tag.strip()
                if not tag:
                    continue

                self._tags[tag] = True

    def __getattr__(self, name: str) -> Any:
        """Allow access to dynamically added attributes."""
        return self._tags.get(name, False)

    def __setattr__(self, name: str, value: Any) -> None:
        """Allow setting dynamically added attributes."""
        if name in Transaction.__slots__:
            super().__setattr__(name, value)
            return

        if not hasattr(self, "_tags"):
            super().__setattr__("_tags", {})
        if value:
            self._tags[name] = value
        elif name in self._tags:
            del self._tags[name]

    def get_tags(self) -> str:
        return "|".join(self._tags)

    def hash(self) -> str:
        """Generate a unique hash of a transaction.

        Returns:
            SHA256 hash of the transaction data
        """
        return hashlib.sha256(
            f"{pd.to_datetime(self.date).strftime('%Y-%m-%d')}|{self.amount}|{self.description}".encode()
        ).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary for DataFrame creation.

        Returns:
            Dictionary with core attributes and tag columns.
        """

        data = {
            "date": self.date,
            "amount": self.amount,
            "description": self.description,
            "tags": self.get_tags(),
        }

        return data

    def __repr__(self) -> str:
        return f"{self.amount} on {self.date} - {self.description}"
