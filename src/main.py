"""Main entry point for the money management application."""

import argparse

from advisor import Advisor
from utilities import Utilities

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="a financial management program")
    subparsers = parser.add_subparsers(dest="command", help="available commands")

    # Subcommand: advise (default behavior)
    advise_parser = subparsers.add_parser(
        "advise", help="run the financial advisor analysis"
    )
    advise_parser.set_defaults(func=lambda args: Advisor().advise())

    # Let each class register its own subparser
    Utilities.register_parser(subparsers)

    args = parser.parse_args()
    # If a command was specified and has a handler, call it
    if hasattr(args, "func"):
        args.func(args)
    else:
        # Default to advise if no command specified
        Advisor().advise()
