from typing import cast

import pandas as pd

from account import Account

ACCOUNT_ADAPTERS = [
    Account(
        "SoFi Checking",
        date_normalizer=lambda df: pd.to_datetime(df["Date"]),
        amount_normalizer=lambda df: cast(pd.Series, pd.to_numeric(df["Amount"])),
        description_normalizer=lambda df: pd.Series(df["Description"]),
    ),
    Account(
        "SoFi Savings",
        date_normalizer=lambda df: pd.to_datetime(df["Date"]),
        amount_normalizer=lambda df: cast(pd.Series, pd.to_numeric(df["Amount"])),
        description_normalizer=lambda df: pd.Series(df["Description"]),
    ),
    Account(
        "Apple Savings",
        date_normalizer=lambda df: pd.to_datetime(df["Transaction Date"]),
        amount_normalizer=lambda df: pd.to_numeric(df["Amount"])
        * df["Transaction Type"].eq("Credit").map(lambda b: 1 if bool(b) else -1),
        description_normalizer=lambda df: pd.Series(df["Description"]),
    ),
    Account(
        "PNC Checking",
        date_normalizer=lambda df: pd.to_datetime(df["Transaction Date"]),
        amount_normalizer=lambda df: cast(
            pd.Series,
            pd.to_numeric(df["Amount"].str.replace(r"[\+\$\s]", "", regex=True)),
        ),
        description_normalizer=lambda df: pd.Series(df["Transaction Description"]),
    ),
    Account(
        "PNC Savings",
        date_normalizer=lambda df: pd.to_datetime(df["Transaction Date"]),
        amount_normalizer=lambda df: cast(
            pd.Series,
            pd.to_numeric(df["Amount"].str.replace(r"[\+\$\s]", "", regex=True)),
        ),
        description_normalizer=lambda df: pd.Series(df["Transaction Description"]),
    ),
    Account(
        "ESL Checking",
        date_normalizer=lambda df: pd.to_datetime(df["Date"]),
        amount_normalizer=lambda df: cast(
            pd.Series,
            pd.Series(pd.to_numeric(df["Amount Credit"].fillna(0)))
            + pd.Series(pd.to_numeric(df["Amount Debit"].fillna(0))),
        ),
        description_normalizer=lambda df: pd.Series(
            df["Description"]
            .astype("string")
            .fillna("")
            .str.cat(df["Memo"].astype("string").fillna("").str.strip(), sep=" ")
        ),
    ),
    Account(
        "ESL Savings",
        date_normalizer=lambda df: pd.to_datetime(df["Date"]),
        amount_normalizer=lambda df: cast(
            pd.Series,
            pd.Series(pd.to_numeric(df["Amount Credit"])).fillna(0)
            + pd.Series(pd.to_numeric(df["Amount Debit"])).fillna(0),
        ),
        description_normalizer=lambda df: pd.Series(
            df["Description"]
            .astype("string")
            .fillna("")
            .str.cat(df["Memo"].astype("string").fillna("").str.strip(), sep=" ")
        ),
    ),
    Account(
        "ESL Shared",
        date_normalizer=lambda df: pd.to_datetime(df["Date"]),
        amount_normalizer=lambda df: cast(
            pd.Series,
            pd.Series(pd.to_numeric(df["Amount Credit"])).fillna(0)
            + pd.Series(pd.to_numeric(df["Amount Debit"])).fillna(0),
        ),
        description_normalizer=lambda df: pd.Series(
            df["Description"]
            .astype("string")
            .fillna("")
            .str.cat(df["Memo"].astype("string").fillna("").str.strip(), sep=" ")
        ),
    ),
    Account(
        "Apple Card",
        date_normalizer=lambda df: pd.to_datetime(df["Transaction Date"]),
        amount_normalizer=lambda df: pd.Series(pd.to_numeric(df["Amount (USD)"])).mul(
            -1
        ),
        description_normalizer=lambda df: pd.Series(df["Description"]),
    ),
    Account(
        "Wells Fargo Active Cash",
        date_normalizer=lambda df: pd.to_datetime(df.iloc[:, 0]),
        amount_normalizer=lambda df: cast(pd.Series, pd.to_numeric(df.iloc[:, 1])),
        description_normalizer=lambda df: pd.Series(df.iloc[:, 4]),
        header_val=None,
    ),
    Account(
        "Chase Freedom Unlimited",
        date_normalizer=lambda df: pd.to_datetime(df["Transaction Date"]),
        amount_normalizer=lambda df: cast(pd.Series, pd.to_numeric(df["Amount"])),
        description_normalizer=lambda df: pd.Series(df["Description"]),
    ),
    Account(
        "Discover It",
        date_normalizer=lambda df: pd.to_datetime(df["Trans. Date"]),
        amount_normalizer=lambda df: cast(pd.Series, pd.to_numeric(df["Amount"])).mul(
            -1
        ),
        description_normalizer=lambda df: pd.Series(df["Description"]),
    ),
]
