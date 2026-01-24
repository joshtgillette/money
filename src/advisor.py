"""Personal finance advisor that orchestrates transaction loading, tagging, and reporting."""

import shutil
from pathlib import Path
from typing import cast

import pandas as pd

from account import Account
from banker import Banker


class Advisor:
    """Orchestrates loading, tagging, and organizing financial transactions."""

    SOURCE_TRANSACTIONS_PATH: Path = Path("sources")
    PROCESSED_TRANSACTIONS_PATH: Path = Path("transactions")

    def __init__(self) -> None:
        """Initialize the advisor with supported bank accounts and tagging system."""
        self.banker: Banker = Banker(
            Account(
                "SoFi Checking",
                date_normalizer=lambda df: pd.to_datetime(df["Date"]),
                amount_normalizer=lambda df: cast(
                    pd.Series, pd.to_numeric(df["Amount"])
                ),
                description_normalizer=lambda df: pd.Series(df["Description"]),
            ),
            Account(
                "SoFi Savings",
                date_normalizer=lambda df: pd.to_datetime(df["Date"]),
                amount_normalizer=lambda df: cast(
                    pd.Series, pd.to_numeric(df["Amount"])
                ),
                description_normalizer=lambda df: pd.Series(df["Description"]),
            ),
            Account(
                "Apple Savings",
                date_normalizer=lambda df: pd.to_datetime(df["Transaction Date"]),
                amount_normalizer=lambda df: pd.to_numeric(df["Amount"])
                * df["Transaction Type"]
                .eq("Credit")
                .map(lambda b: 1 if bool(b) else -1),
                description_normalizer=lambda df: pd.Series(df["Description"]),
            ),
            Account(
                "PNC Checking",
                date_normalizer=lambda df: pd.to_datetime(df["Transaction Date"]),
                amount_normalizer=lambda df: cast(
                    pd.Series,
                    pd.to_numeric(
                        df["Amount"].str.replace(r"[\+\$\s]", "", regex=True)
                    ),
                ),
                description_normalizer=lambda df: pd.Series(
                    df["Transaction Description"]
                ),
            ),
            Account(
                "PNC Savings",
                date_normalizer=lambda df: pd.to_datetime(df["Transaction Date"]),
                amount_normalizer=lambda df: cast(
                    pd.Series,
                    pd.to_numeric(
                        df["Amount"].str.replace(r"[\+\$\s]", "", regex=True)
                    ),
                ),
                description_normalizer=lambda df: pd.Series(
                    df["Transaction Description"]
                ),
            ),
            Account(
                "ESL Checking",
                date_normalizer=lambda df: pd.to_datetime(df["Date"]),
                amount_normalizer=lambda df: cast(
                    pd.Series,
                    pd.Series(pd.to_numeric(df["Amount Credit"].fillna(0)))
                    + pd.Series(pd.to_numeric(df["Amount Debit"].fillna(0))),
                ),
                description_normalizer=lambda df: pd.Series(
                    df["Description"]
                    .astype("string")
                    .fillna("")
                    .str.cat(
                        df["Memo"].astype("string").fillna("").str.strip(), sep=" "
                    )
                ),
            ),
            Account(
                "ESL Savings",
                date_normalizer=lambda df: pd.to_datetime(df["Date"]),
                amount_normalizer=lambda df: cast(
                    pd.Series,
                    pd.Series(pd.to_numeric(df["Amount Credit"])).fillna(0)
                    + pd.Series(pd.to_numeric(df["Amount Debit"])).fillna(0),
                ),
                description_normalizer=lambda df: pd.Series(
                    df["Description"]
                    .astype("string")
                    .fillna("")
                    .str.cat(
                        df["Memo"].astype("string").fillna("").str.strip(), sep=" "
                    )
                ),
            ),
            Account(
                "Apple Card",
                date_normalizer=lambda df: pd.to_datetime(df["Transaction Date"]),
                amount_normalizer=lambda df: pd.Series(
                    pd.to_numeric(df["Amount (USD)"])
                ).mul(-1),
                description_normalizer=lambda df: pd.Series(df["Description"]),
            ),
            Account(
                "Wells Fargo Credit Card",
                date_normalizer=lambda df: pd.to_datetime(df.iloc[:, 0]),
                amount_normalizer=lambda df: cast(
                    pd.Series, pd.to_numeric(df.iloc[:, 1])
                ),
                description_normalizer=lambda df: pd.Series(df.iloc[:, 4]),
                header_val=None,
            ),
            Account(
                "Chase Credit Card",
                date_normalizer=lambda df: pd.to_datetime(df["Transaction Date"]),
                amount_normalizer=lambda df: cast(
                    pd.Series, pd.to_numeric(df["Amount"])
                ),
                description_normalizer=lambda df: pd.Series(df["Description"]),
            ),
        )

    def advise(self) -> None:
        """Load transactions, apply tags, and generate organized transaction reports."""
        # Direct the banker to load transactions for the provided accounts
        self.banker.load_account_transactions(self.SOURCE_TRANSACTIONS_PATH)
        all_transactions = self.banker.filter_transactions()

        if len(all_transactions) == 0:
            print("no transactions loaded.")
            return
        else:
            print(
                f"loaded {len(self.banker.accounts)} bank accounts "
                f"with {len(all_transactions)} total transactions"
            )

        # Wipe processed transactions for fresh write
        shutil.rmtree(self.PROCESSED_TRANSACTIONS_PATH, ignore_errors=True)

        # Record transactions as a whole and by month
        self.banker.write_transactions(
            all_transactions, self.PROCESSED_TRANSACTIONS_PATH / "all"
        )
        self.banker.write_transactions(
            all_transactions, self.PROCESSED_TRANSACTIONS_PATH / "months", by_month=True
        )

        # Record transactions by account
        for account_name, account in self.banker.accounts.items():
            if account.transactions:
                self.banker.write_transactions(
                    list(account.transactions.values()),
                    self.PROCESSED_TRANSACTIONS_PATH
                    / "accounts"
                    / account_name.lower(),
                    ["date", "amount", "description"],
                )
