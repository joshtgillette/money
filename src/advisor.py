"""Personal finance advisor that orchestrates transaction loading, tagging, and reporting."""

from pathlib import Path
from typing import Callable

from adapters import ACCOUNT_ADAPTERS
from banker import Banker


class Advisor:
    """Orchestrates loading, tagging, and organizing financial transactions."""

    SOURCE_TRANSACTIONS_PATH: Path = Path("sources")

    def __init__(self) -> None:
        """Initialize the advisor with supported bank accounts and tagging system."""
        self.banker: Banker = Banker(*ACCOUNT_ADAPTERS)

    def advise(self) -> None:
        """Load transactions, apply tags, and generate organized transaction reports."""
        print()

        # Direct the banker to load transactions for the provided accounts
        self.banker.load_account_transactions(self.SOURCE_TRANSACTIONS_PATH)

        print()
        OPTIONS: list[tuple[str, Callable]] = [("tag transactions", self.tag)]
        while True:
            # Display options
            for num, (label, _) in enumerate(OPTIONS):
                print(f"[{num + 1}] {label}", end="\t\t")
            print()

            # Get input and attempt to exectue option
            user_input: str = input("option #: ")
            if not user_input.strip():
                break

            print()
            try:
                OPTIONS[int(user_input) - 1][1]()
            except ValueError:
                print(f"error: input '{user_input}' is not a number")
            except IndexError:
                print(
                    f"error: option # not from {min(1, len(OPTIONS))} to {len(OPTIONS)}"
                )
            print()
        print()

    def tag(self) -> None:
        for transaction in self.banker:
            # Skip already tagged transactions
            if self.banker.get_existing_tags_for_transaction(transaction):
                continue

            # Display transaction
            print(transaction)

            # Tags are reqiured, if empty then exit tagging
            tags = input("enter tag(s): ").strip()
            if not tags:
                return
            tags = [tag.strip() for tag in tags.split(",")]

            self.banker.write_book(transaction, tags)
            print()
