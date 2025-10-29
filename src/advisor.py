from datetime import datetime
import pandas as pd
from report import Report

class Advisor:

    def __init__(self, accounts: list[str], months: list[datetime]):
        self.accounts = accounts
        self.months = months
        self.report = Report(self.months)

    def start(self):
        self.load_and_normalize_data()
        self.calculate()
        self.report.write()

    def load_and_normalize_data(self):
        for account in self.accounts:
            account.load_transactions(self.months)
            account.normalize()

    def aggregate_transactions(self):
        transactions = []
        for account in self.accounts:
            transactions_with_account = account.transactions.copy()
            transactions_with_account['account'] = account.name
            transactions.append(transactions_with_account)
        transactions = pd.concat(transactions, ignore_index=True)

        return transactions[['date', 'account', 'amount', 'description']].sort_values('date').reset_index(drop=True)

    def calculate(self):
        # Aggregate all account transactions, reorder and sort, calculate total spent
        self.report.transactions = self.aggregate_transactions()
        self.report.total_spent = self.report.transactions['amount'].sum()
