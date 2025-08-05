"""Module for the command-line interface of version_builder.

Provides a CLI entry point to interact with Git tags and display help.
"""

import argparse

from .git import GitHelper


class CLI:
    """Handles command-line arguments and user interaction."""

    def __init__(self) -> None:
        """Initialize the Git helper and argument parser."""
        self.git = GitHelper()

        self.parser = argparse.ArgumentParser(
            prog="version_builder",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        self.parser.add_argument(
            "-lv",
            "--last_version",
            action="store_true",
            help="Show last version",
        )

    def __call__(self) -> None:
        """Parse arguments and execute the appropriate command."""
        args = self.parser.parse_args()

        if args.last_version:
            self.show_last_tag()
        else:
            self.help()

    def help(self) -> None:
        """Print help message from the argument parser."""
        self.parser.print_help()

    def show_last_tag(self) -> None:
        """Display the last Git tag using the GitHelper."""
        self.git.get_last_tag()


def main() -> None:
    """Entry point for the CLI application."""
    cli_helper = CLI()
    cli_helper()
