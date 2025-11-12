from datetime import datetime
from banking.banker import Banker
from report import Report
from tracking.tracker import Tracker

class Advisor:

    def __init__(self, months: list[datetime], banker: Banker, tracker: Tracker):
        self.months = months
        self.banker = banker
        self.tracker = tracker
        self.report = Report()

    def start(self):
        # Direct the banker to load transactions for the specified months
        self.report.note_header("TRANSFER REMOVAL")
        self.banker.load(self.months)
        self.report.note(self.banker.get_log())
        self.report.note(f"loaded {len(self.banker.accounts)} bank accounts "
                         f"with {len(self.banker.transactions)} total transactions, {len(self.banker.transactions_no_transfers)} without transfers\n")

        # Write transactions data to the report
        self.report.write_transactions(self.banker.transactions, "all transactions")
        self.report.write_transactions(self.banker.transactions_no_transfers, "transactions no transfers")

        self.report.note_header("CATEGORY TRACKING")
        self.tracker.track(self.banker.transactions_no_transfers)
        for category in self.tracker.categories:
            self.report.note(f"categorized {len(category.transactions)} transactions as {category.label} "
                             f"totaling ${category.transactions['amount'].sum():,.2f}")
            self.report.write_transactions(category.transactions, f"{category.label} transactions")
