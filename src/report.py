import os
import shutil
from typing import Iterable, List, Union

import pandas as pd

from transaction import Transaction


class Report:
    PATH: str = "report"
    DATA_PATH: str = f"{PATH}/transactions"
    NOTES_FILE: str = f"{PATH}/notes.txt"

    def __init__(self) -> None:
        # Clear report directory
        shutil.rmtree(self.PATH, ignore_errors=True)
        os.makedirs(self.PATH, exist_ok=True)
        os.makedirs(self.DATA_PATH, exist_ok=True)

    def note_header(self, label: str) -> None:
        with open(self.NOTES_FILE, "a") as note_file:
            note_file.write(f"\n{'=' * 10} {label} {'=' * 10}\n\n")

    def note(self, message: str) -> None:
        with open(self.NOTES_FILE, "a") as note_file:
            note_file.write(f"{message}\n")

    def write_transactions(
        self,
        transactions: List[Transaction],
        path: str,
        columns: List[str] = ["date", "amount", "description", "tags"],
    ) -> None:
        transaction_data = pd.DataFrame(
            [transaction.to_dict() for transaction in transactions]
        )

        full_path: str = f"{self.DATA_PATH}/{path}.csv"
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Write full transactions
        transaction_data.to_csv(full_path, columns=columns, index=False)
