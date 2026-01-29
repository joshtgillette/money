"""Personal finance advisor that orchestrates transaction loading, tagging, and reporting."""

import re
from pathlib import Path
from typing import Callable, Dict, List, Tuple

import pandas as pd
from tabulate import tabulate

from account_adapters import ACCOUNT_ADAPTERS
from banker import Banker
from transaction import Transaction


class Advisor:
    """Orchestrates loading, tagging, and organizing financial transactions."""

    SOURCE_TRANSACTIONS_PATH: Path = Path("sources")

    def __init__(self) -> None:
        """Initialize the advisor with supported bank accounts and tagging system."""

        self.banker: Banker = Banker(*ACCOUNT_ADAPTERS)

    def advise(self) -> None:
        """Load transactions, apply tags, and generate organized transaction reports.

        Provides an interactive menu for viewing and tagging transactions.
        """

        # Direct the banker to load transactions for the provided accounts
        self.banker.load_account_transactions(self.SOURCE_TRANSACTIONS_PATH)

        COMMANDS: Dict[str, Callable] = {"tag": self.tag}
        focused_transactions: List[Transaction] = []
        while True:
            # Get input
            input_line: str = input("\n# ").strip()
            if not input_line:
                break

            # If the input is a command, run it
            command_func = COMMANDS.get(input_line)
            if command_func:
                command_func(focused_transactions)
                focused_transactions = []  # clear to maintain up-to-date transactions
                continue

            # Attempt to filter on input
            focused_transactions = self.filter(input_line)
            if not focused_transactions:
                print("\nno transactions for query")
                continue

            # Display filtered transactions
            focused_transactions_tabulated: List[Tuple[str, str, str, str, str]] = [
                transaction.for_tabulate() for transaction in focused_transactions
            ]
            focused_total: float = sum(
                transaction.amount for transaction in focused_transactions
            )
            print(
                f"\n{
                    tabulate(
                        focused_transactions_tabulated
                        + [
                            (
                                '',
                                '',
                                f'= {"+" if focused_total > 0 else "-"}${abs(focused_total):,.2f}',
                                '',
                                '',
                            )
                        ],
                        tablefmt='fancy_grid',
                        showindex=False,
                    )
                }"
            )

    def tag(self, transactions: List[Transaction]) -> None:
        """Interactively tag untagged transactions.

        Displays each untagged transaction and prompts the user to enter
        comma-separated tags. Exits when user provides empty input.
        """

        for transaction in reversed(transactions):
            # Skip already tagged transactions
            if transaction.tags:
                continue

            # Display transaction
            print(
                f"\n{
                    tabulate(
                        [transaction.for_tabulate()],
                        tablefmt='simple',
                    )
                }"
            )

            # Tags are reqiured, if empty then exit tagging
            tags_input: str = input("enter tag(s): ").strip()
            if not tags_input:
                return
            tags: List[str] = [tag.strip() for tag in tags_input.split(",")]

            self.banker.write_book(transaction, tags)

        # No more transactions to tag
        print("tagging completed for query")

    def filter(self, filter_line: str) -> List[Transaction]:
        """Display filtered transactions based on user input."""

        predicates: List[Callable[[Transaction], bool]] = []
        if filter_line == "all":
            # no filter
            predicates = [lambda transaction: True]
        elif bool(re.match(r"^(0[1-9]|1[0-2])\d{2}$", filter_line)):
            # filter on a month/year
            month: int = int(filter_line[:2])
            year: int = int(f"20{filter_line[2:]}")
            predicates = [
                lambda t: pd.to_datetime(t.date).month == month
                and pd.to_datetime(t.date).year == year
            ]
        elif filter_line in self.banker.accounts.keys():
            # filter on bank account
            predicates = [
                lambda transaction: (
                    getattr(transaction, "account", "").lower() == filter_line
                )
            ]
        elif filter_line in self.banker.get_all_tags():
            # filter on tag
            predicates = [
                lambda transaction: (filter_line in getattr(transaction, "tags", []))
            ]
        else:
            # filter on description
            predicates = [
                lambda transaction: (
                    filter_line in getattr(transaction, "description").lower()
                )
            ]

        filtered_transactions: List[Transaction] = self.banker.filter_transactions(
            *predicates
        )

        return filtered_transactions
