from datetime import datetime
from banking.banker import Banker
from tracking.category import Category
from report import Report

class Advisor:

    def __init__(self, months: list[datetime], banker: Banker, categories: list[Category]):
        self.months = months
        self.banker = banker
        self.categories = categories
        self.report = Report()

    def start(self):
        # Direct the banker to load transactions for the specified months
        self.report.note_header("TRANSFER REMOVAL")
        self.banker.load(self.months)
        self.report.note(self.banker.get_log())
        self.report.note(f"loaded {len(self.banker.accounts)} bank accounts "
                         f"with {len(self.banker.get_transactions())} total transactions, "
                         f"{len(self.banker.get_transactions(is_transfer=False))} without transfers\n")

        # Write transactions data to the report
        self.report.write_transactions(self.banker.get_transactions(), "all transactions")
        self.report.write_transactions(self.banker.get_transactions(is_transfer=False), "transactions no transfers")

        self.report.note_header("CATEGORY TRACKING")
        for category in self.categories:
            category.filter(self.banker)
            self.report.note(f"categorized {len(category.transactions)} transactions as {category.label} "
                             f"totaling ${category.transactions['amount'].sum():,.2f}")
            self.report.write_transactions(category.transactions, f"{category.label} transactions")
