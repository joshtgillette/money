from datetime import datetime

import pandas as pd

from accounts.adapters.account import Account
from accounts.adapters.credit.chase import Chase
from tracking.category import Category


class House(Category):
    def __init__(self, label):
        super().__init__(label)

    def filter_function(self, account: Account, transaction: pd.Series):
        return (
            "PAYMENT TO xxxxxx3890" in transaction.description
            or (
                "VENMO CASHOUT ACH CREDIT" in transaction.description
                and abs(
                    transaction.date
                    - datetime(transaction.date.year, transaction.date.month, 1)
                ).days
                <= 3
                and transaction.amount >= 1000
            )
            or (
                "VENMO CASHOUT ACH CREDIT" in transaction.description
                and transaction.amount == 50
                and transaction.date >= datetime(2024, 9, 1)
            )
            or "CHASE CREDIT CRD EPAY" in transaction.description
            and transaction.date >= datetime(2025, 9, 1)
            or (isinstance(account, Chase) and transaction.date >= datetime(2025, 9, 1))
        )
