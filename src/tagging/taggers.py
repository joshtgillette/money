"""Tagging rules for categorizing transactions."""

from datetime import datetime
from typing import Callable, Dict

from accounts.adapters.account import Account
from accounts.adapters.credit.chase import Chase
from tagging.transfer_tagger import TransferTagger
from transaction import Transaction


def init_taggers(
    banker,
) -> Dict[str, Callable[[Account, Transaction], bool] | TransferTagger]:
    """Create tagging rules for transaction categorization.

    Args:
        banker: Banker instance needed for TransferTagger

    Returns:
        Dictionary mapping tag names to their evaluation functions
    """
    return {
        "PAYCHECK": lambda account, transaction: transaction.amount > 0
        and account.is_transaction_paycheck(transaction),
        "INTEREST": lambda account, transaction: account.is_transaction_interest(
            transaction
        ),
        "HOUSE": lambda account, transaction: isinstance(account, Chase)
        and transaction.date > datetime(2025, 9, 1),
        "SUBSCRIPTIONS": lambda account, transaction: "APPLE.COM/BILL"
        in transaction.description
        or "HBOMAX.COM" in transaction.description
        or "GITHUB.COM" in transaction.description,
        "INVESTMENTS": lambda account, transaction: transaction.description
        in ["FID BKG SVC LLC", "FIDELITY INVESTMENTS WITH UMB BANK"],
        "TRANSFER": TransferTagger(banker),
    }
