import json
import os
from pathlib import Path
from typing import Dict

import pandas as pd

from accounts.banker import Banker
from transaction import Transaction


class Tagger:
    """Manages transaction tags loaded from CSV files."""

    TRANSACTIONS_PATH: str = "transactions"
    TAGS_PATH: Path = Path("tags.json")

    def __init__(self) -> None:
        self.tags: Dict[str, str] = {}  # hash -> comma-separated tags (lowercase)

    def load_existing_tags(self, banker: Banker) -> None:
        for csv_path in banker.discover_csvs(self.TRANSACTIONS_PATH):
            transactions: Dict[int, Transaction] = banker.load_transactions(
                pd.read_csv(csv_path)
            )
            for _, transaction in transactions.items():
                if not transaction._tags:
                    continue

                self.tags[transaction.hash()] = transaction.get_tags()

        # Save labels as fallback
        with Path(self.TAGS_PATH).open("w") as file:
            print(self.tags)
            json.dump(self.tags, file)

    def apply_tags(self, banker: Banker) -> None:
        for _, transaction in banker:
            tags: str | None = self.tags.get(transaction.hash(), None)
            if not tags:
                continue

            transaction.set_tags(tags)

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
            transactions_data.append(
                {
                    "date": transaction.date,
                    "account": transaction.account,
                    "amount": transaction.amount,
                    "description": transaction.description,
                    "tag": transaction.get_tags(),
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
