from argparse import ArgumentParser
from banking.banker import Banker
from banking.accounts.sofi import SoFi
from banking.accounts.apple import Apple
from banking.accounts.pnc import PNC
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
        pd.date_range(
            start=datetime.strptime(args.start, "%m%y"),
            end=datetime.strptime(args.end, "%m%y"),
            freq='MS'
        ).tolist(),
        Banker(SoFi("Checking"), SoFi("Savings"), Apple("Savings"), PNC("Checking"), PNC("Savings"))
    ).start()
