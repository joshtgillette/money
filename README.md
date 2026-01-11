# Money - Personal Finance Manager

A Python-based personal finance management system that normalizes and organizes transactions from multiple banks and credit cards.

## Features

### Transaction Normalization

The system automatically converts CSV files from various banks into a standardized format for easy analysis and tracking.

### Transaction Tagging

Manually tag transactions to categorize and organize your spending.

#### How Tagging Works

1. **Load Transactions**: Run the program to normalize transactions from your bank CSV files
2. **Tag Transactions**: Open monthly CSV files in `transactions/months/` and add tags in the `tags` column
3. **Persistent Tags**: Tags are automatically preserved when you reload transactions
4. **Multiple Tags**: Separate multiple tags with pipes: `tag1|tag2|tag3`
5. **Tag Reports**: View transactions grouped by tag in the `transactions/tagged/` directory

#### Tagging Example

After running the program, edit `transactions/months/0525.csv`:

```csv
date,amount,description,tags
2024-05-15,1500.0,PAYROLL DEPOSIT,income
2024-05-16,-45.5,AMAZON PURCHASE,shopping|home improvement
2024-05-20,-120.0,ELECTRIC COMPANY,utilities
```

On the next run, your tags will be preserved and transactions will be organized in `transactions/tagged/` by tag name.

#### Transaction Matching

Tags are matched to transactions using a unique hash of:

- Date
- Amount
- Description

This ensures each unique transaction maintains its own tags across program runs.

## Directory Structure

```
money/
├── sources/    # Place your bank CSV files here (input)
├── transactions/
│   ├── all.csv            # All transactions combined
│   ├── months/            # Transactions grouped by month (editable)
│   ├── accounts/          # Transactions grouped by account
│   └── tagged/            # Transactions grouped by tag
└── src/                   # Application source code
```

## Setup

### Prerequisites

- Python 3.13 or higher
- pandas library

### Installation

1. Install dependencies:

   ```bash
   pip install pandas
   ```

2. Place your bank CSV files in the `sources/` directory
   - Name files using lowercase account names (e.g., `sofi checking.csv`, `apple card.csv`)

3. Run the program:
   ```bash
   python src/main.py
   ```

## Supported Banks

The system includes adapters for the following financial institutions:

### Bank Accounts

- **SoFi** - Checking and Savings
- **Apple** - Savings
- **PNC** - Checking and Savings
- **ESL Federal Credit Union** - Checking and Savings

### Credit Cards

- **Apple Card**
- **Chase**
- **Wells Fargo**

Each adapter handles the specific CSV format for that institution and normalizes it to a standard format.

## Adding New Banks

To add support for a new bank:

1. Create an adapter class in `src/accounts/adapters/bank/` or `src/accounts/adapters/credit/`
2. Inherit from `BankAccount` or `CreditCard`
3. Define normalizer functions for date, amount, and description columns
4. Add the adapter to the `Advisor` class in `src/advisor.py`

See existing adapters for examples.

## Usage

1. **Initial Load**: Place CSV files in `sources/` and run `python src/main.py`
2. **Add Tags**: Edit CSV files in `transactions/months/` to add tags
3. **Reload**: Run the program again - tags will be preserved and reports regenerated
4. **View Reports**: Check organized transactions in the `transactions/` directory

## Notes

- The program clears and regenerates the `transactions/` directory on each run
- Tags are loaded from the `transactions/months/` CSV files, not from a separate tags file
- All financial data stays local - nothing is uploaded or shared
