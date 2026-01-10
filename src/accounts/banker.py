"""Manages multiple bank accounts and provides transaction operations."""

import os
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, cast

import pandas as pd

from accounts.adapters.account import Account
from accounts.adapters.credit.credit_card import CreditCard
from transaction import Transaction


class Banker:
    """Manages financial accounts and provides operations for transaction handling."""
    
    def __init__(self, *accounts: Account) -> None:
        """Initialize the banker with a collection of financial accounts."""
        self.accounts: Dict[str, Account] = {
            account.name.lower(): account for account in accounts
        }

    def load_account_transactions(self, source_transactions_path: Path) -> None:
        """Load and normalize transactions from source CSV files for all accounts."""
        for csv_path in self.discover_csvs(source_transactions_path):
            account = self.accounts.get(csv_path.name.replace(".csv", ""), None)
            if not account:
                continue

            account.add_source_transactions(csv_path)

        # Normalize source transactions to a common format and load
        for _, account in self.accounts.items():
            account.transactions = self.load_transactions(
                account.normalize_source_transactions()
            )

    @staticmethod
    def discover_csvs(path: Path) -> List[Path]:
        """Recursively discover all CSV files in the given path."""
        return list(path.rglob("*.csv"))

    @staticmethod
    def load_transactions(transactions_data: pd.DataFrame) -> Dict[int, Transaction]:
        """Parse transaction data from a DataFrame into Transaction objects."""
        transactions: Dict[int, Transaction] = {}
        for row in transactions_data.itertuples():
            index = cast(int, row.Index)
            transactions[index] = Transaction(
                index=index,
                date=cast(datetime, row.date),
                amount=cast(float, row.amount),
                description=cast(str, row.description),
                tags=cast(str, getattr(row, "tags", None)),
            )

        return transactions

    def __iter__(self) -> Iterator[Tuple[Account, Transaction]]:
        for _, account in self.accounts.items():
            for transaction in account.transactions.values():
                yield account, transaction

    def filter_transactions(
        self, *predicates: Callable[[Transaction], bool]
    ) -> List[Transaction]:
        """Filter transactions across all accounts using provided predicate functions."""
        return [
            transaction
            for _, transaction in self
            if not predicates or all(pred(transaction) for pred in predicates)
        ]

    def write_transactions(
        self,
        transactions: List[Transaction],
        path: Path,
        columns: List[str] = ["date", "amount", "description", "tags"],
        by_month: bool = False,
    ) -> None:
        """Write transactions to CSV files, optionally grouped by month."""
        transaction_data = pd.DataFrame(
            [transaction.to_dict() for transaction in transactions]
        )
        if not by_month:
            # Write all transactions
            path = path.with_suffix(".csv")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            transaction_data.to_csv(path, columns=columns, index=False)
            return

        # Write transactions by month
        for month, group in transaction_data.groupby(
            transaction_data["date"].dt.to_period("M")
        ):
            monthly_path = path / f"{pd.Period(month).strftime('%m%y')}.csv"
            os.makedirs(os.path.dirname(monthly_path), exist_ok=True)
            group.to_csv(
                monthly_path,
                index=False,
            )

    def identify_transfers(self) -> None:
        """Identify and mark internal transfers between accounts.
        
        Uses a two-phase approach to build confidence in transfer identification
        based on matching amounts, dates, and description patterns.
        """

        atd_confidence: Dict[
            str, Dict[str, List[List[Any]]]
        ] = {}  # sending account name: {
        #    receiving account name: [
        #        [from account transaction description,
        #         to account transaction description,
        #         confidence value],
        #    ]
        # }
        passes_ran: int = 0
        transfers_in_pass: int = 0
        while True:
            # Phase 1: Build the ATD confidence directory
            for account, transaction in self:
                # Only consider transactions not already marked as transfers
                if transaction.is_transfer:
                    continue

                counter_transactions: List[Tuple[Account, Transaction]] = (
                    self.find_counter_transactions(account, transaction)
                )
                if len(counter_transactions) == 1:
                    counter_account, counter_transaction = counter_transactions[0]

                    # Determine the sending and receiving accounts
                    (
                        sending_account,
                        sending_transaction,
                        receiving_account,
                        receiving_transaction,
                    ) = (
                        (account, transaction, counter_account, counter_transaction)
                        if transaction.amount < 0
                        else (
                            counter_account,
                            counter_transaction,
                            account,
                            transaction,
                        )
                    )

                    # Update the description pair in corresponding sender/receiver entry with confidence value
                    receiving_accounts: Dict[str, List[List[Any]]] = atd_confidence.get(
                        sending_account.name, {}
                    )
                    description_pairs: List[List[Any]] = receiving_accounts.get(
                        receiving_account.name, []
                    )
                    existing_description_pair: List[List[Any]] = [
                        dp
                        for dp in description_pairs
                        if self.equate_transaction_descriptions(
                            dp[0], sending_transaction.description
                        )
                        and self.equate_transaction_descriptions(
                            dp[1], receiving_transaction.description
                        )
                    ]

                    if (
                        existing_description_pair
                        and existing_description_pair[0][3]
                        != f"{sending_account.name}.{sending_transaction.Index}"
                    ):
                        existing_description_pair[0][2] += 1
                    elif not existing_description_pair:
                        description_pairs.append(
                            [
                                sending_transaction.description,
                                receiving_transaction.description,
                                1,
                                f"{sending_account.name}.{sending_transaction.Index}",
                            ]
                        )
                    receiving_accounts.update(
                        {receiving_account.name: description_pairs}
                    )
                    atd_confidence.update({sending_account.name: receiving_accounts})

            # Phase 2: Identify transfers using the ATD confidence directory
            for account, transaction in self:
                # Only consider transactions not already marked as transfers
                if transaction.is_transfer:
                    continue

                counter_transactions = self.find_counter_transactions(
                    account, transaction
                )
                for counter_account, counter_transaction in counter_transactions:
                    if self.is_transfer(account, transaction.Index) or self.is_transfer(
                        counter_account, counter_transaction.Index
                    ):
                        continue

                    (
                        sending_account,
                        sending_transaction,
                        receiving_account,
                        receiving_transaction,
                    ) = (
                        (account, transaction, counter_account, counter_transaction)
                        if transaction.amount < 0
                        else (
                            counter_account,
                            counter_transaction,
                            account,
                            transaction,
                        )
                    )

                    # Get the description pair with the highest/high confidence value indicating a transfer
                    # between the sending and receiving accounts
                    description_pairs = atd_confidence.get(
                        sending_account.name, {}
                    ).get(receiving_account.name, [])
                    sending_description: Optional[str]
                    receiving_description: Optional[str]
                    confidence: int
                    sending_description, receiving_description, confidence, _ = (
                        max(description_pairs, key=lambda dp: dp[2])
                        if description_pairs
                        else (None, None, 0, None)
                    )

                    # If the confidence is highest, mark the transactions as a transfer!
                    if (
                        confidence > 0
                        and self.equate_transaction_descriptions(
                            sending_description, sending_transaction.description
                        )
                        and self.equate_transaction_descriptions(
                            receiving_description, receiving_transaction.description
                        )
                    ):
                        print(
                            f"transaction of {self.format_amount(sending_transaction.amount)} from "
                            f"{sending_account.name} to {receiving_account.name} ({sending_transaction.description}) "
                            "is transfer"
                        )
                        print(
                            f"transaction of {self.format_amount(receiving_transaction.amount)} from "
                            f"{receiving_account.name} to {sending_account.name} ({receiving_transaction.description}) "
                            "is transfer"
                        )
                        self.set_transfer(account, transaction.Index)
                        self.set_transfer(counter_account, counter_transaction.Index)
                        transfers_in_pass += 1

            if not transfers_in_pass:
                break
            passes_ran += 1
            print(f"{transfers_in_pass} transfers identified in pass {passes_ran}\n")
            transfers_in_pass = 0

    def find_counter_transactions(
        self, account: Account, transaction: Transaction
    ) -> List[Tuple[Account, Transaction]]:
        """Find potential matching transactions that could represent transfers."""
        return [
            (a, t)
            for a, t in self
            if not t.is_transfer
            and a != account
            and t.amount == -transaction.amount
            and abs((t.date - transaction.date).days) <= 7
            and (not isinstance(account, CreditCard) or not isinstance(a, CreditCard))
            and (not isinstance(account, CreditCard) or transaction.amount > 0)
            and (not isinstance(a, CreditCard) or t.amount > 0)
        ]

    def equate_transaction_descriptions(
        self, d1: Optional[str], d2: str, threshold: float = 0.90
    ) -> bool:
        """Compare two transaction descriptions for similarity above a threshold."""
        if d1 is None:
            return False
        return SequenceMatcher(None, d1, d2).ratio() >= threshold

    def identify_returns(self) -> None:
        """Identify and mark product returns or refunds within accounts."""
        for account, transaction in self:
            if transaction.is_transfer or not account.is_return_candidate(transaction):
                continue

            original_transaction: Optional[Transaction] = account.find_counter_return(
                transaction
            )
            if original_transaction is None:
                continue

            print(
                f"transaction of {self.format_amount(transaction.amount)} from "
                f"{account.name} ({transaction.description}) "
                "is return"
            )
            print(
                f"transaction of {self.format_amount(original_transaction.amount)} from "
                f"{account.name} ({original_transaction.description}) "
                "is returned"
            )
            self.set_transfer(account, transaction.Index)
            self.set_transfer(account, original_transaction.Index)

    def set_transfer(
        self, account: Account, transaction_index: int, value: bool = True
    ) -> None:
        """Mark a transaction as a transfer or not."""
        if transaction_index in account.transactions:
            account.transactions[transaction_index].is_transfer = value

    def is_transfer(self, account: Account, transaction_index: int) -> bool:
        """Check if a transaction is marked as a transfer."""
        if transaction_index in account.transactions:
            return account.transactions[transaction_index].is_transfer
        return False

    def format_amount(self, amount: float) -> str:
        """Format a transaction amount as a currency string with sign."""
        return f"-${abs(amount):.2f}" if amount < 0 else f"${abs(amount):.2f}"

    def get_log(self) -> str:
        """Retrieve and clear the accumulated log messages."""
        log_string: str = "\n".join(self.log)
        self.log = []
        return log_string
        self.log = []
        return log_string
