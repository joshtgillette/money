"""Personal finance advisor that orchestrates transaction loading, tagging, and reporting."""

from pathlib import Path

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
        # Direct the banker to load transactions for the provided accounts
        self.banker.load_account_transactions(self.SOURCE_TRANSACTIONS_PATH)
