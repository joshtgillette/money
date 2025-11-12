import pandas as pd
from abc import ABC, abstractmethod

class Category(ABC):

    def __init__(self, label):
        self.label = label
        self.transactions = pd.DataFrame()

    @abstractmethod
    def screen(self, transactions: pd.DataFrame):
        """Override this method to filter transactions."""
        pass

