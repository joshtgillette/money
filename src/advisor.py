from accounts.banker import Banker
from report import Report
from tracking.categories.transfer import Transfer
from tracking.category import Category


class Advisor:
    def __init__(self, banker: Banker, categories: list[Category]):
        self.banker = banker
        self.categories = categories
        self.report = Report()

    def start(self):
        # Direct the banker to load transactions for the specified date range
        self.banker.load()
        if sum(len(account.transactions) for account in self.banker.accounts) == 0:
            self.report.note("No transactions loaded.")
            return

        # Remove transfers if the transfer category exists
        if "transfer" in [category.label for category in self.categories]:
            self.report.note_header("TRANSFER REMOVAL")
            self.banker.identify_returns()
            self.banker.identify_transfers()
            self.report.note(self.banker.get_log())

        # Write transactions data to the report
        transactions = self.banker.get_transactions()
        self.report.write_transactions(transactions, "all")
        non_transfer_transactions = self.banker.get_transactions(
            lambda t: not t.is_transfer
        )
        self.report.write_transactions(non_transfer_transactions, "all - no transfers")
        self.report.note(
            f"loaded {len(self.banker.accounts)} bank accounts "
            f"with {len(transactions)} total transactions, "
            f"{len(non_transfer_transactions)} non-transfers\n"
        )

        # Apply each category's filter and write categorized transactions to the report
        self.report.note_header("CATEGORY TRACKING")
        for category in self.categories:
            category.apply_filter(self.banker)
            transactions = self.banker.get_transactions(
                lambda t: getattr(t, category.label),
                lambda t: not t.is_transfer
                if not isinstance(category, Transfer)
                else True,
            )
            self.report.note(
                f"categorized {len(transactions)} transactions as {category.label} "
                f"totaling ${transactions['amount'].sum():,.2f}"
            )
            self.report.write_transactions(transactions, f"categories/{category.label}")
        self.report.write_transactions(
            self.banker.get_transactions(
                lambda t: not any(
                    getattr(t, category.label) for category in self.categories
                )
            ),
            "uncategorized",
        )

        # Write account transactions - pass transaction lists directly
        for account in self.banker.accounts:
            if account.transactions:
                self.report.write_transactions(
                    account.transactions.values(),
                    f"accounts/{account.name.lower()}",
                    columns=["date", "amount", "description"],
                )
