import hashlib
import json
import os
from typing import Dict, Set

from transaction import Transaction


class TagManager:
    """Manages transaction tags with persistence across runs."""

    TAGS_FILE: str = "tags.json"

    def __init__(self) -> None:
        self.tags: Dict[str, str] = {}  # hash -> comma-separated tags (lowercase)
        self.load()

    def load(self) -> None:
        """Load tags from the persistent storage file."""
        if os.path.exists(self.TAGS_FILE):
            try:
                with open(self.TAGS_FILE, "r") as f:
                    self.tags = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                # If the file is corrupted or unreadable, start fresh
                print(f"Warning: Could not load tags from {self.TAGS_FILE}: {e}")
                self.tags = {}

    def save(self) -> None:
        """Save tags to the persistent storage file."""
        with open(self.TAGS_FILE, "w") as f:
            json.dump(self.tags, f, indent=2)

    def _create_transaction_hash(self, amount: float, description: str) -> str:
        """Create a hash from transaction amount and description.

        Args:
            amount: Transaction amount
            description: Transaction description

        Returns:
            SHA256 hash of the transaction data
        """
        transaction_str = f"{amount}|{description}"
        return hashlib.sha256(transaction_str.encode()).hexdigest()

    def hash_transaction(self, transaction: Transaction) -> str:
        """Generate a unique hash for a transaction.

        Uses amount and description to create a consistent identifier.
        Date is intentionally excluded to allow tags to persist across
        different transaction downloads with overlapping time periods.
        """
        return self._create_transaction_hash(transaction.amount, transaction.description)

    def get_tags(self, transaction: Transaction) -> str:
        """Get the tags for a transaction (empty string if none)."""
        tx_hash = self.hash_transaction(transaction)
        return self.tags.get(tx_hash, "")

    def _normalize_tags(self, tags: str) -> str:
        """Normalize tags to lowercase and strip whitespace.

        Args:
            tags: Comma-separated tags

        Returns:
            Normalized comma-separated tags, or empty string if no valid tags
        """
        if not tags.strip():
            return ""
        normalized_tags = ",".join(
            tag.strip().lower() for tag in tags.split(",") if tag.strip()
        )
        return normalized_tags

    def set_tags(self, transaction: Transaction, tags: str) -> None:
        """Set tags for a transaction.

        Args:
            transaction: The transaction to tag
            tags: Comma-separated tags (will be normalized to lowercase)
        """
        tx_hash = self.hash_transaction(transaction)
        normalized_tags = self._normalize_tags(tags)
        
        if normalized_tags:
            self.tags[tx_hash] = normalized_tags
        else:
            # Remove tag if empty
            self.tags.pop(tx_hash, None)
        self.save()

    def set_tags_by_data(self, amount: float, description: str, tags: str) -> None:
        """Set tags for a transaction using raw data instead of Transaction object.

        Args:
            amount: Transaction amount
            description: Transaction description
            tags: Comma-separated tags (will be normalized to lowercase)
        """
        # Create hash using the same logic as hash_transaction
        tx_hash = self._create_transaction_hash(amount, description)
        normalized_tags = self._normalize_tags(tags)

        if normalized_tags:
            self.tags[tx_hash] = normalized_tags
        else:
            # Remove tag if empty
            self.tags.pop(tx_hash, None)
        self.save()

    def get_all_unique_tags(self) -> Set[str]:
        """Get a set of all unique tags across all transactions."""
        all_tags: Set[str] = set()
        for tags_str in self.tags.values():
            if tags_str:
                all_tags.update(tags_str.split(","))
        return all_tags
