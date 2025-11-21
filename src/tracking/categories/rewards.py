from tracking.category import Category
from accounts.adapters.bank.bank_account import BankAccount
import pandas as pd
from datetime import datetime

class Rewards(Category):

    def __init__(self, label):
        super().__init__(label)

    def filter_function(self, account: BankAccount, transaction: pd.Series):
        return transaction.amount > 0 and \
                (transaction.description == "Money Promo Bonus" or \
                 transaction.description == "Money Referral Bonus" or \
                 "CHASE CREDIT CRD RWRD RDM ACH CREDIT" in transaction.description or \
                 (transaction.date.date() == datetime(2025, 8, 25).date() and account.name == "SoFi Checking" and transaction.description == "VENMO"))