"""Personal finance advisor that orchestrates transaction loading, tagging, and reporting."""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict

from accounts.adapters.account import Account
from accounts.adapters.bank.apple import Apple
from accounts.adapters.bank.esl import ESL
from accounts.adapters.bank.pnc import PNC
from accounts.adapters.bank.sofi import SoFi
from accounts.adapters.credit.apple import Apple as AppleCredit
from accounts.adapters.credit.chase import Chase
from accounts.adapters.credit.wells_fargo import WellsFargo
from accounts.banker import Banker
from tagging.tag_manager import TagManager
from tagging.transfer_tagger import TransferTagger
from transaction import Transaction


class Advisor:
    """Orchestrates loading, tagging, and organizing financial transactions."""

    SOURCE_TRANSACTIONS_PATH: Path = Path("sources")
    PROCESSED_TRANSACTIONS_PATH: Path = Path("transactions")
    TAGGING_PATH: Path = PROCESSED_TRANSACTIONS_PATH / "months"
    TAGGERS: Dict[str, Callable[[Account, Transaction], bool] | TransferTagger] = {
        "INCOME": lambda account, transaction: transaction.amount > 0
        and account.is_transaction_income(transaction),
        "INTEREST": lambda account, transaction: account.is_transaction_interest(
            transaction
        ),
        "RENO": lambda account, transaction: isinstance(account, Chase)
        and transaction.date > datetime(2025, 9, 1),
        "SUBSCRIPTIONS": lambda account, transaction: "APPLE.COM/BILL"
        in transaction.description
        or "HBOMAX.COM" in transaction.description
        or "GITHUB.COM" in transaction.description,
    }

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
        self.TAGGERS["TRANSFER"] = TransferTagger(self.banker)
        self.tag_manager: TagManager = TagManager(self.banker, self.TAGGERS)

    def advise(self) -> None:
        """Load transactions, apply tags, and generate organized transaction reports."""
        existing_tags = self.tag_manager.get_existing_tags(self.TAGGING_PATH)

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

        # Apply tags to loaded transactions
        self.tag_manager.apply_tags(existing_tags)
        self.tag_manager.auto_tag()

        # Wipe processed transactions for fresh write
        shutil.rmtree(self.PROCESSED_TRANSACTIONS_PATH, ignore_errors=True)

        # Write transactions as a whole and by month
        self.banker.write_transactions(
            all_transactions, self.PROCESSED_TRANSACTIONS_PATH / "all"
        )
        self.banker.write_transactions(
            all_transactions, self.PROCESSED_TRANSACTIONS_PATH / "months", by_month=True
        )

        # Write transactions by account
        for account_name, account in self.banker.accounts.items():
            if account.transactions:
                self.banker.write_transactions(
                    list(account.transactions.values()),
                    self.PROCESSED_TRANSACTIONS_PATH
                    / "accounts"
                    / account_name.lower(),
                    ["date", "amount", "description", "tags"],
                )

        # Write transactions by tag
        [
            self.banker.write_transactions(
                self.banker.filter_transactions(
                    lambda transaction: getattr(transaction, tag, False)
                ),
                self.PROCESSED_TRANSACTIONS_PATH
                / self.tag_manager.TAGGED_PATH
                / tag.lower(),
            )
            for tag in self.tag_manager.get_all_tags()
        ]

        # Write transactions with no tags
        self.banker.write_transactions(
            self.banker.filter_transactions(
                lambda transaction: not transaction.get_tags()
            ),
            self.PROCESSED_TRANSACTIONS_PATH
            / self.tag_manager.TAGGED_PATH
            / "untagged",
        )
