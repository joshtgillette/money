from argparse import ArgumentParser
from accounts.banker import Banker
from accounts.adapters.bank.sofi import SoFi
from accounts.adapters.bank.apple import Apple
from accounts.adapters.bank.pnc import PNC
from accounts.adapters.bank.esl import ESL
from accounts.adapters.credit.apple import Apple as AppleCredit
from accounts.adapters.credit.wells_fargo import WellsFargo
from accounts.adapters.credit.chase import Chase
from tracking.categories.income import Income
from tracking.categories.interest import Interest
from tracking.categories.transfer import Transfer
from tracking.categories.jody import Jody
from tracking.categories.house import House
from tracking.categories.invest import Invest
from tracking.categories.rewards import Rewards
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
        Banker(SoFi("Checking"), SoFi("Savings"), Apple("Savings"), PNC("Checking"), PNC("Savings"), ESL("Savings"),
               AppleCredit(), WellsFargo(), Chase()),
        [Income("income"), Interest("interest"), Transfer("transfer"), Jody("jody"), House("house"), Invest("invest"), Rewards("rewards")]
    ).start()
