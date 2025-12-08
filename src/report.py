import os
import shutil

import pandas as pd


class Report:
    PATH = "report"
    FULL_DATA_PATH = f"{PATH}/transactions/full"
    MONTHLY_DATA_PATH = f"{PATH}/transactions/monthly"
    NOTES_FILE = f"{PATH}/notes.txt"

    def __init__(self):
        # Clear report directory
        shutil.rmtree(self.PATH, ignore_errors=True)
        os.makedirs(self.PATH, exist_ok=True)
        os.makedirs(self.FULL_DATA_PATH, exist_ok=True)
        os.makedirs(self.MONTHLY_DATA_PATH, exist_ok=True)

    def note_header(self, label: str):
        with open(self.NOTES_FILE, "a") as note_file:
            note_file.write(f"\n{'=' * 10} {label} {'=' * 10}\n\n")

    def note(self, message: str):
        with open(self.NOTES_FILE, "a") as note_file:
            note_file.write(f"{message}\n")

    def write_transactions(
        self,
        transactions: pd.DataFrame,
        path: str,
        columns=["date", "account", "amount", "description"],
    ):
        transactions = transactions.sort_values("date").reset_index(drop=True)

        full_path = f"{self.FULL_DATA_PATH}/{path}.csv"
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Write full transactions
        transactions.to_csv(full_path, columns=columns, index=False)

        # Write monthly transactions
        for month, group in transactions.groupby(
            transactions["date"].dt.to_period("M")
        ):
            monthly_path = (
                f"{self.MONTHLY_DATA_PATH}/{month.strftime('%m%y')}/{path}.csv"
            )
            os.makedirs(os.path.dirname(monthly_path), exist_ok=True)
            group.to_csv(monthly_path, columns=columns, index=False)
