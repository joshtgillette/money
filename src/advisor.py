import os
import shutil

import pandas as pd

from accounts.banker import Banker
from report import Report
from tag_manager import TagManager


class Advisor:
    TRANSACTIONS_PATH: str = "transactions"

    def __init__(self, banker: Banker) -> None:
        self.banker: Banker = banker
        self.report: Report = Report()
        self.tag_manager: TagManager = TagManager()

    def start(self) -> None:
        # Direct the banker to load transactions for the specified date range
        self.banker.load()
        if sum(len(account.transactions) for account in self.banker.accounts) == 0:
            self.report.note("No transactions loaded.")
            return

        # self.report.note_header("TRANSFER REMOVAL")
        # self.banker.identify_returns()
        # self.banker.identify_transfers()
        # self.report.note(self.banker.get_log())

        # Write transactions data to the report
        transactions: pd.DataFrame = self.banker.get_transactions()
        self.report.write_transactions(transactions, "all")
        # non_transfer_transactions: pd.DataFrame = self.banker.get_transactions(
        #     lambda t: not t.is_transfer
        # )
        # self.report.write_transactions(non_transfer_transactions, "all - no transfers")
        self.report.note(
            f"loaded {len(self.banker.accounts)} bank accounts "
            f"with {len(transactions)} total transactions\n"
            # f"{len(non_transfer_transactions)} non-transfers\n"
        )

        # Write account transactions - pass transaction lists directly
        for account in self.banker.accounts:
            if account.transactions:
                self.report.write_transactions(
                    account.transactions.values(),
                    f"accounts/{account.name.lower()}",
                    columns=["date", "amount", "description"],
                )

        # Recreate transactions directory with tags
        self._write_transactions_with_tags()

        # Write monthly transactions to report
        for month, group in transactions.groupby(
            transactions["date"].dt.to_period("M")
        ):
            self.report.write_transactions(
                group,
                f"monthly/{pd.Period(month).strftime('%m%y')}.csv",
            )

        # Generate tag-based reports
        self._generate_tag_reports()

    def _write_transactions_with_tags(self) -> None:
        """Write transactions to the transactions/ directory with tags."""
        # Clear and recreate transactions directory
        if os.path.exists(self.TRANSACTIONS_PATH):
            shutil.rmtree(self.TRANSACTIONS_PATH)
        os.makedirs(self.TRANSACTIONS_PATH, exist_ok=True)

        # Collect all transactions with tags
        transactions_data = []
        for account, transaction in self.banker:
            tags = self.tag_manager.get_tags(transaction)
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

        for month, group in df.groupby(df["date"].dt.to_period("M")):
            # Format as MMYY.csv (e.g., 0525.csv for May 2025)
            filename = f"{pd.Period(month).strftime('%m%y')}.csv"
            filepath = os.path.join(self.TRANSACTIONS_PATH, filename)

            # Sort by date and write to CSV
            group_sorted = group.sort_values("date").reset_index(drop=True)
            group_sorted.to_csv(
                filepath,
                columns=["date", "account", "amount", "description", "tag"],
                index=False,
            )

    def _generate_tag_reports(self) -> None:
        """Generate tag-based reports in report/transactions/tags/."""
        tags_report_path = os.path.join(self.report.DATA_PATH, "tags")
        os.makedirs(tags_report_path, exist_ok=True)

        # Collect all transactions with their tags
        transactions_by_tag = {}  # tag -> list of transactions
        untagged_transactions = []

        for account, transaction in self.banker:
            tags = self.tag_manager.get_tags(transaction)
            transaction_data = {
                "date": transaction.date,
                "account": transaction.account,
                "amount": transaction.amount,
                "description": transaction.description,
            }

            if tags:
                # Split comma-separated tags and add to each tag's list
                for tag in tags.split(","):
                    tag = tag.strip()
                    if tag not in transactions_by_tag:
                        transactions_by_tag[tag] = []
                    transactions_by_tag[tag].append(transaction_data)
            else:
                untagged_transactions.append(transaction_data)

        # Write a CSV for each tag
        for tag, transactions in transactions_by_tag.items():
            # Sanitize tag name for use in file path
            safe_tag = self._sanitize_filename(tag)
            df = pd.DataFrame(transactions)
            df = df.sort_values("date").reset_index(drop=True)
            filepath = os.path.join(tags_report_path, f"{safe_tag}.csv")
            df.to_csv(filepath, index=False)

        # Write untagged transactions
        if untagged_transactions:
            df = pd.DataFrame(untagged_transactions)
            df = df.sort_values("date").reset_index(drop=True)
            filepath = os.path.join(tags_report_path, "untagged.csv")
            df.to_csv(filepath, index=False)

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize a string for safe use as a filename.

        Removes path traversal characters and other unsafe characters.
        Also handles Windows reserved names.
        """
        # Remove path separators and other dangerous characters
        safe_name = filename.replace("/", "_").replace("\\", "_").replace("..", "_")
        # Remove any other potentially problematic characters
        safe_name = "".join(
            c for c in safe_name if c.isalnum() or c in (" ", "_", "-")
        )
        # Strip leading/trailing whitespace and periods
        safe_name = safe_name.strip(". ")
        # Handle Windows reserved names
        reserved_names = {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        }
        if safe_name.upper() in reserved_names:
            safe_name = f"tag_{safe_name}"
        # Ensure the name isn't empty after sanitization
        return safe_name if safe_name else "unknown"
