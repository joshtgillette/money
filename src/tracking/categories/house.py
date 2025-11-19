from tracking.category import Category
import pandas as pd
from datetime import datetime

class House(Category):

    def __init__(self, label):
        super().__init__(label)

    def filter_function(self, _, transaction: pd.Series):
        return "PAYMENT TO xxxxxx3890" in transaction.description or \
                ("VENMO CASHOUT ACH CREDIT" in transaction.description and
                 abs(transaction.date - datetime(transaction.date.year, transaction.date.month, 1)).days <= 3 and
                 transaction.amount >= 1000) or \
                ("VENMO CASHOUT ACH CREDIT" in transaction.description and
                 transaction.amount == 50 and
                 transaction.date >= datetime(2024, 9, 1)) or \
                 "CHASE CREDIT CRD EPAY" in transaction.description and transaction.date >= datetime(2025, 9, 1)
