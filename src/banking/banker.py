import pandas as pd
from datetime import datetime

class Banker:

    def __init__(self, *accounts):
        self.accounts = list(accounts)
        self.transactions = pd.DataFrame()
        self.log = []

    def load(self, months: list[datetime]):
        for account in self.accounts:
            account.load_transactions(months)
            account.normalize()
            account.transactions["is_transfer"] = False

        self.aggregate_transactions()
        self.remove_transfers()

    def get_transactions(self, is_transfer=None):
        if is_transfer is None:
            return self.transactions

        return self.transactions[self.transactions['is_transfer'] == is_transfer]

    def __iter__(self):
        for account in self.accounts:
            for _, transaction in account.transactions.iterrows():
                yield account, transaction

    def aggregate_transactions(self):
        self.transactions = []
        for account in self.accounts:
            if account.transactions.empty:
                continue

            transactions_with_account = account.transactions.copy()
            transactions_with_account['account'] = account.name
            self.transactions.append(transactions_with_account)
        self.transactions = pd.concat(self.transactions, ignore_index=True)
        self.transactions = self.transactions[['date', 'account', 'amount', 'description', 'is_transfer']].sort_values('date').reset_index(drop=True)

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

        pass_num = removed_in_pass = net_amount_removed = 0
        transfers_by_description = {}
        while True:
            pass_num += 1

            # Build candidate transfer mapping
            for transaction in self.transactions[self.transactions["is_transfer"] == False].itertuples(index=False):
                counter_transactions = self.transactions[
                    (~self.transactions['is_transfer']) &
                    (self.transactions['amount'] == -transaction.amount) &
                    (self.transactions['account'] != transaction.account)
                ]

                # Only consider single, non-chained transfers
                if len(counter_transactions) == 0 or len(counter_transactions) > 1:
                    continue

                # Transaction and counter transaction are thought to be transfers
                transfer = transaction
                counter_transfer = counter_transactions.iloc[0]

                # From the transfer description, make a unique link between the accounts
                from_to_link = ((transfer.account, counter_transfer.account) if transfer.amount < 0 else
                                (counter_transfer.account, transfer.account))
                existing_links = transfers_by_description.get(transfer.description, [])
                if from_to_link not in existing_links:
                    transfers_by_description.update({transfer.description: existing_links + [from_to_link]})

            # Verify transfers from candidate mapping and remove
            for transaction in self.transactions.itertuples(index=True):
                if transaction.is_transfer == True:
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
                        self.transactions[
                            (~self.transactions['is_transfer']) &
                            (self.transactions['account'] == (to_account if transaction.amount < 0 else from_account)) &
                            (self.transactions['amount'] == -transaction.amount) &
                            (self.transactions['description'] == synonym_description)
                        ] for synonym_description in synonym_descriptions]
                    counter_transfer = next((counter_transfer for counter_transfer in counter_transfers
                                            if not counter_transfer.empty), pd.DataFrame())
                    if counter_transfer.empty or len(counter_transfer) > 1:
                        continue

                    # Transaction is confirmed to be a transfer!
                    transfer = transaction
                    self.transactions.loc[transfer.Index, "is_transfer"] = True
                    self.transactions.loc[counter_transfer.index[0], "is_transfer"] = True

                    # Found a transfer pair, mark both for removal
                    self.log.append(f"removing transfer of ${abs(transfer.amount)} from {from_account} to {to_account} ({transfer.description})")
                    self.log.append(f"removing transfer of ${abs(transfer.amount)} from {to_account} to {from_account} ({counter_transfer.iloc[0].description})")

                    removed_in_pass += 2
                    net_amount_removed += transfer.amount + counter_transfer.iloc[0].amount

            if not removed_in_pass:
                break
            self.log.append(f"{removed_in_pass} transfers removed in pass {pass_num} with net ${net_amount_removed}\n")
            removed_in_pass = 0

    def get_log(self):
        log_string = "\n".join(self.log)
        self.log = []
        return log_string
