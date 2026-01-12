from difflib import SequenceMatcher
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from accounts.adapters.account import Account
from accounts.adapters.credit.credit_card import CreditCard
from transaction import Transaction

if TYPE_CHECKING:
    from accounts.banker import Banker


class TransferTagger:
    """Identifies and tags internal transfers between bank accounts."""

    def __init__(self, banker: "Banker") -> None:
        """Initialize the transfer tagger with a banker instance.
        
        Args:
            banker: The banker instance containing all accounts and transactions
        """
        self.banker = banker

    def identify_transfers(self) -> None:
        """Identify internal transfers between bank accounts.
        
        Identification is dependent on relating a candidate transfer's sending and 
        receiving account to the transfer and counter-transfer's descriptions along 
        with a confidence value indicating the frequency of transfers with the same 
        descriptions between the accounts.

        Process:
            Phase 1: Build the account-transfer-description (ATD) confidence directory 
                     that relates a potential transfer's sending and receiving account 
                     by the transactions' descriptions.
                1. For each transaction, find a sole counter transaction indicating a transfer
                2. Link the sending and receiving accounts by the transfer's description 
                   pair with a confidence value
                   
            Phase 2: Identify transactions with accounts and descriptions in the ATD 
                     confidence mapping that have the highest confidence value.

        These phases repeat until transfers are no longer identified.
        """

        atd_confidence: Dict[str, Dict[str, List[List[Any]]]] = {}  # sending account name: {
        #    receiving account name: [
        #        [from account transaction description,
        #         to account transaction description,
        #         confidence value,
        #         tracking key],
        #    ]
        # }
        passes_ran: int = 0
        transfers_in_pass: int = 0
        while True:
            # Phase 1: Build the ATD confidence directory
            for account, transaction in self.banker:
                # Only consider transactions not already marked as transfers
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
                        != f"{sending_account.name}.{sending_transaction.index}"
                    ):
                        existing_description_pair[0][2] += 1
                    elif not existing_description_pair:
                        description_pairs.append(
                            [
                                sending_transaction.description,
                                receiving_transaction.description,
                                1,
                                f"{sending_account.name}.{sending_transaction.index}",
                            ]
                        )
                    receiving_accounts.update(
                        {receiving_account.name: description_pairs}
                    )
                    atd_confidence.update({sending_account.name: receiving_accounts})

            # Phase 2: Identify transfers using the ATD confidence directory
            for account, transaction in self.banker:
                # Only consider transactions not already marked as transfers
                if transaction.TRANSFER:
                    continue

                counter_transactions = self.find_counter_transactions(
                    account, transaction
                )
                for counter_account, counter_transaction in counter_transactions:
                    if self.transfer(account, transaction.index) or self.transfer(
                        counter_account, counter_transaction.index
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
                    if description_pairs:
                        max_pair: List[Any] = max(description_pairs, key=lambda dp: dp[2])
                        sending_description = max_pair[0]  # Already a str
                        receiving_description = max_pair[1]  # Already a str
                        confidence = max_pair[2]  # Already an int
                    else:
                        sending_description = None
                        receiving_description = None
                        confidence = 0

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
                        # print(
                        #     f"transaction of {self.format_amount(sending_transaction.amount)} from "
                        #     f"{sending_account.name} to {receiving_account.name} ({sending_transaction.description}) "
                        #     "is transfer"
                        # )
                        # print(
                        #     f"transaction of {self.format_amount(receiving_transaction.amount)} from "
                        #     f"{receiving_account.name} to {sending_account.name} ({receiving_transaction.description}) "
                        #     "is transfer"
                        # )
                        self.set_transfer(account, transaction.index)
                        self.set_transfer(counter_account, counter_transaction.index)
                        transfers_in_pass += 1

            if not transfers_in_pass:
                break
            passes_ran += 1
            # print(f"{transfers_in_pass} transfers identified in pass {passes_ran}\n")
            transfers_in_pass = 0

    def find_counter_transactions(
        self, account: Account, transaction: Transaction
    ) -> List[Tuple[Account, Transaction]]:
        """Find potential matching transactions that could represent transfers.
        
        Args:
            account: The account containing the transaction to match
            transaction: The transaction to find counter-transactions for
            
        Returns:
            List of tuples containing (account, transaction) pairs that could be transfers
        """
        return [
            (a, t)
            for a, t in self.banker
            if True
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
        """Compare two transaction descriptions for similarity above a threshold.
        
        Args:
            d1: First description to compare (can be None)
            d2: Second description to compare
            threshold: Similarity threshold (default: 0.90)
            
        Returns:
            True if descriptions are similar above the threshold, False otherwise
        """
        if d1 is None:
            return False
        return SequenceMatcher(None, d1, d2).ratio() >= threshold

    def identify_returns(self) -> None:
        """Identify and mark product returns or refunds within accounts."""
        for account, transaction in self.banker:
            if transaction.TRANSFER or not account.is_return_candidate(transaction):
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
            self.set_transfer(account, transaction.index)
            self.set_transfer(account, original_transaction.index)

    def set_transfer(
        self, account: Account, transaction_index: int, value: bool = True
    ) -> None:
        """Mark a transaction as a transfer or not.
        
        Args:
            account: The account containing the transaction
            transaction_index: Index of the transaction to mark
            value: Whether to mark as transfer (default: True)
        """
        if transaction_index in account.transactions:
            account.transactions[transaction_index].TRANSFER = value

    def transfer(self, account: Account, transaction_index: int) -> bool:
        """Check if a transaction is marked as a transfer.
        
        Args:
            account: The account containing the transaction
            transaction_index: Index of the transaction to check
            
        Returns:
            True if the transaction is marked as a transfer, False otherwise
        """
        if transaction_index in account.transactions:
            return account.transactions[transaction_index].transfer
        return False

    def format_amount(self, amount: float) -> str:
        """Format a transaction amount as a currency string with sign.
        
        Args:
            amount: The transaction amount to format
            
        Returns:
            Formatted currency string with sign (e.g., "-$50.00" or "$100.00")
        """
        return f"-${abs(amount):.2f}" if amount < 0 else f"${abs(amount):.2f}"
