from tracking.category import Category
import pandas as pd

class Jody(Category):

    def __init__(self, label):
        super().__init__(label)

    def filter_function(self, _, transaction: pd.Series):
        return transaction.description == "Deposit Internet Transfer from 708226014 CK"
