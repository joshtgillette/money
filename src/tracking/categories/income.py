from tracking.categories.category import Category
import pandas as pd

class Income(Category):

    def __init__(self, label):
        super().__init__(label)

    def screen(self, transactions: pd.DataFrame):
        self.transactions = transactions[
            transactions['description'].str.contains("COMCAST (CC) OF",
                                                     regex=False)
        ]
