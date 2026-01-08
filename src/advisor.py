import os

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
        # Load existing tags from transactions directory before loading new data
        self.tag_manager.load_tags_from_directory(self.TRANSACTIONS_PATH)

        # Direct the banker to load transactions for the specified date range
        self.banker.load()
        if sum(len(account.transactions) for account in self.banker.accounts) == 0:
            self.report.note("No transactions loaded.")
            return

        # Apply tags to loaded transactions
        self.tag_manager.apply_tags_to_transactions(self.banker)

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
        self.tag_manager.write_transactions_with_tags(
            self.banker, self.TRANSACTIONS_PATH
        )

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

    def _generate_tag_reports(self) -> None:
        """Generate tag-based reports in report/transactions/tags/."""
        tags_report_path = os.path.join(self.report.DATA_PATH, "tags")
        os.makedirs(tags_report_path, exist_ok=True)

        # Collect all transactions with their tags
        transactions_by_tag = {}  # tag -> list of transactions
        untagged_transactions = []

        for account, transaction in self.banker:
            # Check for tag attributes in _extra_attributes
            tag_attrs = []
            if hasattr(transaction, "_extra_attributes"):
                for attr, value in transaction._extra_attributes.items():
                    if value is True:
                        tag_attrs.append(attr.replace("_", " "))

            transaction_data = {
                "date": transaction.date,
                "account": transaction.account,
                "amount": transaction.amount,
                "description": transaction.description,
            }

            if tag_attrs:
                # Add transaction to each tag's list
                for tag in tag_attrs:
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
        """
        # Remove path separators and other dangerous characters
        safe_name = filename.replace("/", "_").replace("\\", "_").replace("..", "_")
        # Remove any other potentially problematic characters
        safe_name = "".join(c for c in safe_name if c.isalnum() or c in (" ", "_", "-"))
        # Strip leading/trailing whitespace and periods
        safe_name = safe_name.strip(". ")
        # Ensure the name isn't empty after sanitization
        return safe_name if safe_name else "unknown"
