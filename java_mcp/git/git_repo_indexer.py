"""
Git Repository Indexer Module for Java MCP Server

This module provides the GitRepoIndexer class for managing and indexing multiple git repositories.
It serves as a centralized interface for handling batch git operations including validation,
cloning, and repository management.

The module leverages utility functions from java_mcp.git.utility to perform git operations
and provides comprehensive logging and error handling for repository management workflows.

Classes:
    GitRepoIndexer: Main class for managing multiple git repositories with validation and indexing

Dependencies:
    - GitPython: For git repository operations
    - java_mcp.git.utility: For git utility functions

Author: Rubens Gomes
License: Apache-2.0
Version: 1.0.0
"""

import logging
from typing import List
from git import Repo, GitCommandError, InvalidGitRepositoryError

from java_mcp.git.utility import (create_folder, is_valid_git_url,
                                  ping_git_repository, clone_or_update)

# Configure logging for the module
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class GitRepoIndexer:
    """
    A class for managing and indexing multiple git repositories.

    This class provides a unified interface for handling multiple git repositories,
    including validation, cloning, and indexing. It ensures all provided repository
    URLs are valid and accessible before attempting to clone them locally.

    Attributes:
        repo_urls (List[str]): List of git repository URLs to manage
        folder_path (str): Base path where repositories will be cloned
        local_repos (List[Repo]): List of successfully cloned GitPython Repo objects
    """

    def __init__(self, repo_urls: List[str], folder_path: str):
        """
        Initialize GitRepoIndexer with repository URLs and target folder path.

        This constructor performs comprehensive validation and setup of multiple
        shallow local git repositories. It validates all repository URLs, checks their
        accessibility, creates the target folder structure, and clones all repositories
        to the specified location.

        The initialization process includes:
        1. Validation of all repository URLs for format correctness
        2. Accessibility check for each repository using ping_git_repository
        3. Creation of the target folder structure
        4. Cloning or updating each repository to the local folder

        Args:
            repo_urls (List[str]): A list of git repository URLs to manage. Each URL
                                  must be a valid git repository URL (ending with .git
                                  and using supported protocols: http://, https://,
                                  git@, or ssh://).
            folder_path (str): The base path where all repositories will be cloned.
                              Must be a non-empty string. Individual repositories will
                              be created in subdirectories named after each repository.

        Raises:
            InvalidGitRepositoryError: If any repository URL is invalid or malformed
            GitCommandError: If any repository is not accessible or clone operation fails
            ValueError: If folder_path is invalid or empty
            OSError: If the folder structure cannot be created due to permissions

        Example:
            >>> urls = [
            ...     "https://github.com/user/repo1.git",
            ...     "https://github.com/user/repo2.git"
            ... ]
            >>> indexer = GitRepoIndexer(urls, "/path/to/repos")
            # Creates /path/to/repos/repo1 and /path/to/repos/repo2

            >>> repos = indexer.get_local_repos()
            >>> print(f"Managed {len(repos)} repositories")
            Managed 2 repositories

        Note:
            All repositories are cloned with shallow cloning (depth=1) for efficiency.
            If a repository already exists and matches the URL, it will be updated
            instead of re-cloned. The constructor will fail fast if any repository
            URL is invalid or inaccessible.
        """
        logger.info(f"Initializing GitRepoIndexer with {len(repo_urls)} repository URLs")
        logger.debug(f"Repository URLs: {repo_urls}")
        logger.debug(f"folder path: {folder_path}")

        self.repo_urls = repo_urls
        self.folder_path = folder_path
        self.local_repos: List[Repo] = []

        # Ensures that the provided URLs correspond to valid git repositories
        for i, url in enumerate(repo_urls, 1):
            logger.debug(f"Validating repository {i}/{len(repo_urls)}: {url}")

            if not is_valid_git_url(url):
                logger.error(f"URL is not valid: {url}")
                raise InvalidGitRepositoryError(f"URL is not valid: {url}")

            if not ping_git_repository(url):
                logger.error(f"Git repository is not accessible: {url}")
                raise GitCommandError(f"Git repository is not accessible: {url}")

        # Ensures a folder path exists to store local Git repositories
        logger.debug(f"Ensuring folder path exists: {self.folder_path}")
        create_folder(self.folder_path)
        logger.info(f"Folder path verified to exist: {self.folder_path}")

        # Ensures that the provided Git repository URLs are cloned locally
        for i, url in enumerate(repo_urls, 1):
            logger.debug(f"Fetching remote repository {i}/{len(repo_urls)}: {url}")
            repo = clone_or_update(self.folder_path, url, 1)
            self.local_repos.append(repo)
            logger.info(f"Git repository {url} successfully shallow cloned to {self.folder_path}")

        logger.info(f"GitRepoIndexer initialized with {len(self.local_repos)} repositories in {self.folder_path} ")

    def get_local_repos(self) -> List[Repo]:
        """
        Get the list of "shallow" local Git repositories.  That is only the latest
        commit from the default branch in the remote Git repository is fetched.

        This method returns all successfully locally cloned Git repositories
        as GitPython Repo objects. These can be used for further git operations
        such as reading files, examining commit history, or performing additional
        git commands.

        Returns:
            List[Repo]: A list of GitPython Repo objects representing the "shallow" cloned
                       repositories. The order matches the order of repository URLs
                       provided during initialization.

        Example:
            >>> indexer = GitRepoIndexer(urls, "/path/to/repos")
            >>> repos = indexer.get_local_repos()
            >>> for repo in repos:
            ...     print(f"Repository: {repo.working_dir}")
            ...     print(f"Current branch: {repo.active_branch}")
        """
        return self.local_repos

    @staticmethod
    def get_remote_url(repo: Repo) -> str:
        """
        Get the remote origin URL from a Git repository.

        This static method extracts the remote origin URL from a GitPython Repo object.
        It validates the repository parameter, checks for the existence of remote origins,
        and returns the URL of the 'origin' remote if available.

        The method is commonly used to identify which remote repository a local clone
        corresponds to, which is useful for validation, logging, and repository management
        operations.

        Args:
            repo (Repo): A GitPython Repo object representing a local Git repository.
                        Must be a valid, non-None Repo instance with potential remote origins.

        Returns:
            str: The URL of the 'origin' remote if it exists, None otherwise.
                 The URL format depends on the remote configuration (HTTPS, SSH, etc.).

        Raises:
            ValueError: If the repo parameter is None or falsy.

        Example:
            >>> from git import Repo
            >>> repo = Repo("/path/to/local/repository")
            >>> url = GitRepoIndexer.get_remote_url(repo)
            >>> print(f"Remote URL: {url}")
            Remote URL: https://github.com/user/repository.git

            >>> # Handle case where no origin exists
            >>> repo_no_origin = Repo("/path/to/local/only/repo")
            >>> url = GitRepoIndexer.get_remote_url(repo_no_origin)
            >>> print(f"Remote URL: {url}")
            Remote URL: None

        Note:
            This method specifically looks for a remote named 'origin'. If the repository
            has other remotes but no 'origin' remote, None will be returned. The method
            does not raise an exception for repositories without remotes, but rather
            returns None to allow for graceful handling of local-only repositories.
        """
        if not repo:
            error_msg = "repo must be provided"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.debug(f"Fetching remote Git repository URL for: {repo.working_dir}")
        origin_url = None

        if repo.remotes and 'origin' in [r.name for r in repo.remotes]:
            origin_url = repo.remotes.origin.url
            logger.debug(f"Origin URL: {origin_url}")

        return origin_url
