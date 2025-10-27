from datetime import datetime
import pandas as pd
from report import Report

class Advisor:

    def __init__(self, accounts: list[str], dates: list[datetime]):
        self.accounts = accounts
        self.dates = dates
        self.report = Report()

    def start(self):
        self.load_and_normalize_data()
        self.calculate()
        self.report.write()

    def load_and_normalize_data(self):
        for account in self.accounts:
            account.load_transactions(self.dates)
            account.normalize()

    def calculate(self):
        # Aggregate all account transactions, add an account identifier, reorder and sort
        all_transactions = []
        for account in self.accounts:
            transactions_with_account = account.transactions.copy()
            transactions_with_account['account'] = account.name
            all_transactions.append(transactions_with_account)
        all_transactions = pd.concat(all_transactions, ignore_index=True)[['date', 'account', 'amount', 'description']].sort_values('date').reset_index(drop=True)

        # Provide transactions to report with reordered columns and sorted transactions by date
        self.report.all_transactions = all_transactions
        self.report.total_spent = self.report.all_transactions['amount'].sum()
