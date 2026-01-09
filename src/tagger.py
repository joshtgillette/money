import hashlib
import os
from typing import Dict

import pandas as pd

from transaction import Transaction


class Tagger:
    """Manages transaction tags loaded from CSV files."""

    TRANSACTIONS_PATH: str = "transactions"

    def __init__(self) -> None:
        self.tags: Dict[str, str] = {}  # hash -> comma-separated tags (lowercase)

    def load_existing_tags(self, banker) -> None:
        """Load tags from a CSV file containing transaction data.

        Args:
            banker: Banker to discover csvs
        """

        for csv_path in banker.discover_csvs(self.TRANSACTIONS_PATH):
            try:
                df = pd.read_csv(csv_path)
                # Check if the file has the expected columns
                required_cols = ["date", "amount", "description", "tag"]
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
                        tag_value = (
                            "" if pd.isna(row["tag"]) else str(row["tag"]).strip()
                        )
                        self.set_tags(
                            amount=amount,
                            description=str(row["description"]),
                            date=str(row["date"]),
                            tags=tag_value,
                        )
                    except (ValueError, TypeError) as e:
                        print(
                            f"Warning: Invalid data in {os.path.basename(csv_path)} for amount '{row['amount']}': {e}"
                        )
                        continue
            except Exception as e:
                print(
                    f"Warning: Could not load tags from {os.path.basename(csv_path)}: {e}"
                )

    def set_tags(self, amount: float, description: str, date: str, tags: str) -> None:
        """Set tags for a transaction using raw data.

        Args:
            amount: Transaction amount
            description: Transaction description
            date: Transaction date (should be YYYY-MM-DD format)
            tags: Comma-separated tags (will be normalized to lowercase)
        """
        # Normalize tags to lowercase and strip whitespace
        if not tags.strip():
            normalized = ""
        else:
            normalized = ",".join(
                tag.strip().lower() for tag in tags.split(",") if tag.strip()
            )

        if normalized:
            self.tags[self.hash_transaction(date, amount, description)] = normalized
        else:
            # Remove tag if empty
            self.tags.pop(self.hash_transaction(date, amount, description), None)

    def hash_transaction(self, date: str, amount: float, description: str) -> str:
        """Generate a unique hash for a transaction.

        Uses date, account, amount and description to create a consistent identifier.

        Args:
            date: Transaction date (YYYY-MM-DD format string)
            amount: Transaction amount
            description: Transaction description

        Returns:
            SHA256 hash of the transaction data
        """
        return hashlib.sha256(
            f"{pd.to_datetime(date).strftime('%Y-%m-%d')}|{amount}|{description}".encode()
        ).hexdigest()

    def apply_tags_to_transactions(self, banker) -> None:
        """Apply loaded tags to transaction objects as separate attributes.

        Args:
            banker: Banker instance containing accounts with transactions

        Tags are set as separate attributes on the transaction object.
        For example, "home improvement, school" becomes:
        - transaction.home_improvement = True
        - transaction.school = True
        """
        for _, transaction in banker:
            tags = self.get_tags(transaction)
            if tags:
                # Set each tag as a separate attribute (replace spaces with underscores)
                for tag in tags.split(","):
                    tag_clean = tag.strip()
                    if tag_clean:
                        # Convert tag to valid attribute name (replace spaces with underscores)
                        attr_name = tag_clean.replace(" ", "_")
                        setattr(transaction, attr_name, True)

    def get_tags(self, transaction: Transaction) -> str:
        """Get the tags for a transaction (empty string if none)."""
        return self.tags.get(
            self.hash_transaction(
                transaction.date.strftime("%Y-%m-%d")
                if hasattr(transaction.date, "strftime")
                else str(transaction.date),
                transaction.amount,
                transaction.description,
            ),
            "",
        )

    def write_transactions_with_tags(self, banker) -> None:
        """Write transactions to a directory with tags.

        Args:
            banker: Banker instance containing accounts with transactions
            self.TRANSACTIONS_PATH: Directory to write transaction CSV files to
        """
        # Clear and recreate output directory
        if os.path.exists(self.TRANSACTIONS_PATH):
            import shutil

            shutil.rmtree(self.TRANSACTIONS_PATH)
        os.makedirs(self.TRANSACTIONS_PATH, exist_ok=True)

        # Collect all transactions with tags into a DataFrame
        transactions_data = []
        for _, transaction in banker:
            # Collect all tag attributes from _extra_attributes
            tag_attrs = []
            if hasattr(transaction, "_extra_attributes"):
                for attr, value in transaction._extra_attributes.items():
                    if value is True:
                        tag_attrs.append(attr.replace("_", " "))
            tags = ",".join(sorted(tag_attrs)) if tag_attrs else ""

            transactions_data.append(
                {
                    "date": transaction.date,
                    "account": transaction.account,
                    "amount": transaction.amount,
                    "description": transaction.description,
                    "tag": tags,
                }
            )

        if not transactions_data:
            return

        # Create DataFrame and group by month
        df = pd.DataFrame(transactions_data)
        df["date"] = pd.to_datetime(df["date"])

        # Write each month's transactions to a separate CSV
        for month, group in df.groupby(df["date"].dt.to_period("M")):
            # Format as MMYY.csv (e.g., 0525.csv for May 2025)
            filename = f"{pd.Period(month).strftime('%m%y')}.csv"
            filepath = os.path.join(self.TRANSACTIONS_PATH, filename)

            # Sort and write using pandas
            group_sorted = group.sort_values("date").reset_index(drop=True)
            group_sorted.to_csv(
                filepath,
                columns=["date", "account", "amount", "description", "tag"],
                index=False,
            )
