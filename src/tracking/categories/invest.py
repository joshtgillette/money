from tracking.category import Category
import pandas as pd

class Invest(Category):

    def __init__(self, label):
        super().__init__(label)

    def filter_function(self, _, transaction: pd.Series):
        return transaction.description == "FID BKG SVC LLC"
