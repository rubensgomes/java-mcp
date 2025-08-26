"""
Unit tests for the java_mcp.git.git_repo_indexer module.

This test suite provides comprehensive coverage for the GitRepoIndexer class including
initialization, validation, repository management, and error handling scenarios.
All external dependencies are properly mocked to ensure isolated testing.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from git import Repo, GitCommandError, InvalidGitRepositoryError

from java_mcp.git.git_repo_indexer import GitRepoIndexer


class TestGitRepoIndexerInit:
    """Test cases for GitRepoIndexer.__init__ method."""

    @patch('java_mcp.git.git_repo_indexer.create_folder')
    @patch('java_mcp.git.git_repo_indexer.is_valid_git_url')
    @patch('java_mcp.git.git_repo_indexer.ping_git_repository')
    @patch('java_mcp.git.git_repo_indexer.clone_or_update')
    def test_successful_initialization_single_repo(self, mock_clone, mock_ping, mock_valid_url, mock_create):
        """Test successful initialization with a single repository."""
        # Setup mocks
        mock_valid_url.return_value = True
        mock_ping.return_value = True
        mock_repo = MagicMock(spec=Repo)
        mock_clone.return_value = mock_repo

        # Test data
        repo_urls = ["https://github.com/user/repo.git"]
        folder_path = "/test/repos"

        # Execute
        indexer = GitRepoIndexer(repo_urls, folder_path)

        # Verify attributes
        assert indexer.repo_urls == repo_urls
        assert indexer.folder_path == folder_path
        assert len(indexer.local_repos) == 1
        assert indexer.local_repos[0] == mock_repo

        # Verify method calls
        mock_valid_url.assert_called_once_with("https://github.com/user/repo.git")
        mock_ping.assert_called_once_with("https://github.com/user/repo.git")
        mock_create.assert_called_once_with(folder_path)
        mock_clone.assert_called_once_with(folder_path, "https://github.com/user/repo.git", 1)

    @patch('java_mcp.git.git_repo_indexer.create_folder')
    @patch('java_mcp.git.git_repo_indexer.is_valid_git_url')
    @patch('java_mcp.git.git_repo_indexer.ping_git_repository')
    @patch('java_mcp.git.git_repo_indexer.clone_or_update')
    def test_successful_initialization_multiple_repos(self, mock_clone, mock_ping, mock_valid_url, mock_create):
        """Test successful initialization with multiple repositories."""
        # Setup mocks
        mock_valid_url.return_value = True
        mock_ping.return_value = True
        mock_repo1 = MagicMock(spec=Repo)
        mock_repo2 = MagicMock(spec=Repo)
        mock_repo3 = MagicMock(spec=Repo)
        mock_clone.side_effect = [mock_repo1, mock_repo2, mock_repo3]

        # Test data
        repo_urls = [
            "https://github.com/user/repo1.git",
            "https://github.com/user/repo2.git",
            "git@github.com:user/repo3.git"
        ]
        folder_path = "/test/repos"

        # Execute
        indexer = GitRepoIndexer(repo_urls, folder_path)

        # Verify attributes
        assert indexer.repo_urls == repo_urls
        assert indexer.folder_path == folder_path
        assert len(indexer.local_repos) == 3
        assert indexer.local_repos == [mock_repo1, mock_repo2, mock_repo3]

        # Verify validation calls
        expected_url_calls = [call(url) for url in repo_urls]
        mock_valid_url.assert_has_calls(expected_url_calls)
        mock_ping.assert_has_calls(expected_url_calls)

        # Verify clone calls - now include depth parameter
        expected_clone_calls = [call(folder_path, url, 1) for url in repo_urls]
        mock_clone.assert_has_calls(expected_clone_calls)

        # Verify folder creation called once
        mock_create.assert_called_once_with(folder_path)

    @patch('java_mcp.git.git_repo_indexer.is_valid_git_url')
    @patch('java_mcp.git.git_repo_indexer.ping_git_repository')
    def test_initialization_invalid_url_raises_error(self, mock_ping, mock_valid_url):
        """Test initialization with invalid URL raises InvalidGitRepositoryError."""
        mock_valid_url.side_effect = [True, False]  # First URL valid, second invalid
        mock_ping.return_value = True  # Add ping mock to prevent real network calls

        repo_urls = [
            "https://github.com/user/repo1.git",
            "invalid-url"
        ]
        folder_path = "/test/repos"

        with pytest.raises(InvalidGitRepositoryError, match="URL is not valid: invalid-url"):
            GitRepoIndexer(repo_urls, folder_path)

        # Verify validation was called for both URLs
        mock_valid_url.assert_has_calls([
            call("https://github.com/user/repo1.git"),
            call("invalid-url")
        ])

    @patch('java_mcp.git.git_repo_indexer.is_valid_git_url')
    @patch('java_mcp.git.git_repo_indexer.ping_git_repository')
    def test_initialization_inaccessible_repo_raises_error(self, mock_ping, mock_valid_url):
        """Test initialization with inaccessible repository raises GitCommandError."""
        mock_valid_url.return_value = True
        mock_ping.side_effect = [True, False]  # First repo accessible, second not

        repo_urls = [
            "https://github.com/user/repo1.git",
            "https://github.com/user/private-repo.git"
        ]
        folder_path = "/test/repos"

        with pytest.raises(GitCommandError, match="Git repository is not accessible: https://github.com/user/private-repo.git"):
            GitRepoIndexer(repo_urls, folder_path)

        # Verify ping was called for both URLs
        mock_ping.assert_has_calls([
            call("https://github.com/user/repo1.git"),
            call("https://github.com/user/private-repo.git")
        ])

    @patch('java_mcp.git.git_repo_indexer.create_folder')
    @patch('java_mcp.git.git_repo_indexer.is_valid_git_url')
    @patch('java_mcp.git.git_repo_indexer.ping_git_repository')
    def test_initialization_folder_creation_error(self, mock_ping, mock_valid_url, mock_create):
        """Test initialization with folder creation error."""
        mock_valid_url.return_value = True
        mock_ping.return_value = True
        mock_create.side_effect = OSError("Permission denied")

        repo_urls = ["https://github.com/user/repo.git"]
        folder_path = "/restricted/path"

        with pytest.raises(OSError, match="Permission denied"):
            GitRepoIndexer(repo_urls, folder_path)

    @patch('java_mcp.git.git_repo_indexer.create_folder')
    @patch('java_mcp.git.git_repo_indexer.is_valid_git_url')
    @patch('java_mcp.git.git_repo_indexer.ping_git_repository')
    @patch('java_mcp.git.git_repo_indexer.clone_or_update')
    def test_initialization_clone_error_during_processing(self, mock_clone, mock_ping, mock_valid_url, mock_create):
        """Test initialization with clone error during repository processing."""
        mock_valid_url.return_value = True
        mock_ping.return_value = True
        mock_repo1 = MagicMock(spec=Repo)
        mock_clone.side_effect = [mock_repo1, GitCommandError("Clone failed")]

        repo_urls = [
            "https://github.com/user/repo1.git",
            "https://github.com/user/repo2.git"
        ]
        folder_path = "/test/repos"

        with pytest.raises(GitCommandError, match="Clone failed"):
            GitRepoIndexer(repo_urls, folder_path)

        # Verify first repo was processed successfully before error
        assert mock_clone.call_count == 2

    def test_initialization_empty_repo_list(self):
        """Test initialization with empty repository list."""
        repo_urls = []
        folder_path = "/test/repos"

        with patch('java_mcp.git.git_repo_indexer.create_folder') as mock_create:
            indexer = GitRepoIndexer(repo_urls, folder_path)

            assert indexer.repo_urls == []
            assert indexer.folder_path == folder_path
            assert indexer.local_repos == []
            mock_create.assert_called_once_with(folder_path)

    @patch('java_mcp.git.git_repo_indexer.create_folder')
    @patch('java_mcp.git.git_repo_indexer.is_valid_git_url')
    @patch('java_mcp.git.git_repo_indexer.ping_git_repository')
    @patch('java_mcp.git.git_repo_indexer.clone_or_update')
    def test_initialization_maintains_repo_order(self, mock_clone, mock_ping, mock_valid_url, mock_create):
        """Test that initialization maintains the order of repositories."""
        mock_valid_url.return_value = True
        mock_ping.return_value = True

        # Create distinct mock repos to verify order - remove the name attribute test
        mock_repos = [MagicMock(spec=Repo) for i in range(5)]
        mock_clone.side_effect = mock_repos

        repo_urls = [f"https://github.com/user/repo{i}.git" for i in range(5)]
        folder_path = "/test/repos"

        indexer = GitRepoIndexer(repo_urls, folder_path)

        # Verify order is maintained by checking the exact mock objects
        assert indexer.local_repos == mock_repos
        assert len(indexer.local_repos) == 5

    @patch('java_mcp.git.git_repo_indexer.create_folder')
    @patch('java_mcp.git.git_repo_indexer.is_valid_git_url')
    @patch('java_mcp.git.git_repo_indexer.ping_git_repository')
    @patch('java_mcp.git.git_repo_indexer.clone_or_update')
    def test_initialization_with_different_url_formats(self, mock_clone, mock_ping, mock_valid_url, mock_create):
        """Test initialization with different git URL formats."""
        mock_valid_url.return_value = True
        mock_ping.return_value = True
        mock_repos = [MagicMock(spec=Repo) for _ in range(4)]
        mock_clone.side_effect = mock_repos

        repo_urls = [
            "https://github.com/user/repo1.git",
            "http://git.example.com/user/repo2.git",
            "git@github.com:user/repo3.git",
            "ssh://git@gitlab.com/user/repo4.git"
        ]
        folder_path = "/test/repos"

        indexer = GitRepoIndexer(repo_urls, folder_path)

        assert len(indexer.local_repos) == 4
        # Verify all URL formats were processed
        expected_calls = [call(url) for url in repo_urls]
        mock_valid_url.assert_has_calls(expected_calls)
        mock_ping.assert_has_calls(expected_calls)


class TestGitRepoIndexerGetRepos:
    """Test cases for GitRepoIndexer.get_repos method."""

    @patch('java_mcp.git.git_repo_indexer.create_folder')
    @patch('java_mcp.git.git_repo_indexer.is_valid_git_url')
    @patch('java_mcp.git.git_repo_indexer.ping_git_repository')
    @patch('java_mcp.git.git_repo_indexer.clone_or_update')
    def test_get_repos_returns_correct_list(self, mock_clone, mock_ping, mock_valid_url, mock_create):
        """Test that get_repos returns the correct list of repositories."""
        mock_valid_url.return_value = True
        mock_ping.return_value = True
        mock_repo1 = MagicMock(spec=Repo)
        mock_repo2 = MagicMock(spec=Repo)
        mock_clone.side_effect = [mock_repo1, mock_repo2]

        repo_urls = [
            "https://github.com/user/repo1.git",
            "https://github.com/user/repo2.git"
        ]
        folder_path = "/test/repos"

        indexer = GitRepoIndexer(repo_urls, folder_path)
        repos = indexer.get_local_repos()

        assert repos == [mock_repo1, mock_repo2]
        assert repos is indexer.local_repos  # Should return the same list object

    @patch('java_mcp.git.git_repo_indexer.create_folder')
    def test_get_repos_empty_list(self, mock_create):
        """Test get_repos with empty repository list."""
        indexer = GitRepoIndexer([], "/test/repos")
        repos = indexer.get_local_repos()

        assert repos == []
        assert isinstance(repos, list)

    @patch('java_mcp.git.git_repo_indexer.create_folder')
    @patch('java_mcp.git.git_repo_indexer.is_valid_git_url')
    @patch('java_mcp.git.git_repo_indexer.ping_git_repository')
    @patch('java_mcp.git.git_repo_indexer.clone_or_update')
    def test_get_repos_multiple_calls_same_result(self, mock_clone, mock_ping, mock_valid_url, mock_create):
        """Test that multiple calls to get_repos return the same result."""
        mock_valid_url.return_value = True
        mock_ping.return_value = True
        mock_repo = MagicMock(spec=Repo)
        mock_clone.return_value = mock_repo

        indexer = GitRepoIndexer(["https://github.com/user/repo.git"], "/test/repos")

        repos1 = indexer.get_local_repos()
        repos2 = indexer.get_local_repos()

        assert repos1 == repos2
        assert repos1 is repos2  # Should be the exact same object


class TestGitRepoIndexerIntegration:
    """Integration tests for GitRepoIndexer class."""

    @patch('java_mcp.git.git_repo_indexer.create_folder')
    @patch('java_mcp.git.git_repo_indexer.is_valid_git_url')
    @patch('java_mcp.git.git_repo_indexer.ping_git_repository')
    @patch('java_mcp.git.git_repo_indexer.clone_or_update')
    def test_full_workflow_success(self, mock_clone, mock_ping, mock_valid_url, mock_create):
        """Test complete workflow from initialization to repository access."""
        # Setup mocks
        mock_valid_url.return_value = True
        mock_ping.return_value = True
        mock_repos = [MagicMock(spec=Repo) for _ in range(3)]
        mock_clone.side_effect = mock_repos

        # Test complete workflow
        repo_urls = [
            "https://github.com/user/frontend.git",
            "https://github.com/user/backend.git",
            "git@github.com:user/shared.git"
        ]
        folder_path = "/projects"

        # Initialize indexer
        indexer = GitRepoIndexer(repo_urls, folder_path)

        # Verify initialization
        assert len(indexer.repo_urls) == 3
        assert indexer.folder_path == folder_path

        # Get repositories and verify
        repos = indexer.get_local_repos()
        assert len(repos) == 3
        assert all(isinstance(repo, MagicMock) for repo in repos)

        # Verify all validation steps were called
        assert mock_valid_url.call_count == 3
        assert mock_ping.call_count == 3
        assert mock_clone.call_count == 3
        mock_create.assert_called_once_with(folder_path)

    @patch('java_mcp.git.git_repo_indexer.create_folder')
    @patch('java_mcp.git.git_repo_indexer.is_valid_git_url')
    @patch('java_mcp.git.git_repo_indexer.ping_git_repository')
    @patch('java_mcp.git.git_repo_indexer.clone_or_update')
    def test_partial_failure_stops_processing(self, mock_clone, mock_ping, mock_valid_url, mock_create):
        """Test that failure during processing stops the entire operation."""
        mock_valid_url.side_effect = [True, True, False]  # Third URL is invalid
        mock_ping.return_value = True

        repo_urls = [
            "https://github.com/user/repo1.git",
            "https://github.com/user/repo2.git",
            "invalid-url"
        ]
        folder_path = "/test/repos"

        with pytest.raises(InvalidGitRepositoryError):
            GitRepoIndexer(repo_urls, folder_path)

        # Verify processing stopped at validation - clone should not be called
        mock_clone.assert_not_called()
        # Ping should only be called for the first two valid URLs
        assert mock_ping.call_count == 2

    @patch('java_mcp.git.git_repo_indexer.create_folder')
    @patch('java_mcp.git.git_repo_indexer.is_valid_git_url')
    @patch('java_mcp.git.git_repo_indexer.ping_git_repository')
    @patch('java_mcp.git.git_repo_indexer.clone_or_update')
    def test_error_after_successful_clones(self, mock_clone, mock_ping, mock_valid_url, mock_create):
        """Test error handling after some repositories are successfully cloned."""
        mock_valid_url.return_value = True
        mock_ping.return_value = True

        # First two clones succeed, third fails
        mock_repo1 = MagicMock(spec=Repo)
        mock_repo2 = MagicMock(spec=Repo)
        mock_clone.side_effect = [mock_repo1, mock_repo2, GitCommandError("Network error")]

        repo_urls = [
            "https://github.com/user/repo1.git",
            "https://github.com/user/repo2.git",
            "https://github.com/user/repo3.git"
        ]
        folder_path = "/test/repos"

        with pytest.raises(GitCommandError, match="Network error"):
            GitRepoIndexer(repo_urls, folder_path)

        # Verify that clone was attempted for all three repositories
        assert mock_clone.call_count == 3


class TestGitRepoIndexerEdgeCases:
    """Test edge cases and error conditions for GitRepoIndexer."""

    def test_initialization_with_none_repo_urls(self):
        """Test initialization with None repository URLs."""
        with pytest.raises(TypeError):
            GitRepoIndexer(None, "/test/repos")

    @patch('java_mcp.git.git_repo_indexer.is_valid_git_url')
    @patch('java_mcp.git.git_repo_indexer.ping_git_repository')
    def test_initialization_with_none_folder_path(self, mock_ping, mock_valid_url):
        """Test initialization with None folder path."""
        # Mock the dependencies to prevent real network calls
        mock_valid_url.return_value = True
        mock_ping.return_value = True

        # The actual error should come from trying to use None as folder_path
        # This will fail during attribute assignment or when create_folder is called
        with pytest.raises((TypeError, AttributeError)):
            GitRepoIndexer(["https://github.com/user/repo.git"], None)

    @patch('java_mcp.git.git_repo_indexer.create_folder')
    @patch('java_mcp.git.git_repo_indexer.is_valid_git_url')
    @patch('java_mcp.git.git_repo_indexer.ping_git_repository')
    @patch('java_mcp.git.git_repo_indexer.clone_or_update')
    def test_large_number_of_repositories(self, mock_clone, mock_ping, mock_valid_url, mock_create):
        """Test initialization with a large number of repositories."""
        mock_valid_url.return_value = True
        mock_ping.return_value = True

        # Create 50 mock repositories
        num_repos = 50
        mock_repos = [MagicMock(spec=Repo) for _ in range(num_repos)]
        mock_clone.side_effect = mock_repos

        repo_urls = [f"https://github.com/user/repo{i}.git" for i in range(num_repos)]
        folder_path = "/test/repos"

        indexer = GitRepoIndexer(repo_urls, folder_path)

        assert len(indexer.local_repos) == num_repos
        assert mock_valid_url.call_count == num_repos
        assert mock_ping.call_count == num_repos
        assert mock_clone.call_count == num_repos

    @patch('java_mcp.git.git_repo_indexer.create_folder')
    @patch('java_mcp.git.git_repo_indexer.is_valid_git_url')
    @patch('java_mcp.git.git_repo_indexer.ping_git_repository')
    @patch('java_mcp.git.git_repo_indexer.clone_or_update')
    def test_duplicate_repository_urls(self, mock_clone, mock_ping, mock_valid_url, mock_create):
        """Test initialization with duplicate repository URLs."""
        mock_valid_url.return_value = True
        mock_ping.return_value = True
        mock_repos = [MagicMock(spec=Repo) for _ in range(3)]
        mock_clone.side_effect = mock_repos

        # Same URL repeated
        repo_urls = [
            "https://github.com/user/repo.git",
            "https://github.com/user/repo.git",
            "https://github.com/user/repo.git"
        ]
        folder_path = "/test/repos"

        indexer = GitRepoIndexer(repo_urls, folder_path)

        # Should process all URLs even if duplicated
        assert len(indexer.local_repos) == 3
        assert mock_clone.call_count == 3


class TestGitRepoIndexerGetRemoteUrl:
    """Test cases for GitRepoIndexer.get_remote_url static method."""

    def test_get_remote_url_with_origin_https(self):
        """Test get_remote_url with repository having HTTPS origin remote."""
        # Create mock repository with origin remote
        mock_repo = MagicMock(spec=Repo)
        mock_repo.working_dir = "/path/to/repo"

        # Setup mock remotes - create a mock remotes collection
        mock_origin = MagicMock()
        mock_origin.name = "origin"
        mock_origin.url = "https://github.com/user/repo.git"

        # Create a mock remotes collection that behaves like GitPython's
        mock_remotes = MagicMock()
        mock_remotes.__iter__ = MagicMock(return_value=iter([mock_origin]))
        mock_remotes.origin.url = "https://github.com/user/repo.git"
        mock_repo.remotes = mock_remotes

        # Execute
        result = GitRepoIndexer.get_remote_url(mock_repo)

        # Verify
        assert result == "https://github.com/user/repo.git"

    def test_get_remote_url_with_origin_ssh(self):
        """Test get_remote_url with repository having SSH origin remote."""
        # Create mock repository with SSH origin remote
        mock_repo = MagicMock(spec=Repo)
        mock_repo.working_dir = "/path/to/repo"

        # Setup mock remotes
        mock_origin = MagicMock()
        mock_origin.name = "origin"
        mock_origin.url = "git@github.com:user/repo.git"

        mock_remotes = MagicMock()
        mock_remotes.__iter__ = MagicMock(return_value=iter([mock_origin]))
        mock_remotes.origin.url = "git@github.com:user/repo.git"
        mock_repo.remotes = mock_remotes

        # Execute
        result = GitRepoIndexer.get_remote_url(mock_repo)

        # Verify
        assert result == "git@github.com:user/repo.git"

    def test_get_remote_url_with_multiple_remotes_has_origin(self):
        """Test get_remote_url with multiple remotes including origin."""
        # Create mock repository with multiple remotes
        mock_repo = MagicMock(spec=Repo)
        mock_repo.working_dir = "/path/to/repo"

        # Setup multiple mock remotes
        mock_origin = MagicMock()
        mock_origin.name = "origin"
        mock_origin.url = "https://github.com/user/repo.git"

        mock_upstream = MagicMock()
        mock_upstream.name = "upstream"
        mock_upstream.url = "https://github.com/upstream/repo.git"

        mock_fork = MagicMock()
        mock_fork.name = "fork"
        mock_fork.url = "https://github.com/fork/repo.git"

        mock_remotes = MagicMock()
        mock_remotes.__iter__ = MagicMock(return_value=iter([mock_upstream, mock_origin, mock_fork]))
        mock_remotes.origin.url = "https://github.com/user/repo.git"
        mock_repo.remotes = mock_remotes

        # Execute
        result = GitRepoIndexer.get_remote_url(mock_repo)

        # Verify origin URL is returned despite multiple remotes
        assert result == "https://github.com/user/repo.git"

    def test_get_remote_url_no_remotes(self):
        """Test get_remote_url with repository having no remotes."""
        # Create mock repository with no remotes
        mock_repo = MagicMock(spec=Repo)
        mock_repo.working_dir = "/path/to/repo"

        mock_remotes = MagicMock()
        mock_remotes.__iter__ = MagicMock(return_value=iter([]))
        mock_remotes.__bool__ = MagicMock(return_value=False)
        mock_repo.remotes = mock_remotes

        # Execute
        result = GitRepoIndexer.get_remote_url(mock_repo)

        # Verify
        assert result is None

    def test_get_remote_url_no_origin_remote(self):
        """Test get_remote_url with repository having remotes but no origin."""
        # Create mock repository with remotes but no origin
        mock_repo = MagicMock(spec=Repo)
        mock_repo.working_dir = "/path/to/repo"

        # Setup mock remotes without origin
        mock_upstream = MagicMock()
        mock_upstream.name = "upstream"
        mock_upstream.url = "https://github.com/upstream/repo.git"

        mock_fork = MagicMock()
        mock_fork.name = "fork"
        mock_fork.url = "https://github.com/fork/repo.git"

        mock_remotes = MagicMock()
        mock_remotes.__iter__ = MagicMock(return_value=iter([mock_upstream, mock_fork]))
        mock_repo.remotes = mock_remotes

        # Execute
        result = GitRepoIndexer.get_remote_url(mock_repo)

        # Verify
        assert result is None

    def test_get_remote_url_none_repo_raises_error(self):
        """Test get_remote_url with None repository raises ValueError."""
        with pytest.raises(ValueError, match="repo must be provided"):
            GitRepoIndexer.get_remote_url(None)

    def test_get_remote_url_empty_repo_raises_error(self):
        """Test get_remote_url with empty/falsy repository raises ValueError."""
        with pytest.raises(ValueError, match="repo must be provided"):
            GitRepoIndexer.get_remote_url("")

        with pytest.raises(ValueError, match="repo must be provided"):
            GitRepoIndexer.get_remote_url(False)

        with pytest.raises(ValueError, match="repo must be provided"):
            GitRepoIndexer.get_remote_url(0)

    def test_get_remote_url_with_gitlab_url(self):
        """Test get_remote_url with GitLab repository URL."""
        # Create mock repository with GitLab origin
        mock_repo = MagicMock(spec=Repo)
        mock_repo.working_dir = "/path/to/repo"

        # Setup mock remotes
        mock_origin = MagicMock()
        mock_origin.name = "origin"
        mock_origin.url = "https://gitlab.com/user/project.git"

        mock_remotes = MagicMock()
        mock_remotes.__iter__ = MagicMock(return_value=iter([mock_origin]))
        mock_remotes.origin.url = "https://gitlab.com/user/project.git"
        mock_repo.remotes = mock_remotes

        # Execute
        result = GitRepoIndexer.get_remote_url(mock_repo)

        # Verify
        assert result == "https://gitlab.com/user/project.git"

    def test_get_remote_url_with_custom_git_server(self):
        """Test get_remote_url with custom Git server URL."""
        # Create mock repository with custom Git server
        mock_repo = MagicMock(spec=Repo)
        mock_repo.working_dir = "/path/to/repo"

        # Setup mock remotes
        mock_origin = MagicMock()
        mock_origin.name = "origin"
        mock_origin.url = "https://git.company.com/team/project.git"

        mock_remotes = MagicMock()
        mock_remotes.__iter__ = MagicMock(return_value=iter([mock_origin]))
        mock_remotes.origin.url = "https://git.company.com/team/project.git"
        mock_repo.remotes = mock_remotes

        # Execute
        result = GitRepoIndexer.get_remote_url(mock_repo)

        # Verify
        assert result == "https://git.company.com/team/project.git"

    def test_get_remote_url_with_ssh_custom_port(self):
        """Test get_remote_url with SSH URL using custom port."""
        # Create mock repository with SSH URL and custom port
        mock_repo = MagicMock(spec=Repo)
        mock_repo.working_dir = "/path/to/repo"

        # Setup mock remotes
        mock_origin = MagicMock()
        mock_origin.name = "origin"
        mock_origin.url = "ssh://git@git.company.com:2222/team/project.git"

        mock_remotes = MagicMock()
        mock_remotes.__iter__ = MagicMock(return_value=iter([mock_origin]))
        mock_remotes.origin.url = "ssh://git@git.company.com:2222/team/project.git"
        mock_repo.remotes = mock_remotes

        # Execute
        result = GitRepoIndexer.get_remote_url(mock_repo)

        # Verify
        assert result == "ssh://git@git.company.com:2222/team/project.git"

    def test_get_remote_url_case_sensitivity(self):
        """Test get_remote_url is case sensitive for remote names."""
        # Create mock repository with uppercase "ORIGIN" remote
        mock_repo = MagicMock(spec=Repo)
        mock_repo.working_dir = "/path/to/repo"

        # Setup mock remotes with uppercase name
        mock_origin_upper = MagicMock()
        mock_origin_upper.name = "ORIGIN"
        mock_origin_upper.url = "https://github.com/user/repo.git"

        mock_remotes = MagicMock()
        mock_remotes.__iter__ = MagicMock(return_value=iter([mock_origin_upper]))
        mock_repo.remotes = mock_remotes

        # Execute
        result = GitRepoIndexer.get_remote_url(mock_repo)

        # Verify - should return None because it looks for lowercase "origin"
        assert result is None

    @patch('java_mcp.git.git_repo_indexer.logger')
    def test_get_remote_url_logging(self, mock_logger):
        """Test get_remote_url produces appropriate log messages."""
        # Create mock repository with origin remote
        mock_repo = MagicMock(spec=Repo)
        mock_repo.working_dir = "/path/to/test/repo"

        # Setup mock remotes
        mock_origin = MagicMock()
        mock_origin.name = "origin"
        mock_origin.url = "https://github.com/user/repo.git"

        mock_remotes = MagicMock()
        mock_remotes.__iter__ = MagicMock(return_value=iter([mock_origin]))
        mock_remotes.origin.url = "https://github.com/user/repo.git"
        mock_repo.remotes = mock_remotes

        # Execute
        result = GitRepoIndexer.get_remote_url(mock_repo)

        # Verify logging calls
        mock_logger.debug.assert_has_calls([
            call("Fetching remote Git repository URL for: /path/to/test/repo"),
            call("Origin URL: https://github.com/user/repo.git")
        ])

        # Verify result
        assert result == "https://github.com/user/repo.git"

    @patch('java_mcp.git.git_repo_indexer.logger')
    def test_get_remote_url_logging_no_origin(self, mock_logger):
        """Test get_remote_url logging when no origin remote exists."""
        # Create mock repository with no origin remote
        mock_repo = MagicMock(spec=Repo)
        mock_repo.working_dir = "/path/to/test/repo"

        mock_remotes = MagicMock()
        mock_remotes.__iter__ = MagicMock(return_value=iter([]))
        mock_remotes.__bool__ = MagicMock(return_value=False)
        mock_repo.remotes = mock_remotes

        # Execute
        result = GitRepoIndexer.get_remote_url(mock_repo)

        # Verify logging calls - should only log the initial debug message
        mock_logger.debug.assert_called_once_with(
            "Fetching remote Git repository URL for: /path/to/test/repo"
        )

        # Verify result
        assert result is None

    @patch('java_mcp.git.git_repo_indexer.logger')
    def test_get_remote_url_logging_error_for_none_repo(self, mock_logger):
        """Test get_remote_url error logging for None repository."""
        # Execute and expect exception
        with pytest.raises(ValueError, match="repo must be provided"):
            GitRepoIndexer.get_remote_url(None)

        # Verify error logging
        mock_logger.error.assert_called_once_with("repo must be provided")


if __name__ == "__main__":
    pytest.main([__file__])
