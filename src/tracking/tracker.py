import pandas as pd

class Tracker:

    def __init__(self, *categories):
        self.categories = categories

    def track(self, transactions: pd.DataFrame):
        for category in self.categories:
            category.screen(transactions)
