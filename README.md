# Money - Personal Finance Manager

A Python-based personal finance management system that normalizes transactions from various banks and generates reports.

## Features

### Transaction Tagging

The system supports manual tagging of transactions to categorize them for better analysis.

#### How It Works

1. **Transactions Directory**: After running the program, transactions are saved to the `transactions/` directory, organized by month (e.g., `0525.csv` for May 2025).

2. **Tag Column**: Each monthly CSV file includes a `tag` column where you can manually add tags to transactions.

3. **Tag Persistence**: Tags are stored in a `tags.json` file and persist across runs. When you download new transaction data, previously tagged transactions will automatically retain their tags.

4. **Multiple Tags**: You can add multiple tags to a transaction by separating them with commas (e.g., `shopping,home improvement`).

5. **Case Insensitive**: Tags are automatically normalized to lowercase (e.g., "Income" and "income" are treated the same).

#### Example Usage

1. Run the program to load transactions:

   ```bash
   python src/main.py
   ```

2. Open `transactions/0525.csv` and add tags to the tag column:

   ```csv
   date,account,amount,description,tag
   2024-05-15,SoFi Checking,1500.0,COMCAST (CC) OF PAYROLL,income
   2024-05-16,SoFi Checking,-45.5,AMAZON PURCHASE,"shopping,home improvement"
   2024-05-20,SoFi Checking,-120.0,ELECTRIC COMPANY,utilities
   ```

3. The tags are automatically saved to `tags.json` for persistence.

4. Next time you run the program, even if you download new transaction data with overlapping dates, your tags will be preserved.

#### Tag Reports

After running the program, check the `report/transactions/tags/` directory for:

- A CSV file for each tag containing all transactions with that tag
- `untagged.csv` containing all transactions without tags

#### Transaction Matching

Tags are matched based on:

- **Date**: The transaction date
- **Account**: The transaction account
- **Amount**: The transaction amount
- **Description**: The transaction description

This means each unique transaction (same date, account, amount, and description) will have its own tags.

## Directory Structure

```
money/
├── source transactions/      # Source CSV files from banks (input)
├── transactions/          # Normalized transactions with tags (editable)
├── report/               # Generated reports
│   ├── transactions/
│   │   ├── tags/        # Tag-based transaction reports
│   │   ├── accounts/    # Account-specific reports
│   │   └── monthly/     # Monthly reports
│   └── notes.txt
```

Note: `tags.json` is not used; tags are loaded from the `transactions/` CSV files.

## Setup

1. Install dependencies:

   ```bash
   pip install pandas
   ```

2. Place your bank transaction CSV files in the `source transactions/` directory, named according to your account names (e.g., `sofi checking.csv`).

3. Run the program:
   ```bash
   python src/main.py
   ```

## Supported Banks

The system currently supports the following banks with their specific CSV formats:

- SoFi (Checking and Savings)
- Apple (Savings)
- PNC (Checking and Savings)
- ESL (Checking and Savings)
- Apple Card (Credit)
- Wells Fargo (Credit Card)
- Chase (Credit Card)

Each bank has an adapter that normalizes its specific CSV format into a standard format.
