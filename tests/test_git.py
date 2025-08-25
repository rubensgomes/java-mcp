"""
Unit tests for the git.py module.

This test suite provides comprehensive coverage for all git operations including
input validation, URL validation, repository checks, folder creation, and
git clone/update operations.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from git import Repo, GitCommandError

from java_mcp.git import (
    _validate_inputs,
    _create_folder,
    is_valid_git_url,
    is_git_repo,
    is_valid_git_repo,
    git_folder_name,
    update,
    clone_or_update
)


class TestValidateInputs:
    """Test cases for the _validate_inputs function."""

    def test_valid_inputs(self):
        """Test that valid inputs pass validation."""
        # Should not raise any exception
        _validate_inputs("/path/to/folder", "https://github.com/user/repo.git")
        _validate_inputs("relative/path", "git@github.com:user/repo.git")
        _validate_inputs("/home/user", "ssh://git@github.com/user/repo.git")

    def test_empty_folder_path_raises_error(self):
        """Test that empty folder path raises ValueError."""
        with pytest.raises(ValueError, match="folder_path must be provided"):
            _validate_inputs("", "https://github.com/user/repo.git")

    def test_none_folder_path_raises_error(self):
        """Test that None folder path raises ValueError."""
        with pytest.raises(ValueError, match="folder_path must be provided"):
            _validate_inputs(None, "https://github.com/user/repo.git")

    def test_empty_repository_url_raises_error(self):
        """Test that empty repository URL raises ValueError."""
        with pytest.raises(ValueError, match="repository_url must be provided"):
            _validate_inputs("/path/to/folder", "")

    def test_none_repository_url_raises_error(self):
        """Test that None repository URL raises ValueError."""
        with pytest.raises(ValueError, match="repository_url must be provided"):
            _validate_inputs("/path/to/folder", None)

    def test_invalid_repository_url_raises_error(self):
        """Test that invalid repository URL raises ValueError."""
        with pytest.raises(ValueError, match="repository_url is not valid"):
            _validate_inputs("/path/to/folder", "https://github.com/user/repo")  # Missing .git

        with pytest.raises(ValueError, match="repository_url is not valid"):
            _validate_inputs("/path/to/folder", "ftp://example.com/repo.git")  # Invalid protocol


class TestCreateFolder:
    """Test cases for the _create_folder function."""

    def test_create_new_folder(self):
        """Test creating a new folder."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_folder = Path(temp_dir) / "new_folder"
            _create_folder(str(test_folder))
            assert test_folder.exists()
            assert test_folder.is_dir()

    def test_create_nested_folders(self):
        """Test creating nested folder structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_folder = Path(temp_dir) / "nested" / "deep" / "folder"
            _create_folder(str(test_folder))
            assert test_folder.exists()
            assert test_folder.is_dir()

    def test_existing_folder_no_error(self):
        """Test that creating existing folder doesn't raise error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create folder twice - should not raise error
            _create_folder(temp_dir)
            _create_folder(temp_dir)
            assert Path(temp_dir).exists()


class TestIsValidGitUrl:
    """Test cases for the is_valid_git_url function."""

    def test_valid_https_url(self):
        """Test valid HTTPS URLs."""
        assert is_valid_git_url("https://github.com/user/repo.git") is True
        assert is_valid_git_url("https://gitlab.com/user/project.git") is True

    def test_valid_http_url(self):
        """Test valid HTTP URLs."""
        assert is_valid_git_url("http://github.com/user/repo.git") is True

    def test_valid_ssh_git_url(self):
        """Test valid SSH git@ URLs."""
        assert is_valid_git_url("git@github.com:user/repo.git") is True
        assert is_valid_git_url("git@gitlab.com:user/project.git") is True

    def test_valid_ssh_protocol_url(self):
        """Test valid SSH protocol URLs."""
        assert is_valid_git_url("ssh://git@github.com/user/repo.git") is True

    def test_invalid_protocol(self):
        """Test URLs with invalid protocols."""
        assert is_valid_git_url("ftp://example.com/repo.git") is False
        assert is_valid_git_url("file:///path/to/repo.git") is False
        assert is_valid_git_url("invalid://example.com/repo.git") is False

    def test_missing_git_extension(self):
        """Test URLs missing .git extension."""
        assert is_valid_git_url("https://github.com/user/repo") is False
        assert is_valid_git_url("git@github.com:user/repo") is False

    def test_empty_or_none_url(self):
        """Test empty or None URLs."""
        assert is_valid_git_url("") is False
        assert is_valid_git_url(None) is False


class TestIsGitRepo:
    """Test cases for the is_git_repo function."""

    def test_valid_git_repository(self):
        """Test detection of valid git repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a .git directory
            git_dir = Path(temp_dir) / ".git"
            git_dir.mkdir()

            assert is_git_repo(temp_dir) is True

    def test_non_git_directory(self):
        """Test detection of non-git directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Directory exists but no .git subdirectory
            assert is_git_repo(temp_dir) is False

    def test_nonexistent_directory(self):
        """Test detection of nonexistent directory."""
        assert is_git_repo("/path/that/does/not/exist") is False

    def test_file_instead_of_directory(self):
        """Test when path points to a file instead of directory."""
        with tempfile.NamedTemporaryFile() as temp_file:
            assert is_git_repo(temp_file.name) is False


class TestIsValidGitRepo:
    """Test cases for the is_valid_git_repo function."""

    @patch('java_mcp.git.is_git_repo')
    @patch('java_mcp.git.Repo')
    def test_valid_repo_matching_url(self, mock_repo_class, mock_is_git_repo):
        """Test valid repository with matching URL."""
        mock_is_git_repo.return_value = True

        # Mock the repo and remote
        mock_repo = Mock()
        mock_remote = Mock()
        mock_remote.url = "https://github.com/user/repo.git"
        mock_repo.remotes.origin = mock_remote
        mock_repo_class.return_value = mock_repo

        result = is_valid_git_repo("/path/to/repo", "https://github.com/user/repo.git")
        assert result is True

    @patch('java_mcp.git.is_git_repo')
    @patch('java_mcp.git.Repo')
    def test_valid_repo_different_url(self, mock_repo_class, mock_is_git_repo):
        """Test valid repository with different URL."""
        mock_is_git_repo.return_value = True

        # Mock the repo and remote with different URL
        mock_repo = Mock()
        mock_remote = Mock()
        mock_remote.url = "https://github.com/user/other.git"
        mock_repo.remotes.origin = mock_remote
        mock_repo_class.return_value = mock_repo

        result = is_valid_git_repo("/path/to/repo", "https://github.com/user/repo.git")
        assert result is False

    @patch('java_mcp.git.is_git_repo')
    def test_not_git_repo(self, mock_is_git_repo):
        """Test when folder is not a git repository."""
        mock_is_git_repo.return_value = False

        result = is_valid_git_repo("/path/to/folder", "https://github.com/user/repo.git")
        assert result is False


class TestGitFolderName:
    """Test cases for the git_folder_name function."""

    def test_github_https_url(self):
        """Test folder name generation for GitHub HTTPS URL."""
        result = git_folder_name("/repos", "https://github.com/user/myproject.git")
        expected = str(Path("/repos") / "myproject")
        assert result == expected

    def test_github_ssh_url(self):
        """Test folder name generation for GitHub SSH URL."""
        result = git_folder_name("~/code", "git@github.com:user/awesome-lib.git")
        expected = str(Path("~/code") / "awesome-lib")
        assert result == expected

    def test_relative_path(self):
        """Test folder name generation with relative path."""
        result = git_folder_name("projects", "https://gitlab.com/team/webapp.git")
        expected = str(Path("projects") / "webapp")
        assert result == expected

    def test_complex_repo_name(self):
        """Test folder name generation with complex repository name."""
        result = git_folder_name("/base", "https://github.com/org/project-name-with-dashes.git")
        expected = str(Path("/base") / "project-name-with-dashes")
        assert result == expected

    def test_invalid_inputs_raise_error(self):
        """Test that invalid inputs raise ValueError."""
        with pytest.raises(ValueError):
            git_folder_name("", "https://github.com/user/repo.git")

        with pytest.raises(ValueError):
            git_folder_name("/path", "invalid-url")


class TestUpdate:
    """Test cases for the update function."""

    @patch('java_mcp.git.git_folder_name')
    @patch('java_mcp.git._validate_inputs')
    @patch('java_mcp.git.Repo')
    def test_successful_update_matching_url(self, mock_repo_class, mock_validate, mock_git_folder):
        """Test successful update with matching URL."""
        mock_validate.return_value = None
        mock_git_folder.return_value = "/repos/project"

        # Mock the repo and remote
        mock_repo = Mock()
        mock_remote = Mock()
        mock_remote.url = "https://github.com/user/repo.git"
        mock_remote.pull = Mock()
        mock_repo.remotes.origin = mock_remote
        mock_repo_class.return_value = mock_repo

        # Should not raise exception
        update("/repos", "https://github.com/user/repo.git")

        mock_remote.pull.assert_called_once()

    @patch('java_mcp.git.git_folder_name')
    @patch('java_mcp.git._validate_inputs')
    @patch('java_mcp.git.Repo')
    def test_update_different_url_raises_exception(self, mock_repo_class, mock_validate, mock_git_folder):
        """Test update with different URL raises exception."""
        mock_validate.return_value = None
        mock_git_folder.return_value = "/repos/project"

        # Mock the repo and remote with different URL
        mock_repo = Mock()
        mock_remote = Mock()
        mock_remote.url = "https://github.com/user/different.git"
        mock_repo.remotes.origin = mock_remote
        mock_repo_class.return_value = mock_repo

        with pytest.raises(Exception, match="different remote URL"):
            update("/repos", "https://github.com/user/repo.git")

    @patch('java_mcp.git._validate_inputs')
    def test_update_invalid_inputs_raise_error(self, mock_validate):
        """Test that invalid inputs raise ValueError."""
        mock_validate.side_effect = ValueError("Invalid input")

        with pytest.raises(ValueError):
            update("", "https://github.com/user/repo.git")


class TestCloneOrUpdate:
    """Test cases for the clone_or_update function."""

    @patch('java_mcp.git.is_git_repo')
    @patch('java_mcp.git.is_valid_git_repo')
    @patch('java_mcp.git.git_folder_name')
    @patch('java_mcp.git._create_folder')
    @patch('java_mcp.git._validate_inputs')
    @patch('java_mcp.git.Repo')
    def test_update_existing_repo(self, mock_repo_class, mock_validate, mock_create_folder,
                                 mock_git_folder, mock_is_valid_git_repo, mock_is_git_repo):
        """Test updating existing repository."""
        mock_validate.return_value = None
        mock_create_folder.return_value = None
        mock_git_folder.return_value = "/repos/project"
        mock_is_git_repo.return_value = True
        mock_is_valid_git_repo.return_value = True

        # Mock the repo for pull operation
        mock_repo = Mock()
        mock_remote = Mock()
        mock_remote.pull = Mock()
        mock_repo.remotes.origin = mock_remote
        mock_repo_class.return_value = mock_repo

        clone_or_update("/repos", "https://github.com/user/repo.git")

        mock_remote.pull.assert_called_once()

    @patch('java_mcp.git.is_git_repo')
    @patch('java_mcp.git.is_valid_git_repo')
    @patch('java_mcp.git.git_folder_name')
    @patch('java_mcp.git._create_folder')
    @patch('java_mcp.git._validate_inputs')
    def test_existing_repo_different_url_raises_exception(self, mock_validate, mock_create_folder,
                                                         mock_git_folder, mock_is_valid_git_repo,
                                                         mock_is_git_repo):
        """Test existing repository with different URL raises exception."""
        mock_validate.return_value = None
        mock_create_folder.return_value = None
        mock_git_folder.return_value = "/repos/project"
        mock_is_git_repo.return_value = True
        mock_is_valid_git_repo.return_value = False

        with pytest.raises(Exception, match="does not match the provided URL"):
            clone_or_update("/repos", "https://github.com/user/repo.git")

    @patch('java_mcp.git.is_git_repo')
    @patch('java_mcp.git.git_folder_name')
    @patch('java_mcp.git._create_folder')
    @patch('java_mcp.git._validate_inputs')
    @patch('java_mcp.git.Repo')
    def test_clone_new_repo(self, mock_repo_class, mock_validate, mock_create_folder,
                           mock_git_folder, mock_is_git_repo):
        """Test cloning new repository."""
        mock_validate.return_value = None
        mock_create_folder.return_value = None
        mock_git_folder.return_value = "/repos/project"
        mock_is_git_repo.return_value = False

        # Mock the clone_from class method
        mock_repo_class.clone_from = Mock()

        clone_or_update("/repos", "https://github.com/user/repo.git")

        mock_repo_class.clone_from.assert_called_once_with(
            "https://github.com/user/repo.git",
            Path("/repos"),
            depth=1
        )

    @patch('java_mcp.git._validate_inputs')
    def test_invalid_inputs_raise_error(self, mock_validate):
        """Test that invalid inputs raise ValueError."""
        mock_validate.side_effect = ValueError("Invalid input")

        with pytest.raises(ValueError):
            clone_or_update("", "https://github.com/user/repo.git")


# Integration test helpers for when we want to test with actual git operations
class TestIntegrationHelpers:
    """Helper methods for integration tests (when testing with real git repos)."""

    @pytest.fixture
    def temp_git_repo(self):
        """Create a temporary git repository for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            # Initialize git repo
            repo = Repo.init(repo_path)

            # Create initial commit
            test_file = repo_path / "README.md"
            test_file.write_text("# Test Repository")
            # Use relative path for git add to avoid path resolution issues
            repo.index.add(["README.md"])
            repo.index.commit("Initial commit")

            yield repo_path, repo

    def test_is_git_repo_integration(self, temp_git_repo):
        """Integration test for is_git_repo with real git repository."""
        repo_path, _ = temp_git_repo
        assert is_git_repo(str(repo_path)) is True

    def test_git_folder_name_integration(self):
        """Integration test for git_folder_name."""
        result = git_folder_name("/tmp", "https://github.com/test/integration.git")
        expected = "/tmp/integration"
        assert result == expected


if __name__ == "__main__":
    pytest.main([__file__])
