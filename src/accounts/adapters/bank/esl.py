import pandas as pd

from accounts.adapters.bank.bank_account import BankAccount


class ESL(BankAccount):
    def __init__(self, name: str):
        super().__init__(name)
        self.raw_transactions = pd.DataFrame()

    def normalize(self):
        """Convert ESL's CSV format to standard transaction format."""
        if self.raw_transactions.empty:
            return

        self.transactions = (
            pd.DataFrame(
                {
                    "date": pd.to_datetime(self.raw_transactions["Date"]),
                    "amount": pd.to_numeric(
                        self.raw_transactions["Amount Credit"]
                    ).fillna(0)
                    + pd.to_numeric(self.raw_transactions["Amount Debit"]).fillna(0),
                    "description": self.raw_transactions["Description"]
                    + " "
                    + self.raw_transactions["Memo"].fillna("").str.strip(),
                }
            )
            .sort_values("date")
            .reset_index(drop=True)
        )

    def is_transaction_income(self, transaction: pd.Series) -> bool:
        """Determine if a normalized transaction is income."""
        return False

    def is_transaction_interest(self, transaction: pd.Series) -> bool:
        """Determine if a normalized transaction is interest income."""
        return False
