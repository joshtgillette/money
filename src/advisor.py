from datetime import datetime
import pandas as pd
from report import Report

class Advisor:

    def __init__(self, accounts: list[str], months: list[datetime]):
        self.accounts = accounts
        self.months = months
        self.report = Report(self.months)

    def start(self):
        self.load_and_normalize_data()
        self.remove_internal_transfers()
        self.calculate()
        self.report.write()

    def load_and_normalize_data(self):
        for account in self.accounts:
            account.load_transactions(self.months)
            account.normalize()

    def remove_internal_transfers(self):
        """
        phase 1: find candidate transfers -
            1. For each transaction search for a one-off counter transaction from another account
            2. If found link the two accounts by description, denoting a candidate transfer
        phase 2: confirm transfers and remove -
            1. For each transaction find a counter transaction with:
                - the exact opposite amount (zero-sum)
                - from/to the correct account based on transfer direction
                - a synonym description that indicates the same account transfer flow

        repeat these phases until transfers are no longer removed
        """

        transfers_by_description = {}
        transactions = self.aggregate_transactions()
        while True:
            # Build candidate transfer mapping
            for transaction in transactions.itertuples(index=False):
                counter_transactions = transactions[transactions['amount'] == -transaction.amount]

                # Only consider single, non-chained transfers
                if len(counter_transactions) == 0 or len(counter_transactions) > 1:
                    continue

                # Set suspected counter transfer
                counter_transaction = counter_transactions.iloc[0]

                # A transfer cannot be within the same account
                if transaction.account == counter_transaction.account:
                    continue

                # Transaction and counter transaction are thought to be transfers
                transfer = transaction
                counter_transfer = counter_transaction

                # From the transfer description, make a unique link between the accounts
                from_to_link = ((transfer.account, counter_transfer.account) if transfer.amount < 0 else
                                (counter_transfer.account, transfer.account))
                existing_links = transfers_by_description.get(transfer.description, [])
                if from_to_link not in existing_links:
                    transfers_by_description.update({transfer.description: existing_links + [from_to_link]})

            # Verify transfers from candidate mapping and remove
            transfers_to_remove = set()
            for transaction in transactions.itertuples(index=True):
                # Only consider transactions with descriptions thought to be transfers and
                # ensure "deleted" transactions are not reconsidered due to pairing
                if (transaction.description not in transfers_by_description or
                    transaction.Index in transfers_to_remove):
                    continue

                # For the given transaction with a thought to be transfer description, iterate over the linked accounts
                for (from_account, to_account) in transfers_by_description.get(transaction.description, []):
                    # Multiple (two) descriptions can indicate the same account transfer from -> to flow
                    synonym_descriptions = [description for description, links in transfers_by_description.items()
                                            if (from_account, to_account) in links]

                    # Perform the transfer search. A transfer:
                    #   1. Has the exact opposite amount (zero-sum)
                    #   2. If the transfer amount is negative, search for the "to" account, otherwise search for the "from" account
                    #   3. Has a synonym description that indicates the same account transfer flow
                    counter_transfers = [
                        transactions[
                            (transactions['amount'] == -transaction.amount) &
                            (transactions['account'] == (to_account if transaction.amount < 0 else from_account)) &
                            (transactions['description'] == synonym_description)
                        ] for synonym_description in synonym_descriptions]
                    counter_transfer = next((counter_transfer for counter_transfer in counter_transfers
                                            if not counter_transfer.empty), pd.DataFrame())
                    if counter_transfer.empty or len(counter_transfer) > 1:
                        continue

                    # Transaction is confirmed to be a transfer!
                    transfer = transaction
                    transfers_to_remove.update([transfer.Index, counter_transfer.index[0]])

                    # Found a transfer pair, mark both for removal
                    transfers_to_remove.update([transaction.Index, counter_transfer.index[0]])

            transactions_no_transfers = transactions.drop(index=transfers_to_remove)
            if len(transactions_no_transfers) == len(transactions):
                break
            transactions = transactions_no_transfers

        # Remove transfers from transactions
        self.report.transactions_no_transfers = transactions.drop(index=transfers_to_remove)

    def aggregate_transactions(self):
        transactions = []
        for account in self.accounts:
            transactions_with_account = account.transactions.copy()
            transactions_with_account['account'] = account.name
            transactions.append(transactions_with_account)
        transactions = pd.concat(transactions, ignore_index=True)

        return transactions[['date', 'account', 'amount', 'description']].sort_values('date').reset_index(drop=True)

    def calculate(self):
        # Aggregate all account transactions, reorder and sort, calculate total spent
        self.report.transactions = self.aggregate_transactions()
        self.report.total_spent = self.report.transactions['amount'].sum()
