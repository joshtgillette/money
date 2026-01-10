import pandas as pd

from accounts.banker import Banker
from report import Report
from tagger import Tagger


class Advisor:
    def __init__(self, banker: Banker) -> None:
        self.banker: Banker = banker
        self.tagger: Tagger = Tagger()
        self.report: Report = Report()

    def start(self) -> None:
        # Load existing tags from transactions directory before loading new data
        self.tagger.load_existing_tags(self.banker)

        # Direct the banker to load transactions for the provided accounts
        self.banker.load_account_transactions()

        if (
            sum(
                len(account.transactions) for _, account in self.banker.accounts.items()
            )
            == 0
        ):
            self.report.note("No transactions loaded.")
            return

        # Apply tags to loaded transactions
        self.tagger.apply_tags(self.banker)

        # self.report.note_header("TRANSFER REMOVAL")
        # self.banker.identify_returns()
        # self.banker.identify_transfers()
        # self.report.note(self.banker.get_log())

        # Write collective and by month transactions data to the report
        transactions = self.banker.filter_transactions()
        self.report.write_transactions(transactions, "all")
        self.report.write_transactions(transactions, "months", by_month=True)

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
        for account_name, account in self.banker.accounts.items():
            if account.transactions:
                self.report.write_transactions(
                    account.transactions.values(),
                    f"accounts/{account_name.lower()}",
                    columns=["date", "amount", "description"],
                )

        # Recreate transactions directory with tags
        self.tagger.write_transactions_with_tags(self.banker)

        # Write tagged transactions to report
        [
            self.report.write_transactions(
                self.banker.filter_transactions(
                    lambda t: getattr(t, tag.replace(" ", "_"), False)
                ),
                f"tags/{tag}",
            )
            for tag in self.tagger.get_all_tags()
        ]
