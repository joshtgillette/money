import os
import pandas as pd

class Report:

    def __init__(self):
        # Create report directory if it doesn't exist
        os.makedirs('report', exist_ok=True)

        # Info in report
        self.total_spent = 0
        self.all_transactions = pd.DataFrame()

    def write(self):
        # Export all transactions to CSV
        self.all_transactions.to_csv('report/all_transactions.csv', index=False)

        # Record total spent
        print(f"total spent: {self.total_spent}")
