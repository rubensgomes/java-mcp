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
        assert len(indexer.repos) == 1
        assert indexer.repos[0] == mock_repo

        # Verify method calls
        mock_valid_url.assert_called_once_with("https://github.com/user/repo.git")
        mock_ping.assert_called_once_with("https://github.com/user/repo.git")
        mock_create.assert_called_once_with(folder_path)
        mock_clone.assert_called_once_with(folder_path, "https://github.com/user/repo.git")

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
        assert len(indexer.repos) == 3
        assert indexer.repos == [mock_repo1, mock_repo2, mock_repo3]

        # Verify validation calls
        expected_url_calls = [call(url) for url in repo_urls]
        mock_valid_url.assert_has_calls(expected_url_calls)
        mock_ping.assert_has_calls(expected_url_calls)

        # Verify clone calls
        expected_clone_calls = [call(folder_path, url) for url in repo_urls]
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
            assert indexer.repos == []
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
        assert indexer.repos == mock_repos
        assert len(indexer.repos) == 5

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

        assert len(indexer.repos) == 4
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
        repos = indexer.get_repos()

        assert repos == [mock_repo1, mock_repo2]
        assert repos is indexer.repos  # Should return the same list object

    @patch('java_mcp.git.git_repo_indexer.create_folder')
    def test_get_repos_empty_list(self, mock_create):
        """Test get_repos with empty repository list."""
        indexer = GitRepoIndexer([], "/test/repos")
        repos = indexer.get_repos()

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

        repos1 = indexer.get_repos()
        repos2 = indexer.get_repos()

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
        repos = indexer.get_repos()
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

        assert len(indexer.repos) == num_repos
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
        assert len(indexer.repos) == 3
        assert mock_clone.call_count == 3


if __name__ == "__main__":
    pytest.main([__file__])
