"""Transaction model representing a single financial transaction."""

from datetime import datetime
from typing import Any, List

import pandas as pd


class Transaction:
    """Represents a single financial transaction with account, date, amount, and description."""

    account: str
    date: datetime
    amount: float
    description: str
    tags: List[str]

    def __init__(self, df: Any) -> None:
        """Initialize a transaction from a pandas DataFrame row.

        Args:
            df: A pandas named tuple or row containing transaction data.
        """

        self.account = df.account
        self.date = pd.to_datetime(df.date)
        self.amount = df.amount
        self.description = df.description

    def set_tags(self, tags: List[str]) -> None:
        """Set tags for this transaction.

        Args:
            tags: List of tag strings to associate with this transaction.
        """

        self.tags = tags

    def get_account(self) -> str:
        """Get the account name for this transaction.

        Returns:
            The account name as a string.
        """

        return self.account

    def get_date(self) -> str:
        """Get the formatted date string for this transaction.

        Returns:
            Date formatted as "Month Day, Year" (e.g., "January 15, 2025").
        """

        return self.date.strftime("%B %d, %Y")

    def get_amount(self) -> str:
        """Get the formatted amount string for this transaction.

        Returns:
            Amount formatted with sign and currency (e.g., "+$1,234.56" or "-$500.00").
        """

        return f"{'+' if self.amount > 0 else '-'}${abs(self.amount):,.2f}"

    def get_description(self) -> str:
        """Get the description for this transaction.

        Returns:
            The transaction description as a string.
        """

        return self.description

    def get_tags(self) -> str:
        """Get comma-separated tags for this transaction.

        Returns:
            Comma-separated string of all tags (e.g., "food, groceries, essential").
        """

        return ", ".join(self.tags)

    def hash(self) -> str:
        """Generate a unique hash string for this transaction.

        Returns:
            A formatted string combining all transaction fields for unique identification.
        """

        return f"{self.get_account()} on {self.get_date()} for {self.get_amount()} - {self.get_description()}"

    def for_tabulate(self) -> tuple[str, str, str, str, str]:
        """Convert transaction to a tuple format suitable for tabulate display.

        Returns:
            Tuple of (account, date, amount, description, tags) as formatted strings.
        """

        return (
            self.get_account(),
            self.get_date(),
            self.get_amount(),
            self.get_description(),
            self.get_tags(),
        )
