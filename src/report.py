import os
import pandas as pd

class Report:

    def __init__(self, months):
        self.months = months
        self.total_spent = 0
        self.transactions = pd.DataFrame()
        self.transactions_no_transfers = pd.DataFrame()

        # Create report directory if it doesn't exist
        os.makedirs('report', exist_ok=True)

    def write(self):
        # Export all transactions to CSV
        self.transactions.to_csv(f"report/all transactions from {self.months[0].strftime('%m%y')} to {self.months[-1].strftime('%m%y')}.csv", index=False)

        self.transactions_no_transfers.to_csv(f"report/all transactions without transfers from {self.months[0].strftime('%m%y')} to {self.months[-1].strftime('%m%y')}.csv", index=False)

        # Record total spent
        print(f"total spent: {self.total_spent}")
