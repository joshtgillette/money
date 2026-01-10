import os
import shutil
from pathlib import Path
from typing import List

import pandas as pd

from transaction import Transaction


class Report:
    PATH: Path = Path("report")
    DATA_PATH: Path = PATH / "transactions"
    NOTES_PATH: Path = PATH / "notes.txt"

    def __init__(self) -> None:
        # Clear report directory
        shutil.rmtree(self.PATH, ignore_errors=True)
        os.makedirs(self.PATH, exist_ok=True)
        os.makedirs(self.DATA_PATH, exist_ok=True)

    def note_header(self, label: str) -> None:
        with open(self.NOTES_PATH, "a") as note_file:
            note_file.write(f"\n{'=' * 10} {label} {'=' * 10}\n\n")

    def note(self, message: str) -> None:
        with open(self.NOTES_PATH, "a") as note_file:
            note_file.write(f"{message}\n")

    def write_transactions(
        self,
        transactions: List[Transaction],
        path: str,
        columns: List[str] = ["date", "amount", "description", "tags"],
        by_month: bool = False,
    ) -> None:
        transaction_data = pd.DataFrame(
            [transaction.to_dict() for transaction in transactions]
        )
        full_path: Path = self.DATA_PATH / path

        if not by_month:
            # Write all transactions
            full_path = full_path.with_suffix(".csv")
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            transaction_data.to_csv(full_path, columns=columns, index=False)
            return

        # Write transactions by month
        for month, group in transaction_data.groupby(
            transaction_data["date"].dt.to_period("M")
        ):
            monthly_path = full_path / f"{pd.Period(month).strftime('%m%y')}.csv"
            os.makedirs(os.path.dirname(monthly_path), exist_ok=True)
            group.to_csv(
                monthly_path,
                columns=columns,
                index=False,
            )
