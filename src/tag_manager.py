import hashlib
import os
from typing import Dict

import pandas as pd

from transaction import Transaction


class TagManager:
    """Manages transaction tags loaded from CSV files."""

    def __init__(self) -> None:
        self.tags: Dict[str, str] = {}  # hash -> comma-separated tags (lowercase)

    def hash_transaction(self, transaction: Transaction) -> str:
        """Generate a unique hash for a transaction.

        Uses date, account, amount and description to create a consistent identifier.
        """
        # Use just the date part (YYYY-MM-DD) for consistency with CSV data
        date_str = transaction.date.strftime('%Y-%m-%d') if hasattr(transaction.date, 'strftime') else str(transaction.date)
        transaction_str = f"{date_str}|{transaction.account}|{transaction.amount}|{transaction.description}"
        return hashlib.sha256(transaction_str.encode()).hexdigest()

    def get_tags(self, transaction: Transaction) -> str:
        """Get the tags for a transaction (empty string if none)."""
        return self.tags.get(self.hash_transaction(transaction), "")

    def _normalize_tags(self, tags: str) -> str:
        """Normalize tags to lowercase and strip whitespace.

        Args:
            tags: Comma-separated tags

        Returns:
            Normalized comma-separated tags, or empty string if no valid tags
        """
        if not tags.strip():
            return ""
        return ",".join(
            tag.strip().lower() for tag in tags.split(",") if tag.strip()
        )

    def set_tags(self, amount: float, description: str, date: str, account: str, tags: str) -> None:
        """Set tags for a transaction using raw data.

        Args:
            amount: Transaction amount
            description: Transaction description
            date: Transaction date (should be YYYY-MM-DD format)
            account: Transaction account
            tags: Comma-separated tags (will be normalized to lowercase)
        """
        # Normalize date to YYYY-MM-DD format
        import pandas as pd
        date_normalized = pd.to_datetime(date).strftime('%Y-%m-%d')
        transaction_str = f"{date_normalized}|{account}|{amount}|{description}"
        tx_hash = hashlib.sha256(transaction_str.encode()).hexdigest()
        normalized = self._normalize_tags(tags)

        if normalized:
            self.tags[tx_hash] = normalized
        else:
            # Remove tag if empty
            self.tags.pop(tx_hash, None)

    def load_tags_from_csv(self, csv_path: str) -> None:
        """Load tags from a CSV file containing transaction data.

        Args:
            csv_path: Path to the CSV file with transaction data and tags

        The CSV file should have columns: date, account, amount, description, tag
        """
        if not os.path.exists(csv_path):
            return

        try:
            df = pd.read_csv(csv_path)
            # Check if the file has the expected columns
            required_cols = ["date", "account", "amount", "description", "tag"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                print(
                    f"Warning: Skipping {os.path.basename(csv_path)} - missing columns: {', '.join(missing_cols)}"
                )
                return

            # Load tags from the CSV file
            for _, row in df.iterrows():
                try:
                    amount = float(row["amount"])
                    # Process all rows, including those with empty tags (for removal)
                    tag_value = "" if pd.isna(row["tag"]) else str(row["tag"]).strip()
                    self.set_tags(
                        amount=amount,
                        description=str(row["description"]),
                        date=str(row["date"]),
                        account=str(row["account"]),
                        tags=tag_value,
                    )
                except (ValueError, TypeError) as e:
                    print(
                        f"Warning: Invalid data in {os.path.basename(csv_path)} for amount '{row['amount']}': {e}"
                    )
                    continue
        except Exception as e:
            print(f"Warning: Could not load tags from {os.path.basename(csv_path)}: {e}")

    def apply_tags_to_transactions(self, banker) -> None:
        """Apply loaded tags to transaction objects.

        Args:
            banker: Banker instance containing accounts with transactions
        """
        for account, transaction in banker:
            tags = self.get_tags(transaction)
            if tags:
                transaction.tag = tags
