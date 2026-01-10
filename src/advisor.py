import shutil
from pathlib import Path

from accounts.adapters.bank.apple import Apple
from accounts.adapters.bank.esl import ESL
from accounts.adapters.bank.pnc import PNC
from accounts.adapters.bank.sofi import SoFi
from accounts.adapters.credit.apple import Apple as AppleCredit
from accounts.adapters.credit.chase import Chase
from accounts.adapters.credit.wells_fargo import WellsFargo
from accounts.banker import Banker
from tagger import Tagger


class Advisor:
    SOURCE_TRANSACTIONS_PATH: Path = Path("source transactions")
    PROCESSED_TRANSACTIONS_PATH: Path = Path("transactions")
    TAGGING_PATH: Path = PROCESSED_TRANSACTIONS_PATH / "months"

    def __init__(self) -> None:
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
        self.tagger: Tagger = Tagger(self.banker)

    def advise(self) -> None:
        # Load existing tags before fresh load of source transactions
        self.tagger.load_existing_tags(self.TAGGING_PATH)

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
        self.tagger.apply_tags()

        # Wipe processed transactions for fresh write
        shutil.rmtree(self.PROCESSED_TRANSACTIONS_PATH, ignore_errors=True)

        # Write transactions as a whole and by month
        self.banker.write_transactions(
            all_transactions, self.PROCESSED_TRANSACTIONS_PATH / "all"
        )
        self.banker.write_transactions(
            all_transactions, self.PROCESSED_TRANSACTIONS_PATH / "months", by_month=True
        )

        # Write transactions by month
        for account_name, account in self.banker.accounts.items():
            if account.transactions:
                self.banker.write_transactions(
                    list(account.transactions.values()),
                    self.PROCESSED_TRANSACTIONS_PATH
                    / "accounts"
                    / account_name.lower(),
                )

        # Write transactions by tag
        [
            self.banker.write_transactions(
                self.banker.filter_transactions(
                    lambda t: getattr(t, tag.replace(" ", "_"), False)
                ),
                self.PROCESSED_TRANSACTIONS_PATH / self.tagger.TAGS_PATH / tag,
            )
            for tag in self.tagger.get_all_tags()
        ]
