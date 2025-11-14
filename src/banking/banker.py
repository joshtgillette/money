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

        self.remove_transfers()

    def __iter__(self):
        for account in self.accounts:
            for transaction in account.transactions.itertuples(index=True):
                yield account, transaction

    def get_transactions(self, is_transfer=None):
        columns = ['date', 'account', 'amount', 'description', 'is_transfer']
        transactions = []
        for account, transaction in self:
            if is_transfer is not None and transaction.is_transfer != is_transfer:
                continue

            transaction_with_account = pd.Series(transaction._asdict())
            transaction_with_account['account'] = account.name
            transactions.append(transaction_with_account)
        if not transactions:
            return pd.DataFrame(columns=columns)

        return pd.DataFrame(transactions)[columns].sort_values('date').reset_index(drop=True)

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
            for account, transaction in self:
                if transaction.is_transfer:
                    continue

                # Transaction and counter transaction are thought to be transfers
                counter_account, counter_transfer = self.find_counter_transfer(account, transaction)
                if not counter_account:
                    continue
                transfer = transaction

                # From the transfer description, make a unique link between the accounts
                from_to_link = ((account.name, counter_account.name) if transfer.amount < 0 else
                                (counter_account.name, account.name))
                existing_links = transfers_by_description.get(transfer.description, [])
                if from_to_link not in existing_links:
                    transfers_by_description.update({transfer.description: existing_links + [from_to_link]})

            # Verify transfers from candidate mapping and remove
            for account, transaction in self:
                if transaction.is_transfer:
                    continue

                # For the given transaction with a thought to be transfer description, iterate over the linked accounts
                for (from_account_name, to_account_name) in transfers_by_description.get(transaction.description, []):
                    # Multiple (two) descriptions can indicate the same account transfer from -> to flow
                    synonym_descriptions = [description for description, links in transfers_by_description.items()
                                            if (from_account_name, to_account_name) in links]

                    # Perform the transfer search. A transfer:
                    #   1. Has the exact opposite amount (zero-sum)
                    #   2. If the transfer amount is negative, search for the "to" account, otherwise search for the "from" account
                    #   3. Has a synonym description that indicates the same account transfer flow
                    counter_transfers = [
                        self.find_transactions(
                            to_account_name if transaction.amount < 0 else from_account_name,
                            -transaction.amount,
                            synonym_description
                        ) for synonym_description in synonym_descriptions
                    ]
                    counter_transfer = next(((account, counter_transfer) for account, counter_transfer in counter_transfers
                                            if not counter_transfer.empty), (None, pd.DataFrame()))
                    if counter_transfer[1].empty or len(counter_transfer[1]) > 1:
                        continue
                    counter_account, counter_transfer = counter_transfer
                    counter_transfer = counter_transfer.iloc[0]

                    # Transaction is confirmed to be a transfer!
                    transfer = transaction
                    account.transactions.loc[transfer.Index, "is_transfer"] = True
                    counter_account.transactions.loc[counter_transfer.Index, "is_transfer"] = True

                    # Found a transfer pair, mark both for removal
                    self.log.append(f"removing transfer of ${abs(transfer.amount)} from {from_account_name} to {to_account_name} ({transfer.description})")
                    self.log.append(f"removing transfer of ${abs(transfer.amount)} from {to_account_name} to {from_account_name} ({counter_transfer.description})")
                    removed_in_pass += 2
                    net_amount_removed += transfer.amount + counter_transfer.amount

            if not removed_in_pass:
                break
            self.log.append(f"{removed_in_pass} transfers removed in pass {pass_num} with net ${net_amount_removed}\n")
            removed_in_pass = 0

    def find_counter_transfer(self, account, transaction):
        """Find the definitive counter-transfer for a given transaction."""

        # A counter transaction is a counter-priced transaction in another account, not a guaranteed transfer
        counter_transfer = None
        for a, t in self:
            if a != account and t.amount == -transaction.amount and not t.is_transfer:
                if counter_transfer:
                    # Only consider single, non-chained transfers
                    return None, None

                counter_transfer = (a, pd.DataFrame([t]))

        # This is a confirmed counter-transfer
        return counter_transfer if counter_transfer else (None, None)

    def find_transactions(self, account_name, amount, description):
        """Find transactions matching the given criteria."""

        account, transactions = None, []
        for a, t in self:
            if not t.is_transfer and a.name == account_name and t.amount == amount and t.description == description:
                account = a
                transactions.append(t)

        return account, pd.DataFrame(transactions)

    def get_log(self):
        log_string = "\n".join(self.log)
        self.log = []
        return log_string
