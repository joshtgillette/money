from banking.banker import Banker

class Tracker:

    def __init__(self, *categories):
        self.categories = categories

    def track(self, banker: Banker):
        for category in self.categories:
            category.filter(banker)
