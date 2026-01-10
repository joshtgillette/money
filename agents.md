# Agent Coding Style Guide

This document outlines the coding conventions and style preferences for this project based on the existing codebase.

## General Principles

- **Minimalism**: Write concise, focused code. Avoid over-engineering or unnecessary abstractions.
- **Clarity over cleverness**: Code should be self-documenting with clear naming and simple logic.
- **Functional approach**: Use lambda functions and functional patterns where appropriate.
- **Type safety**: Always include type hints for function parameters and return values.

## Code Organization

### File Structure
- Keep related functionality together in cohesive modules
- Use adapter pattern for bank-specific implementations
- Separate concerns: transaction logic, tagging, account management

### Class Design
- Use `__slots__` to optimize memory for data classes
- Leverage inheritance for common behavior (e.g., `Account`, `BankAccount`, `CreditCard`)
- Keep classes focused on a single responsibility
- Use abstract base classes (`ABC`) when defining interfaces

## Type Hints

### Always specify types for:
- Function parameters
- Return values  
- Class attributes
- Instance variables

### Examples:
```python
def __init__(self, name: str) -> None:
    self.name: str = name
    self.transactions: Dict[int, Transaction] = {}

def load_transactions(transactions_data: pd.DataFrame) -> Dict[int, Transaction]:
    transactions: Dict[int, Transaction] = {}
    return transactions
```

### Use precise types:
- `Dict[str, str]` not `dict`
- `List[Transaction]` not `list`
- `Optional[str]` for nullable values
- `Callable` for function types
- Type unions with `|` operator (e.g., `str | None`)

## Documentation

### Docstring Style
- Use concise, clear docstrings that explain **what** the function does
- Focus on the purpose and outcome, not implementation details
- Keep docstrings brief - one or two sentences for most functions
- Use triple quotes even for single-line docstrings

### Examples:
```python
def hash(self) -> str:
    """Generate a unique hash of a transaction.
    
    Returns:
        SHA256 hash of the transaction data
    """
```

```python
def discover_csvs(path: Path) -> List[Path]:
    """Recursively discover all CSV files in the given path."""
```

### Class Docstrings
- Describe the class's purpose and responsibility
- Keep it concise - one sentence for simple classes

```python
class Tagger:
    """Manages transaction tags loaded from CSV files."""
```

## Naming Conventions

### Variables and Functions
- Use descriptive, lowercase names with underscores: `transaction_data`, `load_transactions`
- Avoid abbreviations unless widely understood (e.g., `df` for DataFrame)
- Boolean variables: `is_transfer`, `by_month`

### Constants
- Use UPPER_CASE for class-level constants: `TAGS_PATH`, `SOURCE_TRANSACTIONS_PATH`

### Type Annotations
- For clarity: `amount: float`, `date: datetime`, `index: int`

## Imports

### Organization
- Group imports logically: stdlib, third-party, local
- Remove unused imports
- Use specific imports, not wildcards

### Example:
```python
import hashlib
from datetime import datetime
from typing import Any, Dict

import pandas as pd

from accounts.banker import Banker
from transaction import Transaction
```

## Functional Patterns

### Lambda Functions
- Use lambdas for simple data transformations
- Common pattern in adapters for normalizing data:

```python
self.date_normalizer = lambda df: pd.to_datetime(df["Date"])
self.amount_normalizer = lambda df: pd.to_numeric(df["Amount"])
self.description_normalizer = lambda df: df["Description"]
```

### List Comprehensions
- Use for filtering and transforming collections
- Keep them readable - break complex ones into multiple lines

```python
return [
    transaction
    for _, transaction in self
    if not predicates or all(pred(transaction) for pred in predicates)
]
```

## Data Handling

### Pandas
- Use method chaining where appropriate
- Leverage pandas built-in functions
- Use `pd.to_datetime()`, `pd.to_numeric()` for type conversion

### Path Handling
- Use `pathlib.Path` over string concatenation
- Use `/` operator for path joining: `path / "subdir"`

## Error Handling

- Use guard clauses to exit early
- Check for None/empty values before processing
- Validate data at boundaries (file loading, user input)

## Examples from Codebase

### Simple, Focused Functions
```python
def get_all_tags(self):
    return {
        tag.strip()
        for tags in self.tags.values()
        for tag in tags.split("|")
        if tag.strip()
    }
```

### Clean Class Initialization
```python
def __init__(self, banker: Banker) -> None:
    self.banker = banker
    self.tags: Dict[str, str] = {}  # hash -> comma-separated tags (lowercase)
```

### Type-Safe Dictionary Operations
```python
def load_transactions(transactions_data: pd.DataFrame) -> Dict[int, Transaction]:
    transactions: Dict[int, Transaction] = {}
    for row in transactions_data.itertuples():
        index = cast(int, row.Index)
        transactions[index] = Transaction(...)
    return transactions
```

## Anti-Patterns to Avoid

- Don't add comments for obvious code - let the code speak for itself
- Avoid deeply nested logic - use early returns
- Don't use mutable default arguments
- Avoid string concatenation for paths - use `pathlib`
- Don't repeat yourself - extract common patterns
- Avoid large functions - keep them focused and small

## Summary

The key philosophy is: **write clean, typed, minimal code that is easy to read and understand.** Every line should have a clear purpose, and the code should be self-explanatory through good naming and structure.
