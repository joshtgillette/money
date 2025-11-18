import os
import shutil
import pandas as pd

class Report:

    PATH = "report"
    DATA_PATH = f"{PATH}/data"
    NOTES_FILE = f"{PATH}/notes.txt"

    def __init__(self):
        # Clear report directory
        shutil.rmtree(self.PATH, ignore_errors=True)
        os.makedirs(self.PATH, exist_ok=True)
        os.makedirs(self.DATA_PATH, exist_ok=True)

    def note_header(self, label: str):
        with open(self.NOTES_FILE, "a") as note_file:
            note_file.write(f"\n{'='*10} {label} {'='*10}\n\n")

    def note(self, message: str):
        with open(self.NOTES_FILE, "a") as note_file:
            note_file.write(f"{message}\n")

    def write_transactions(self, transactions: pd.DataFrame, filename: str):
        transactions.sort_values('date').to_csv(
            f"{self.DATA_PATH}/{filename}.csv",
            columns=['date', 'account', 'amount', 'description'],
            index=False
        )
