import os
from difflib import SequenceMatcher

import pandas as pd

from accounts.adapters.credit.credit_card import CreditCard


class Banker:
    TRANSACTIONS_PATH = "../transactions"

    def __init__(self, *accounts):
        self.accounts = list(accounts)
        self.transactions = pd.DataFrame()
        self.log = []

    def load(self):
        name_account_mapping = {
            account.name.lower(): account for account in self.accounts
        }
        for root, _, files in os.walk(self.TRANSACTIONS_PATH):
            for file in files:
                if not file.endswith(".csv"):
                    continue

                key = file[:-4].lower()
                if key in name_account_mapping:
                    name_account_mapping[key].load_transactions(
                        os.path.join(root, file)
                    )

        for account in self.accounts:
            account.normalize()
            account.transactions["is_transfer"] = False
            account._sync_transaction_list()

    def __iter__(self):
        for account in self.accounts:
            for transaction in account.transaction_list:
                yield account, transaction

    def get_transactions(self, *predicates):
        # Add account name to each transaction
        for account in self.accounts:
            account.transactions["account"] = account.name

        # Collect transactions based on predicates
        return pd.DataFrame(
            [
                transaction
                for _, transaction in self
                if not predicates or all(pred(transaction) for pred in predicates)
            ]
        )

    def identify_transfers(self):
        """
        Identify internal transfers between bank accounts. Identification is dependent on relating a candidate
        transfer's sending and receiving account to the transfer and counter-transfer's descriptions along with
        a confidence value indicating the frequency of transfer's with the same descriptions between the accounts.

        phase 1: build the account-transfer-description (ATD) confidence directory that relates a potential
                 transfer's sending and receiving account by the transactions' descriptions.
            1. For each transaction, find a sole counter transaction indicating a transfer
            2. Link the sending and receiving accounts by the transfer's description pair with a confidence value
        phase 2: identify transactions with accounts and descriptions in the ATD confidence mapping that have both the highest confidence value.

        repeat these phases until transfers are no longer identified
        """

        atd_confidence = {}  # sending account name: {
        #    receiving account name: [
        #        [from account transaction description,
        #         to account transaction description,
        #         confidence value],
        #    ]
        # }
        passes_ran = transfers_in_pass = 0
        while True:
            # Phase 1: Build the ATD confidence directory
            for account, transaction in self:
                # Only consider transactions not already marked as transfers
                if transaction.is_transfer:
                    continue

                counter_transactions = self.find_counter_transactions(
                    account, transaction
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
                    receiving_accounts = atd_confidence.get(sending_account.name, {})
                    description_pairs = receiving_accounts.get(
                        receiving_account.name, []
                    )
                    existing_description_pair = [
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
                        self.log.append(
                            f"transaction of {self.format_amount(sending_transaction.amount)} from "
                            f"{sending_account.name} to {receiving_account.name} ({sending_transaction.description}) "
                            "is transfer"
                        )
                        self.log.append(
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
            self.log.append(
                f"{transfers_in_pass} transfers identified in pass {passes_ran}\n"
            )
            transfers_in_pass = 0

    def find_counter_transactions(self, account, transaction):
        """Find counter-transactions for a given transaction."""

        # A counter transaction is a valid counter-priced transaction in another account, not a guaranteed transfer
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

    def equate_transaction_descriptions(self, d1, d2, threshold=0.90):
        return SequenceMatcher(None, d1, d2).ratio() >= threshold

    def identify_returns(self):
        for account, transaction in self:
            if transaction.is_transfer or not account.is_return_candidate(transaction):
                continue

            original_transaction = account.find_counter_return(transaction)
            if original_transaction is None:
                continue

            self.log.append(
                f"transaction of {self.format_amount(transaction.amount)} from "
                f"{account.name} ({transaction.description}) "
                "is return"
            )
            self.log.append(
                f"transaction of {self.format_amount(original_transaction.amount)} from "
                f"{account.name} ({original_transaction.description}) "
                "is returned"
            )
            self.set_transfer(account, transaction.Index)
            self.set_transfer(account, original_transaction.Index)

    def set_transfer(self, account, transaction_index, value=True):
        account.transactions.loc[transaction_index, "is_transfer"] = value
        # Also update the transaction object in the list
        for transaction in account.transaction_list:
            if transaction.Index == transaction_index:
                transaction.is_transfer = value
                break

    def is_transfer(self, account, transaction_index) -> bool:
        return account.transactions.loc[transaction_index, "is_transfer"]

    def format_amount(self, amount: float) -> str:
        return f"-${abs(amount):.2f}" if amount < 0 else f"${abs(amount):.2f}"

    def get_log(self):
        log_string = "\n".join(self.log)
        self.log = []
        return log_string
