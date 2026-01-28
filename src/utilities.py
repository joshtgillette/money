from argparse import _SubParsersAction
from pathlib import Path
from shutil import copy2

import pandas as pd


class Utilities:
    @staticmethod
    def register_parser(subparsers: _SubParsersAction) -> None:
        """
        Register the combine subcommand parser.

        Args:
            subparsers: The subparsers object from the main argument parser
        """

        combine_parser = subparsers.add_parser(
            "combine", help="combine multiple CSV files into one"
        )
        combine_parser.add_argument(
            "src_path",
            type=Path,
            help="source directory containing CSV files to combine",
        )
        combine_parser.add_argument(
            "dst_path",
            type=Path,
            help="destination path for the combined CSV file",
        )
        combine_parser.add_argument(
            "--sort_col",
            type=str,
            default=None,
            help="optional column name to sort the combined CSV by",
        )
        combine_parser.set_defaults(
            func=lambda args: Utilities.combine_csvs(
                args.src_path, args.dst_path, args.sort_col
            )
        )

        backup_parser = subparsers.add_parser(
            "backup", help="backup book.json to iCloud Drive"
        )
        backup_parser.set_defaults(func=lambda args: Utilities.backup_book())

    @staticmethod
    def combine_csvs(
        src_path: Path, dst_path: Path, sort_col: str | None = None
    ) -> None:
        """
        Recursively find all CSV files in src_path directory, combine them,
        optionally sort by sort_col, and write to dst_path.

        Args:
            src_path: Source directory to search for CSV files
            dst_path: Destination path for the combined CSV file
            sort_col: Optional column name to sort the combined data by

        Raises:
            ValueError: If no CSV files found or if CSVs have incompatible schemas
            FileNotFoundError: If src_path doesn't exist
        """

        print()

        # Check paths' existence
        if not src_path.exists():
            raise FileNotFoundError(f"source path does not exist: {src_path}")
        if not src_path.is_dir():
            raise ValueError(f"source path must be a directory: {src_path}")

        # Recursively find all CSV files
        csv_files = list(src_path.rglob("*.csv"))
        if not csv_files:
            raise ValueError(f"no CSV files found in: {src_path}")
        print(f"found {len(csv_files)} csv file(s) to attempt combine\n")

        # Read all CSV files
        dataframes = []
        reference_columns = None
        num_processed_files, num_processed_rows = 0, 0
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)

                # Check if this CSV has the same columns as the first one
                if reference_columns is None:
                    reference_columns = set(df.columns)
                else:
                    current_columns = set(df.columns)
                    if current_columns != reference_columns:
                        raise ValueError(
                            f"csv schema mismatch: {csv_file.name} has columns "
                            f"{current_columns} but expected {reference_columns}"
                        )

                dataframes.append(df)
                num_processed_files += 1
                num_processed_rows += len(df)
                print(f"loaded '{csv_file.relative_to(src_path)}'")
            except Exception as e:
                print(f"error loading '{csv_file.name}': {str(e).lower()}")
                continue

        # Combine all dataframes
        combined_df = pd.concat(dataframes, ignore_index=True)
        print(
            f"\n{num_processed_files} files totaling {num_processed_rows} rows combined into {len(combined_df)} rows"
        )

        # Sort if sort_col is provided and valid
        sort_status: str = "(unsorted)"
        if sort_col and sort_col in combined_df.columns:
            combined_df = combined_df.sort_values(by=sort_col, ascending=False)
            sort_status = ""

        # Write combined CSV
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        combined_df.to_csv(dst_path, index=False)
        print(f"csv written to {dst_path} {sort_status}\n")

    @staticmethod
    def backup_book() -> None:
        """
        Copy book.json to iCloud Drive folder.

        Raises:
            FileNotFoundError: If book.json doesn't exist or iCloud Drive is not accessible
        """
        print()

        # Define paths
        book_path = Path("book.json")
        icloud_path = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs"
        backup_path = icloud_path / "book.json"

        # Check if book.json exists
        if not book_path.exists():
            raise FileNotFoundError(f"book.json not found at: {book_path.absolute()}\n")

        # Check if iCloud Drive is accessible
        if not icloud_path.exists():
            raise FileNotFoundError(f"iCloud Drive not accessible at: {icloud_path}\n")

        # Copy the file
        try:
            copy2(book_path, backup_path)
            print("book successfully backed up to iCloud Drive\n")
        except Exception as e:
            print(f"✗ failed to backup book.json: {str(e)}\n")
            raise
