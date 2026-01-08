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
        transactions: Union[pd.DataFrame, Iterable[Transaction]],
        path: str,
        columns: List[str] = ["date", "account", "amount", "description"],
    ) -> None:
        # Convert transaction list to DataFrame if needed
        if not isinstance(transactions, pd.DataFrame):
            # Assume it's an iterable of Transaction objects
            transactions = pd.DataFrame(
                [
                    {
                        "date": txn.date,
                        "amount": txn.amount,
                        "description": txn.description,
                        "account": getattr(txn, "account", None),
                    }
                    for txn in transactions
                ]
            )

        transactions = transactions.sort_values("date").reset_index(drop=True)

        full_path: str = f"{self.DATA_PATH}/{path}.csv"
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Write full transactions
        transactions.to_csv(full_path, columns=columns, index=False)
