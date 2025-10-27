from argparse import ArgumentParser
from bank_accounts.sofi import SoFi
from bank_accounts.apple import Apple
from bank_accounts.pnc import PNC
from datetime import datetime
from advisor import Advisor
import pandas as pd

if __name__ == "__main__":
    parser = ArgumentParser(description="Money advisor")
    parser.add_argument(
        "--start",
        type=str,
        default="0925",
        help="Start date for the report"
    )
    parser.add_argument(
        "--end",
        type=str,
        default=datetime.now().strftime("%m%y"),
        help="End date for the report"
    )
    args = parser.parse_args()

    Advisor(
        [SoFi("Checking"), SoFi("Savings"), Apple("Savings"), PNC("Checking"), PNC("Savings")],
        pd.date_range(
            start=datetime.strptime(args.start, "%m%y"),
            end=datetime.strptime(args.end, "%m%y"),
            freq='MS'
        ).tolist()
    ).start()
