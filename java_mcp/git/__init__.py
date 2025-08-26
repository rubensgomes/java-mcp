"""
Git Operations Package for Java MCP Server

This package provides comprehensive git repository management capabilities for the Java MCP Server.
It includes utilities for cloning, updating, validating git repositories, and managing multiple
repositories through a centralized indexer.

The package is organized into two main modules:
- utility: Core git utility functions for individual repository operations
- git_repo_indexer: High-level class for managing multiple repositories

Key Features:
- Repository cloning with shallow clone optimization (depth=1)
- Repository updates with conflict detection and resolution
- Git URL validation with protocol support (HTTP/HTTPS/SSH)
- Repository accessibility checking without full cloning
- Batch repository management through GitRepoIndexer
- Comprehensive logging and error handling
- Cross-platform path handling and folder management
- Input validation and sanitization

Modules:
    utility: Core git utility functions including clone_or_update, validation, and repository checks
    git_repo_indexer: GitRepoIndexer class for managing multiple repositories with validation

Classes:
    GitRepoIndexer: Main class for batch repository management and indexing

Functions:
    clone_or_update(): Clone new or update existing repositories
    update(): Pull latest changes from remote repository
    is_valid_git_url(): Validate git repository URL format
    is_git_repo(): Check if folder contains a git repository
    is_valid_git_repo(): Validate repository and match against expected URL
    git_folder_name(): Generate repository folder paths from URLs
    ping_git_repository(): Check repository accessibility without cloning
    create_folder(): Create directory structures recursively

Usage:
    # Import the main components
    from java_mcp.git import GitRepoIndexer
    from java_mcp.git.utility import clone_or_update, is_valid_git_url

    # Use GitRepoIndexer for multiple repositories
    repos = ["https://github.com/user/repo1.git", "https://github.com/user/repo2.git"]
    indexer = GitRepoIndexer(repos, "/path/to/local/repos")

    # Use utility functions for individual operations
    repo = clone_or_update("/path/to/repos", "https://github.com/user/repo.git")
    is_valid = is_valid_git_url("https://github.com/user/repo.git")

Dependencies:
    - GitPython: For git repository operations
    - pathlib: For cross-platform path handling
    - logging: For operation logging and debugging

Author: Rubens Gomes
License: Apache-2.0
Version: 1.0.0
Package: java_mcp.git
"""

# Import main classes and functions for easy access
from .git_repo_indexer import GitRepoIndexer
from .utility import (
    clone_or_update,
    update,
    is_valid_git_url,
    is_git_repo,
    is_valid_git_repo,
    git_folder_name,
    ping_git_repository,
    create_folder
)

# Define what gets exported when using "from java_mcp.git import *"
__all__ = [
    # Main class
    'GitRepoIndexer',

    # Core git operations
    'clone_or_update',
    'update',

    # Validation functions
    'is_valid_git_url',
    'is_git_repo',
    'is_valid_git_repo',
    'ping_git_repository',

    # Utility functions
    'git_folder_name',
    'create_folder'
]

# Package metadata
__version__ = '1.0.0'
__author__ = 'Rubens Gomes'
__license__ = 'Apache-2.0'
__package_name__ = 'java_mcp.git'

# Module-level logging configuration
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Initialized {__package_name__} package version {__version__}")
