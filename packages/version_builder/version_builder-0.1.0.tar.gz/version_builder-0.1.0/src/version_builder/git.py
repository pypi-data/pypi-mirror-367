"""Module for interacting with Git repositories.

Provides a helper class to work with Git tags and logging.
"""

from logging import Logger

from git import Repo

from .logger import logger


class GitHelper:
    """A helper class to interact with a local Git repository."""

    repo: Repo
    log: Logger

    def __init__(self) -> None:
        """Initialize the Git repository and logger."""
        self.repo = Repo.init()
        self.log = logger

    def get_last_tag(self) -> None:
        """Log information about existing Git tags or absence of them."""
        if not self.repo.tags:
            self.log.info("No tags found")

        for tag in self.repo.tags:
            self.log.info(tag)
