import hashlib
from datetime import datetime
from typing import Any, Dict, List


class Transaction:
    """Represents a financial transaction with tagging capabilities."""

    __slots__ = (
        "index",
        "account_name",
        "date",
        "amount",
        "description",
        "account",
        "_tags",
    )

    def __init__(
        self,
        index: int,
        account_name: str,
        date: datetime,
        amount: float,
        description: str,
        tags: str = "",
    ) -> None:
        """Initialize a transaction with core financial data and optional tags."""
        self.index: int = index
        self.account_name: str = account_name
        self.date: datetime = date
        self.amount: float = amount
        self.description: str = description
        self._tags: Dict[str, bool] = {}  # For tags
        self.set_tags(tags)

    def set_tags(self, tags_val: str) -> None:
        """Parse and store tags from a pipe-separated string."""
        for tag in tags_val.split("|"):
            tag = tag.strip().replace(" ", "_")
            if not tag:
                continue

            self._tags[tag] = True

    def get_tags_val(self) -> str:
        """Return all tags as a pipe-separated string."""
        return "|".join([tag.replace("_", " ") for tag in self._tags])

    def get_tags(self) -> List[str]:
        return list(self._tags.keys())

    def __getattr__(self, name: str) -> Any:
        """Allow access to tags as dynamic attributes."""
        name = name.replace(" ", "_")
        return self._tags.get(name.lower(), False) or self._tags.get(
            name.upper(), False
        )

    def __setattr__(self, name: str, value: Any) -> None:
        """Allow setting tags as dynamic attributes."""
        if name in Transaction.__slots__:
            super().__setattr__(name, value)
            return

        self._tags[name] = value

    def hash(self) -> str:
        """Generate a unique hash identifier for this transaction.

        Returns:
            SHA256 hash of the transaction's date, amount, and description
        """
        return hashlib.sha256(
            f"{self.account_name}{self.date.strftime('%Y-%m-%d')}{self.amount}{self.description}".encode()
        ).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to a dictionary suitable for DataFrame creation.

        Returns:
            Dictionary containing transaction data with tag information
        """

        return {
            "account": self.account_name,
            "date": self.date,
            "amount": self.amount,
            "description": self.description,
            "tags": self.get_tags_val(),
        }

    def __repr__(self) -> str:
        return f"{self.account_name}, {self.description} on {self.date.strftime('%m/%d/%y')} for {self.amount}"
