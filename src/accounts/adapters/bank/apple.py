import pandas as pd
from typing import Optional

from accounts.adapters.bank.bank_account import BankAccount
from transaction import Transaction


class Apple(BankAccount):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.raw_transactions: pd.DataFrame = pd.DataFrame()

    def normalize(self) -> None:
        """Convert Apple's CSV format to standard transaction format."""
        if self.raw_transactions.empty:
            return

        self._build_transactions_from_dataframe(
            pd.DataFrame(
                {
                    "date": pd.to_datetime(self.raw_transactions["Transaction Date"]),
                    "amount": pd.to_numeric(self.raw_transactions["Amount"])
                    * (self.raw_transactions["Transaction Type"] == "Credit").map(
                        {True: 1, False: -1}
                    ),
                    "description": self.raw_transactions["Description"],
                }
            )
            .sort_values("date")
            .reset_index(drop=True)
        )

    def is_transaction_income(self, transaction: Transaction) -> bool:
        """Determine if a normalized transaction is income."""
        return (
            super().is_transaction_income(transaction)
            and "ACH Transfer from COMCAST (CC) OF PAYROLL" in transaction.description
        )

    def is_transaction_interest(self, transaction: Transaction) -> bool:
        """Determine if a normalized transaction is interest income."""
        return (
            super().is_transaction_interest(transaction)
            and "Interest Paid" in transaction.description
        )
