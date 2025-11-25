from tracking.category import Category
import pandas as pd

class Jody(Category):

    def __init__(self, label):
        super().__init__(label)

    def filter_function(self, _, transaction: pd.Series):
        return transaction.description == "ESL FEDERAL CU P2P ACH WEB PAYMENT JOSHUA GILLETTE"
