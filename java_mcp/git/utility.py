"""
Git Utility Functions Module for Java MCP Server

This module provides a comprehensive set of utility functions for git repository management
including cloning, updating, validating, and accessing git repositories. It serves as the
core utility layer for git operations within the Java MCP Server architecture.

The module uses the GitPython library to perform git operations and includes comprehensive
logging, error handling, and input validation. All functions are designed to be robust,
with proper error handling and detailed logging for debugging and monitoring purposes.

Key Features:
- Clone git repositories with shallow cloning (depth=1) for efficiency
- Update existing repositories by pulling latest changes from remote
- Validate git URLs and repository states with comprehensive checks
- Check repository accessibility without full cloning using git ls-remote
- Automatic folder creation and path management with cross-platform support
- Comprehensive logging for all operations with configurable log levels
- Input validation for all parameters with detailed error messages
- Repository state validation and URL matching capabilities

Core Functions:
- clone_or_update(): Unified interface for cloning new or updating existing repositories
- update(): Update an existing repository with latest changes from remote origin
- is_valid_git_url(): Validate git repository URLs for format and protocol compliance
- is_git_repo(): Check if a folder contains a valid git repository
- is_valid_git_repo(): Validate repository exists and matches expected remote URL
- git_folder_name(): Generate repository folder paths from repository URLs
- ping_git_repository(): Check repository accessibility without cloning
- create_folder(): Create directory structures recursively with proper error handling

Private Functions:
- _validate_inputs(): Internal input validation for folder paths and repository URLs

Supported Git Protocols:
- HTTP/HTTPS: http://, https:// (for public and authenticated repositories)
- SSH: git@hostname:user/repo.git (for SSH key-based authentication)
- SSH explicit: ssh://git@hostname/user/repo.git (alternative SSH format)

Error Handling:
All functions include comprehensive error handling with specific exception types:
- ValueError: For invalid input parameters
- GitCommandError: For git operation failures
- InvalidGitRepositoryError: For repository validation failures
- OSError: For file system operation failures

Dependencies:
- GitPython: For git repository operations and command execution
- pathlib: For cross-platform path handling and manipulation
- logging: For comprehensive operation logging and debugging

Usage Patterns:
This module is designed to be used by higher-level components like GitRepoIndexer
for batch operations, or directly for individual repository management tasks.

Author: Rubens Gomes
License: Apache-2.0
Version: 1.1.0
Last Updated: August 2025
"""

import logging
from pathlib import Path

from git import Repo, GitCommandError, InvalidGitRepositoryError
from git.cmd import Git

# Configure logging for the module
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def _validate_inputs(folder_path: str, repository_url: str) -> None:
    """
    Validate the input parameters for git operations.

    This function performs comprehensive validation of the folder path and repository URL
    parameters that are commonly used across git operations. It ensures that both parameters
    are provided and that the repository URL follows the expected git URL format.

    Args:
        folder_path (str): The path to the folder where git operations will be performed.
                          Must be a non-empty string.
        repository_url (str): The URL of the git repository. Must be a non-empty string
                             and follow valid git URL format (ending with .git and using
                             supported protocols: http://, https://, git@, or ssh://).

    Returns:
        None: This function does not return a value. It either completes successfully
              or raises an exception for invalid inputs.

    Raises:
        ValueError: If folder_path is None, empty, or whitespace-only
        ValueError: If repository_url is None, empty, or whitespace-only
        ValueError: If repository_url does not follow valid git URL format

    Example:
        >>> _validate_inputs("/path/to/folder", "https://github.com/user/repo.git")
        # Completes successfully for valid inputs

        >>> _validate_inputs("", "https://github.com/user/repo.git")
        ValueError: folder_path must be provided

        >>> _validate_inputs("/path/to/folder", "https://github.com/user/repo")
        ValueError: repository_url is not valid
    """
    if not folder_path:
        error_msg = "folder_path must be provided"
        logger.error(error_msg)
        raise ValueError(error_msg)

    if not repository_url:
        error_msg = "repository_url must be provided"
        logger.error(error_msg)
        raise ValueError(error_msg)

    if not is_valid_git_url(repository_url):
        error_msg = "repository_url is not valid"
        logger.error(error_msg)
        raise ValueError(error_msg)


def create_folder(folder_path: str) -> None:
    """
    Create the specified folder path if it does not exist.

    This utility function creates a directory structure recursively, ensuring that all
    parent directories are created as needed. If the folder already exists, no action
    is taken and no error is raised. This function is used internally to ensure that
    target directories exist before performing git operations.

    Args:
        folder_path (str): The path to the folder to create. Can be an absolute or
                          relative path. All parent directories will be created if
                          they don't exist.

    Returns:
        None: This function does not return a value. It either completes successfully
              after creating the folder structure or logs the successful creation.

    Raises:
        OSError: If the folder cannot be created due to permissions or other system issues
        TypeError: If folder_path is not a string

    Example:
        >>> create_folder("/path/to/new/directory")
        # Creates the entire directory structure if it doesn't exist

        >>> create_folder("relative/path/to/dir")
        # Creates relative directory structure from current working directory

    Note:
        This function uses Path.mkdir(parents=True, exist_ok=True) which means:
        - parents=True: Creates parent directories as needed
        - exist_ok=True: Does not raise an error if the directory already exists
    """
    logger.debug("Creating folder: %s", folder_path)
    Path(folder_path).mkdir(parents=True, exist_ok=True)
    logger.info("Folder created successfully: %s", folder_path)


def is_git_repo(folder_path: str) -> bool:
    """
    Check if the specified folder path is a valid git repository.

    This function determines if a given folder contains a git repository by
    checking for the existence of the folder and the presence of a .git
    subdirectory. It resolves the path to handle relative paths correctly.

    Args:
        folder_path (str): The path to the folder to check. Can be an absolute
                          or relative path.

    Returns:
        bool: True if the folder exists and contains a .git subdirectory,
              False otherwise.

    Example:
        >>> is_git_repo("/path/to/existing/repo")
        True  # If /path/to/existing/repo/.git exists

        >>> is_git_repo("/path/to/regular/folder")
        False  # If folder exists but no .git subdirectory

        >>> is_git_repo("/path/to/nonexistent")
        False  # If folder doesn't exist

    Note:
        This function only checks for the presence of a .git directory and
        does not validate the integrity or state of the git repository.
    """
    logger.debug("Checking if folder is a valid git repository: %s", folder_path)
    target_path = Path(folder_path).resolve()
    is_valid = target_path.exists() and (target_path / '.git').exists()

    if is_valid:
        logger.debug("Valid git repository found at: %s", folder_path)
    else:
        logger.debug("No git repository found at: %s", folder_path)

    return is_valid


def is_valid_git_url(url: str) -> bool:
    """
    Check if the provided URL is a valid git repository URL.

    This function validates git repository URLs by checking for supported protocols
    and ensuring the URL ends with the .git extension. It supports common git
    protocols used for repository access.

    Supported protocols:
    - http:// and https:// for HTTP/HTTPS access
    - git@ for SSH access (e.g., git@github.com:user/repo.git)
    - ssh:// for explicit SSH protocol

    Args:
        url (str): The URL to validate. Must be a non-empty string.

    Returns:
        bool: True if the URL is a valid git repository URL with supported
              protocol and .git extension, False otherwise.

    Example:
        >>> is_valid_git_url("https://github.com/user/repo.git")
        True

        >>> is_valid_git_url("git@github.com:user/repo.git")
        True

        >>> is_valid_git_url("https://github.com/user/repo")
        False  # Missing .git extension

        >>> is_valid_git_url("ftp://example.com/repo.git")
        False  # Unsupported protocol

    Note:
        This function only validates the URL format and does not check if the
        repository actually exists or is accessible.
    """
    logger.debug("Validating git URL: %s", url)

    # Handle None or non-string input
    if not url or not isinstance(url, str):
        logger.warning("Git URL is invalid: %s", url)
        return False

    # Check if URL has valid protocol and ends with .git
    valid_protocols = url.startswith("http://") or url.startswith("https://") or url.startswith(
        "git@") or url.startswith("ssh://")
    ends_with_git = url.endswith(".git")
    is_valid = valid_protocols and ends_with_git

    if is_valid:
        logger.debug("Git URL is valid: %s", url)
    else:
        logger.warning("Git URL is invalid: %s", url)

    return is_valid


def is_valid_git_repo(folder_path: str, repository_url: str) -> bool:
    """
    Check if the specified folder path is a valid git repository and matches the given URL.

    This function performs a two-step validation: first checking if the folder
    contains a git repository, then verifying that the repository's remote
    origin URL matches the provided repository URL.

    Args:
        folder_path (str): The path to the folder to check
        repository_url (str): The URL of the git repository to match against
                             the repository's remote origin URL

    Returns:
        bool: True if the folder is a valid git repository and its remote
              origin URL matches the provided URL, False otherwise.

    Example:
        >>> is_valid_git_repo("/path/to/repo", "https://github.com/user/repo.git")
        True  # If repo exists and remote URL matches

        >>> is_valid_git_repo("/path/to/repo", "https://github.com/user/other.git")
        False  # If repo exists but remote URL doesn't match

        >>> is_valid_git_repo("/path/to/folder", "https://github.com/user/repo.git")
        False  # If folder is not a git repository

    Note:
        This function requires that the repository has a remote named 'origin'.
        If no origin remote exists, it will raise an exception.
    """
    logger.debug("Validating git repository at %s against URL: %s", folder_path, repository_url)
    if not is_git_repo(folder_path):
        logger.debug("Folder %s is not a git repository", folder_path)
        return False

    repo = Repo(folder_path)
    matches = repo.remotes.origin.url == repository_url

    if matches:
        logger.debug("Git repository at %s matches the URL: %s", folder_path, repository_url)
    else:
        logger.debug("Git repository at %s does not match the URL: %s", folder_path, repository_url)

    return matches


def git_folder_name(folder_path: str, repository_url: str) -> str:
    """
    Generate a folder name for the git repository based on the repository URL.

    This function extracts the repository name from the git URL and combines it
    with the base folder path to create the full target path where the repository
    should be cloned or located. The repository name is derived by taking the
    last segment of the URL and removing the .git extension.

    Args:
        folder_path (str): The base path where the repository should be located.
                          Must be a valid, non-empty string.
        repository_url (str): The URL of the git repository. Must be a valid git
                             URL format as validated by _validate_inputs.

    Returns:
        str: The full path where the repository should be cloned, consisting of
             the folder_path joined with the repository name.

    Raises:
        ValueError: If folder_path or repository_url is invalid (raised by _validate_inputs)

    Example:
        >>> git_folder_name("/repos", "https://github.com/user/myproject.git")
        "/repos/myproject"

        >>> git_folder_name("~/code", "git@github.com:user/awesome-lib.git")
        "~/code/awesome-lib"

    Note:
        This function automatically extracts the repository name by removing the
        .git extension from the URL. It validates inputs before processing and
        uses pathlib.Path for proper path construction across different operating systems.
    """
    _validate_inputs(folder_path, repository_url)
    logger.debug("Generating git folder path for URL: %s in base path: %s",
                 repository_url, folder_path)
    # Extract repository name from URL (remove .git extension)
    repo_name = repository_url.split('/')[-1].replace('.git', '')
    full_path = str(Path(folder_path) / repo_name)
    logger.debug("Generated git folder path: %s", full_path)
    return full_path


def update(folder_path: str, repository_url: str) -> Repo:
    """
    Update an existing git repository by pulling the latest changes from the remote.

    This function validates the input parameters, constructs the target git folder path,
    opens the existing git repository, validates that the remote URL matches the expected
    repository URL, and then performs a git pull to update the repository with the latest
    changes from the remote origin.

    Args:
        folder_path (str): The base path where the repository is located.
                          Must be a non-empty string.
        repository_url (str): The URL of the git repository to update. Must be a non-empty
                             string and follow valid git URL format (ending with .git and
                             using supported protocols: http://, https://, git@, or ssh://).

    Returns:
        Repo: The updated local Git repository

    Raises:
        ValueError: If folder_path or repository_url is invalid (raised by _validate_inputs)
        GitError: If the repository cannot be opened or accessed
        Exception: If the existing repository has a different remote URL than expected
        GitCommandError: If the git pull operation fails

    Example:
        >>> repo = update("/path/to/repos", "https://github.com/user/repo.git")
        # Successfully pulls latest changes if repository exists and URL matches

        >>> repo = update("/path/to/repos", "https://github.com/user/different.git")
        Exception: Repository at /path/to/repos/different has different remote URL...

    Note:
        This function assumes that the repository already exists at the computed target
        path. It will not create or clone a new repository - use the clone() function
        for that purpose. The target repository path is computed by combining the
        folder_path with the repository name extracted from the repository_url.
    """
    _validate_inputs(folder_path, repository_url)
    target_git_folder = git_folder_name(folder_path, repository_url)
    logger.debug("Target git folder resolved to: %s", target_git_folder)
    # Convert to Path object for better path handling
    target_git_path = Path(target_git_folder)

    # Open existing repository
    repo = Repo(target_git_path)
    logger.debug("Successfully opened existing repository")

    # Check if the remote URL matches the requested repository_url
    if repo.remotes.origin.url == repository_url:
        logger.info("Repository already exists at %s. Pulling latest changes...", target_git_path)
        # Pull latest changes from the remote repository
        repo.remotes.origin.pull()
        logger.info("Successfully pulled latest changes from remote repository")
    else:
        error_msg = (f"Repository at {target_git_folder} has different remote "
                     f"URL: {repo.remotes.origin.url}. Expected: {repository_url}")
        raise InvalidGitRepositoryError(error_msg)

    # returns an updated local repository
    return repo


def clone_or_update(folder_path: str, repository_url: str) -> Repo:
    """
    Clone a git repository or update it if it already exists at the specified folder path.

    This function provides a unified interface for both cloning new repositories and updating
    existing ones. It validates the input parameters, ensures the target folder exists,
    and then either clones a new repository or updates an existing one based on whether
    a git repository already exists at the computed target path.

    The function will:
    1. Validate input parameters and create the base folder if needed
    2. Compute the target git folder path based on the repository URL
    3. If a git repository already exists and matches the URL, perform a git pull
    4. If no repository exists, clone the repository with shallow clone (depth=1)
    5. If a repository exists but has a different remote URL, raise an exception

    Args:
        folder_path (str): The base path where the repository should be located or cloned.
                          Must be a non-empty string. The actual repository will be created
                          in a subdirectory named after the repository.
        repository_url (str): The URL of the git repository to clone or update. Must be a
                             non-empty string and follow valid git URL format (ending with
                             .git and using supported protocols: http://, https://, git@, ssh://).

    Returns:
        Repo: The cloned or updated local Git repository

    Raises:
        ValueError: If folder_path or repository_url is invalid (raised by _validate_inputs)
        GitError: If the repository cannot be opened, accessed, or cloned
        Exception: If an existing repository has a different remote URL than expected
        GitCommandError: If git operations (clone or pull) fail

    Example:
        >>> repo = clone_or_update("/path/to/repos", "https://github.com/user/repo.git")
        # If /path/to/repos/repo doesn't exist, clones the repository there
        # If /path/to/repos/repo exists and matches URL, pulls latest changes

        >>> repo = clone_or_update("/path/to/repos", "https://github.com/user/different.git")
        # Creates /path/to/repos/different if it doesn't exist

        >>> repo = clone_or_update("/path/to/repos", "https://github.com/user/wrong.git")
        # Raises Exception if /path/to/repos/wrong exists but has different remote URL

    Note:
        The target repository path is automatically computed by combining the folder_path
        with the repository name extracted from the repository_url (without .git extension).
        This function uses shallow cloning (depth=1) for new repositories to save bandwidth
        and storage space.
    """
    logger.info("Starting clone operation for repository: %s to path: %s",
                repository_url, folder_path)
    # validate function parameters
    _validate_inputs(folder_path, repository_url)
    # ensure the target folder exists
    create_folder(folder_path)
    # check if a git folder already exists for the given repo URL
    target_git_folder = git_folder_name(folder_path, repository_url)
    logger.debug("Resolved target git folder: %s", target_git_folder)

    # the local Git repository cloned or updated
    repo: Repo

    if is_git_repo(target_git_folder):
        logger.info("Repository already exists at %s", target_git_folder)

        if is_valid_git_repo(target_git_folder, repository_url):
            logger.info("Existing repository at %s matches the provided URL. "
                        "Pulling latest changes...", target_git_folder)
            repo = Repo(target_git_folder)
            repo.remotes.origin.pull()
            logger.info("Successfully pulled latest changes from remote repository")
        else:
            error_msg = (f"Existing repository at {target_git_folder} does not match "
                         f"the provided URL: {repository_url}")
            logger.error(error_msg)
            raise InvalidGitRepositoryError(error_msg)

    else:
        # Convert to Path object for better path handling
        target_path = Path(folder_path)
        # Clone repository using GitPython with shallow clone (depth 1)
        logger.info("Cloning repository %s to %s...", repository_url, target_path)
        repo = Repo.clone_from(repository_url, target_path, depth=1)
        logger.info("Successfully cloned repository to %s", target_path)

    return repo


def ping_git_repository(repository_url: str) -> bool:
    """
    Quickly check if a git repository URL is accessible without cloning.

    This function performs a lightweight accessibility check for git repositories
    using the git ls-remote command. It's much faster than cloning and doesn't
    require local storage, making it ideal for validation purposes before
    attempting expensive clone operations.

    The function uses the git ls-remote --exit-code command which:
    - Returns exit code 0 if the repository exists and is accessible
    - Returns exit code 2 if the repository doesn't exist or has no refs
    - Throws GitCommandError for authentication or network issues

    Args:
        repository_url (str): The git repository URL to check. Should be a valid
                             git URL format (http://, https://, git@, or ssh://).

    Returns:
        bool: True if the repository is accessible and contains refs,
              False if the repository is inaccessible, doesn't exist,
              or if any error occurs during the check.

    Example:
        >>> ping_git_repository("https://github.com/octocat/Hello-World.git")
        True  # Public repository is accessible

        >>> ping_git_repository("https://github.com/nonexistent/repo.git")
        False  # Repository doesn't exist

        >>> ping_git_repository("https://private-git.company.com/secret/repo.git")
        False  # May fail due to authentication requirements

    Note:
        This function is designed to fail gracefully. Any exception during
        the git ls-remote operation will result in False being returned.
        For private repositories, this function may return False even if
        the repository exists but requires authentication.
    """
    try:
        git = Git()
        # ls-remote with --exit-code returns 0 if refs exist, 2 if not
        git.ls_remote("--exit-code", repository_url)
        logger.debug(f"Repository is accessible: {repository_url}")
        return True
    except GitCommandError as e:
        logger.warning(f"Repository not accessible: {repository_url} - {e}")
        return False
    except Exception as e:
        logger.error(f"Error checking repository: {repository_url} - {e}")
        return False
