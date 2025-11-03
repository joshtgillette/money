from datetime import datetime
from banking.banker import Banker
from report import Report

class Advisor:

    def __init__(self, months: list[datetime], banker: Banker):
        self.months = months
        self.banker = banker
        self.report = Report()

    def start(self):
        # Direct the banker to load transactions for the specified months
        self.banker.load(self.months)
        self.report.note(self.banker.get_log())
        self.report.note(f"loaded {len(self.banker.accounts)} bank accounts "
                         f"with {len(self.banker.transactions)} total transactions, {len(self.banker.transactions_no_transfers)} without transfers\n")

        # Write transactions data to the report
        self.report.write_transactions(self.banker.transactions, "all transactions")
        self.report.write_transactions(self.banker.transactions_no_transfers, "transactions no transfers")
        self.calculate()

    def calculate(self):
        # Aggregate all account transactions, reorder and sort, calculate total spent
        self.report.note("performing calculations..")
