import pandas as pd

from accounts.banker import Banker
from report import Report


class Advisor:
    def __init__(self, banker: Banker) -> None:
        self.banker: Banker = banker
        self.report: Report = Report()

    def start(self) -> None:
        # Direct the banker to load transactions for the specified date range
        self.banker.load()
        if sum(len(account.transactions) for account in self.banker.accounts) == 0:
            self.report.note("No transactions loaded.")
            return

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
