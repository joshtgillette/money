import pandas as pd
from datetime import datetime

class Banker:

    def __init__(self, *accounts):
        self.accounts = list(accounts)
        self.transactions = pd.DataFrame()
        self.transactions_no_transfers = pd.DataFrame()
        self.log = []

    def load(self, months: list[datetime]):
        for account in self.accounts:
            account.load_transactions(months)
            account.normalize()


        self.transactions = self.aggregate_transactions()
        self.transactions_no_transfers = self.remove_transfers()

    def __iter__(self):
        for account in self.accounts:
            for _, transaction in account.transactions.iterrows():
                yield account, transaction

    def aggregate_transactions(self):
        transactions = []
        for account in self.accounts:
            if account.transactions.empty:
                continue

            transactions_with_account = account.transactions.copy()
            transactions_with_account['account'] = account.name
            transactions.append(transactions_with_account)
        transactions = pd.concat(transactions, ignore_index=True)

        return transactions[['date', 'account', 'amount', 'description']].sort_values('date').reset_index(drop=True)

    def remove_transfers(self):
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

        pass_count = net_removed = 0
        transfers_by_description = {}
        transactions = self.aggregate_transactions()
        while True:
            pass_count += 1

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
                    net_removed += transfer.amount + counter_transfer.iloc[0].amount

                    # Found a transfer pair, mark both for removal
                    self.log.append(f"removing transfer of ${abs(transfer.amount)} from {from_account} to {to_account} ({transfer.description})")
                    self.log.append(f"removing transfer of ${abs(transfer.amount)} from {to_account} to {from_account} ({counter_transfer.iloc[0].description})")

            if not transfers_to_remove:
                break

            transactions = transactions.drop(index=transfers_to_remove)
            self.log.append(f"{len(transfers_to_remove)} transfers removed in pass {pass_count} with net ${net_removed}\n")

        return transactions

    def get_log(self):
        log_string = "\n".join(self.log)
        self.log = []
        return log_string
