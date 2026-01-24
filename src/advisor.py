"""Personal finance advisor that orchestrates transaction loading, tagging, and reporting."""

import shutil
from pathlib import Path
from typing import List

from accounts.adapters.bank.apple import Apple
from accounts.adapters.bank.esl import ESL
from accounts.adapters.bank.pnc import PNC
from accounts.adapters.bank.sofi import SoFi
from accounts.adapters.credit.apple import Apple as AppleCredit
from accounts.adapters.credit.chase import Chase
from accounts.adapters.credit.wells_fargo import WellsFargo
from accounts.banker import Banker
from transaction import Transaction


class Advisor:
    """Orchestrates loading, tagging, and organizing financial transactions."""

    SOURCE_TRANSACTIONS_PATH: Path = Path("sources")
    PROCESSED_TRANSACTIONS_PATH: Path = Path("transactions")

    def __init__(self) -> None:
        """Initialize the advisor with supported bank accounts and tagging system."""
        self.banker: Banker = Banker(
            SoFi("SoFi Checking"),
            SoFi("SoFi Savings"),
            Apple("Apple Savings"),
            PNC("PNC Checking"),
            PNC("PNC Savings"),
            ESL("ESL Checking"),
            ESL("ESL Savings"),
            AppleCredit("Apple Card"),
            WellsFargo("Wells Fargo Credit Card"),
            Chase("Chase Credit Card"),
        )

    def advise(self) -> None:
        """Load transactions, apply tags, and generate organized transaction reports."""
        # Direct the banker to load transactions for the provided accounts
        self.banker.load_account_transactions(self.SOURCE_TRANSACTIONS_PATH)
        all_transactions = self.banker.filter_transactions()

        if len(all_transactions) == 0:
            print("no transactions loaded.")
            return
        else:
            print(
                f"loaded {len(self.banker.accounts)} bank accounts "
                f"with {len(all_transactions)} total transactions"
            )

        # Wipe processed transactions for fresh write
        shutil.rmtree(self.PROCESSED_TRANSACTIONS_PATH, ignore_errors=True)

        # Record transactions as a whole and by month
        self.banker.write_transactions(
            all_transactions, self.PROCESSED_TRANSACTIONS_PATH / "all"
        )
        self.banker.write_transactions(
            all_transactions, self.PROCESSED_TRANSACTIONS_PATH / "months", by_month=True
        )

        # Record transactions by account
        for account_name, account in self.banker.accounts.items():
            if account.transactions:
                self.banker.write_transactions(
                    list(account.transactions.values()),
                    self.PROCESSED_TRANSACTIONS_PATH
                    / "accounts"
                    / account_name.lower(),
                    ["date", "amount", "description"],
                )
