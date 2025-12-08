from accounts.adapters.bank.apple import Apple
from accounts.adapters.bank.esl import ESL
from accounts.adapters.bank.pnc import PNC
from accounts.adapters.bank.sofi import SoFi
from accounts.adapters.credit.apple import Apple as AppleCredit
from accounts.adapters.credit.chase import Chase
from accounts.adapters.credit.wells_fargo import WellsFargo
from accounts.banker import Banker
from advisor import Advisor
from tracking.categories.house import House
from tracking.categories.income import Income
from tracking.categories.interest import Interest
from tracking.categories.invest import Invest
from tracking.categories.jody import Jody
from tracking.categories.rewards import Rewards
from tracking.categories.transfer import Transfer

if __name__ == "__main__":
    Advisor(
        Banker(
            SoFi("SoFi Checking"),
            SoFi("SoFi Savings"),
            Apple("Apple Savings"),
            PNC("PNC Checking"),
            PNC("PNC Savings"),
            ESL("ESL Checking"),
            ESL("ESL Savings"),
            AppleCredit("Apple Card"),
            WellsFargo("Wells Fargo Credit Card"),
            Chase("Chase Credit Card"),
        ),
        [
            Income("income"),
            Interest("interest"),
            Transfer("transfer"),
            Jody("jody"),
            House("house"),
            Invest("invest"),
            Rewards("rewards"),
        ],
    ).start()
