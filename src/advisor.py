"""Personal finance advisor that orchestrates transaction loading, tagging, and reporting."""

import re
from pathlib import Path
from typing import Callable, List

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

        OPTIONS: list[tuple[str, Callable[[], None]]] = [
            ("view", self.view),
            ("tag", self.tag),
        ]
        while True:
            # Display options
            print()
            for num, (label, _) in enumerate(OPTIONS):
                print(f"[{num + 1}] {label}", end="\t\t")
            print()

            # Get input and attempt to exectue option
            user_option: str = input("option #: ")
            if not user_option.strip():
                break

            try:
                OPTIONS[int(user_option) - 1][1]()
            except ValueError:
                print(f"error: input '{user_option}' is not a number")
            except IndexError:
                print(
                    f"error: option # not from {min(1, len(OPTIONS))} to {len(OPTIONS)}"
                )
        print()

    def tag(self) -> None:
        """Interactively tag untagged transactions.

        Displays each untagged transaction and prompts the user to enter
        comma-separated tags. Exits when user provides empty input.
        """

        for transaction in self.banker.filter_transactions(reversed=True):
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

    def view(self) -> None:
        """Display filtered transactions based on user input."""

        predicates: List[Callable[[Transaction], bool]] = []
        filter_input: str = input("\nenter filter: ").lower()
        if filter_input == "all":
            # no filter
            predicates = [lambda transaction: True]
        elif bool(re.match(r"^(0[1-9]|1[0-2])\d{2}$", filter_input)):
            # filter on a month/year
            month: int = int(filter_input[:2])
            year: int = int(f"20{filter_input[2:]}")
            predicates = [
                lambda t: pd.to_datetime(t.date).month == month
                and pd.to_datetime(t.date).year == year
            ]
        elif filter_input in self.banker.accounts.keys():
            # filter on bank account
            predicates = [
                lambda transaction: (
                    getattr(transaction, "account", "").lower() == filter_input
                )
            ]
        elif filter_input in self.banker.get_all_tags():
            # filter on tag
            predicates = [
                lambda transaction: (filter_input in getattr(transaction, "tags", []))
            ]
        else:
            # filter on description
            predicates = [
                lambda transaction: (
                    filter_input in getattr(transaction, "description").lower()
                )
            ]

        filtered_transactions: List[Transaction] = self.banker.filter_transactions(
            *predicates
        )
        if not filtered_transactions:
            print("\nno transactions for query")
            return

        print(
            f"\n{
                tabulate(
                    [
                        transaction.for_tabulate()
                        for transaction in filtered_transactions
                    ],
                    tablefmt='fancy_grid',
                    showindex=False,
                )
            }"
        )
