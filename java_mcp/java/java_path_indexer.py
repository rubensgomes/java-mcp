"""
Java Path Indexer Module for Java MCP Server

This module provides the JavaPathIndexer class for discovering and indexing Java source files
within Git repositories. It serves as a bridge between Git repository management and Java
source code analysis by locating all Java files in standard Maven/Gradle project structures.

The module focuses on finding Java source files in the conventional 'src/main/java' directory
structure and provides efficient path management for subsequent Java code analysis operations.

Key Features:
- Automatic discovery of Java files in Maven/Gradle project structures
- Validation of Git repositories for Java content
- Path indexing with comprehensive logging
- Support for multiple repositories in a single indexer
- Standard Java project structure validation (src/main/java)

Classes:
    JavaPathIndexer: Main class for indexing Java file paths from Git repositories

Dependencies:
    - GitPython: For Git repository operations
    - pathlib: For cross-platform path handling
    - java_mcp.git.git_repo_indexer: For Git repository management

Author: Rubens Gomes
License: Apache-2.0
Version: 1.0.0
"""

import logging
from pathlib import Path
from typing import List

from git import Repo

from java_mcp.git.git_repo_indexer import GitRepoIndexer

# Configure logging for the module
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class JavaPathIndexer:
    """
    A class for indexing Java source file paths from Git repositories.

    This class processes Git repositories to discover and index Java source files
    following standard Maven/Gradle project structures. It validates repositories,
    ensures they contain Java projects, and collects all Java file paths for
    subsequent analysis operations.

    The indexer expects repositories to follow the standard Java project structure:
    - Repository root/
      - src/
        - main/
          - java/  <- Java source files are expected here

    Attributes:
        java_paths (List[Path]): List of Path objects pointing to discovered Java files
    """

    def __init__(self, local_repos: List[Repo]):
        """
        Initialize JavaPathIndexer with local Git repositories.

        This constructor processes multiple Git repositories to discover and index
        Java source files. It validates each repository, ensures they contain valid
        Java project structures, and recursively finds all Java files within the
        standard Maven/Gradle source directory (src/main/java).

        The initialization process includes:
        1. Validation of Git repositories (non-bare, accessible)
        2. Remote URL verification for each repository
        3. Java project structure validation (src/main/java directory exists)
        4. Recursive discovery of all .java files
        5. Path indexing and logging

        Args:
            local_repos (List[Repo]): A list of GitPython Repo objects representing
                                     local Git repositories to process. Each repository
                                     must be non-bare and contain a standard Java project
                                     structure with src/main/java directory.

        Raises:
            ValueError: If any repository is bare or if remote URL cannot be retrieved
            FileNotFoundError: If the src/main/java directory is not found in any repository

        Example:
            >>> from java_mcp.git.git_repo_indexer import GitRepoIndexer
            >>> git_indexer = GitRepoIndexer(repo_urls, "/local/repos")
            >>> local_repos = git_indexer.get_local_repos()
            >>> java_indexer = JavaPathIndexer(local_repos)
            >>> print(f"Found {len(java_indexer.java_paths)} Java files")

        Note:
            The indexer expects standard Maven/Gradle project structure. Repositories
            with non-standard structures or missing src/main/java directories will
            cause initialization to fail. All Java files are discovered recursively,
            including those in nested package directories.
        """
        logger.info(f"Initializing JavaPathIndexer with {len(local_repos)} local Git repositories")
        logger.debug(f"Git local repositories: {local_repos}")

        self.java_paths: List[Path] = []

        for i, local_repo in enumerate(local_repos, 1):
            logger.debug(f"Validating repository {i}/{len(local_repos)}: {local_repo}")

            # Ensures that the provided repos correspond to valid local git repositories
            if local_repo.bare:
                error_msg = f"Repository is bare or not local, and cannot be processed: {local_repo}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            remote_url = GitRepoIndexer.get_remote_url(local_repo)

            if not remote_url:
                error_msg = f"Could not retrieve the remote URL from repo: {local_repo}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Construct the path to the Java source directory
            repo_path = Path(local_repo.working_dir)
            java_src_path = repo_path / "src" / "main" / "java"

            # Ensure Java source directory (src/main/java) exists
            if not java_src_path.is_dir():
                error_msg = (f"No Java source directory (src/main/java) found in:"
                             f" {repo_path} with remote url {remote_url}")
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)

            # Find all .java file paths within java_src_path
            self.java_paths = list(java_src_path.rglob("*.java"))
            logger.info(f"Found {len(self.java_paths)} Java files in {java_src_path}")

    def get_java_paths(self) -> List[Path]:
        """
        Get the list of Java file paths found in the local Git repositories.

        This method returns all discovered Java file paths as pathlib Path objects.
        These can be used for further processing, such as parsing or indexing.

        Returns:
            List[Path]: A list of pathlib Path objects representing the Java files.
                        The order matches the order of repositories provided during
                        initialization.

        Example:
            >>> indexer = JavaPathIndexer(local_repos)
            >>> java_files = indexer.get_java_paths()
            >>> for java_file in java_files:
            ...     print(f"Java file: {java_file}")
        """
        return self.java_paths

