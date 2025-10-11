"""Tests for .env file discovery and copying utilities.

This module tests all functions in spork.env_files with filesystem operations.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestDiscoverEnvFiles:
    """Tests for discover_env_files() function."""

    def test_discover_env_files_finds_files(self, tmp_path):
        """Given workspace with .env files
        When calling discover_env_files()
        Then all .env files should be returned"""
        from spork.env_files import discover_env_files

        # Given
        (tmp_path / ".env").write_text("KEY=value")
        (tmp_path / ".env.local").write_text("KEY=local")
        backend_dir = tmp_path / "backend"
        backend_dir.mkdir()
        (backend_dir / ".env.development").write_text("KEY=dev")
        (tmp_path / "README.md").write_text("# readme")

        # When
        result = discover_env_files(tmp_path)

        # Then
        assert ".env" in result
        assert ".env.local" in result
        assert str(Path("backend") / ".env.development") in result
        assert "README.md" not in result

    def test_discover_env_files_empty_workspace(self, tmp_path):
        """Given workspace with no .env files
        When calling discover_env_files()
        Then empty list should be returned"""
        from spork.env_files import discover_env_files

        # Given - empty directory

        # When
        result = discover_env_files(tmp_path)

        # Then
        assert result == []

    def test_discover_env_files_filters_non_env(self, tmp_path):
        """Given workspace with mixed file types
        When calling discover_env_files()
        Then only .env* files should be returned"""
        from spork.env_files import discover_env_files

        # Given
        (tmp_path / ".env").write_text("KEY=value")
        (tmp_path / "config.json").write_text("{}")
        (tmp_path / ".gitignore").write_text("*.log")
        (tmp_path / ".env.test").write_text("KEY=test")
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("print('hello')")

        # When
        result = discover_env_files(tmp_path)

        # Then
        assert len(result) == 2
        assert ".env" in result
        assert ".env.test" in result

    def test_discover_env_files_nested_directories(self, tmp_path):
        """Given .env files in nested directories
        When calling discover_env_files()
        Then nested paths should be preserved"""
        from spork.env_files import discover_env_files

        # Given
        backend_dir = tmp_path / "backend"
        backend_dir.mkdir()
        (backend_dir / ".env").write_text("KEY=backend")

        frontend_dir = tmp_path / "frontend"
        frontend_dir.mkdir()
        (frontend_dir / ".env.local").write_text("KEY=frontend")

        api_config_dir = tmp_path / "api" / "config"
        api_config_dir.mkdir(parents=True)
        (api_config_dir / ".env.test").write_text("KEY=api")

        # When
        result = discover_env_files(tmp_path)

        # Then
        assert str(Path("backend") / ".env") in result
        assert str(Path("frontend") / ".env.local") in result
        assert str(Path("api") / "config" / ".env.test") in result

    def test_discover_env_files_skips_git_directory(self, tmp_path):
        """Given .env files in .git directory
        When calling discover_env_files()
        Then .git files should be skipped"""
        from spork.env_files import discover_env_files

        # Given
        (tmp_path / ".env").write_text("KEY=value")
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / ".env.backup").write_text("KEY=backup")

        # When
        result = discover_env_files(tmp_path)

        # Then
        assert ".env" in result
        assert len(result) == 1  # Should not include .git/.env.backup

    def test_discover_env_files_skips_worktrees_directory(self, tmp_path):
        """Given .env files in .worktrees directory
        When calling discover_env_files()
        Then .worktrees files should be skipped"""
        from spork.env_files import discover_env_files

        # Given
        (tmp_path / ".env").write_text("KEY=value")
        worktrees_dir = tmp_path / ".worktrees" / "feature-branch"
        worktrees_dir.mkdir(parents=True)
        (worktrees_dir / ".env").write_text("KEY=worktree")

        # When
        result = discover_env_files(tmp_path)

        # Then
        assert ".env" in result
        assert len(result) == 1  # Should not include .worktrees files

    def test_discover_env_files_invalid_path(self):
        """Given non-existent workspace path
        When calling discover_env_files()
        Then ValueError should be raised"""
        from spork.env_files import discover_env_files

        # When / Then
        with pytest.raises(ValueError, match="does not exist"):
            discover_env_files(Path("/nonexistent/path"))

    def test_discover_env_files_not_directory(self, tmp_path):
        """Given path to a file (not directory)
        When calling discover_env_files()
        Then ValueError should be raised"""
        from spork.env_files import discover_env_files

        # Given
        file_path = tmp_path / "file.txt"
        file_path.write_text("content")

        # When / Then
        with pytest.raises(ValueError, match="not a directory"):
            discover_env_files(file_path)


class TestReadEnvFileFromFilesystem:
    """Tests for read_env_file_from_filesystem() function."""

    def test_read_env_file_success(self, tmp_path):
        """Given valid workspace and filepath
        When calling read_env_file_from_filesystem()
        Then file content should be returned"""
        from spork.env_files import read_env_file_from_filesystem

        # Given
        expected_content = "DATABASE_URL=postgres://localhost\nAPI_KEY=test123\n"
        (tmp_path / ".env").write_text(expected_content)

        # When
        result = read_env_file_from_filesystem(tmp_path, ".env")

        # Then
        assert result == expected_content

    def test_read_env_file_nested_path(self, tmp_path):
        """Given nested .env file
        When calling read_env_file_from_filesystem()
        Then file content should be returned"""
        from spork.env_files import read_env_file_from_filesystem

        # Given
        backend_dir = tmp_path / "backend"
        backend_dir.mkdir()
        expected_content = "DB_HOST=localhost\n"
        (backend_dir / ".env").write_text(expected_content)

        # When
        result = read_env_file_from_filesystem(tmp_path, str(Path("backend") / ".env"))

        # Then
        assert result == expected_content

    def test_read_env_file_not_found(self, tmp_path):
        """Given file that doesn't exist
        When calling read_env_file_from_filesystem()
        Then FileNotFoundError should be raised"""
        from spork.env_files import read_env_file_from_filesystem

        # When / Then
        with pytest.raises(FileNotFoundError, match="not found"):
            read_env_file_from_filesystem(tmp_path, "missing.env")

    def test_read_env_file_invalid_workspace(self):
        """Given non-existent workspace
        When calling read_env_file_from_filesystem()
        Then ValueError should be raised"""
        from spork.env_files import read_env_file_from_filesystem

        # When / Then
        with pytest.raises(ValueError, match="does not exist"):
            read_env_file_from_filesystem(Path("/nonexistent"), ".env")

    def test_read_env_file_empty_filepath(self, tmp_path):
        """Given empty filepath
        When calling read_env_file_from_filesystem()
        Then ValueError should be raised"""
        from spork.env_files import read_env_file_from_filesystem

        # When / Then
        with pytest.raises(ValueError, match="cannot be empty"):
            read_env_file_from_filesystem(tmp_path, "")

    def test_read_env_file_is_directory(self, tmp_path):
        """Given path that is a directory
        When calling read_env_file_from_filesystem()
        Then ValueError should be raised"""
        from spork.env_files import read_env_file_from_filesystem

        # Given
        dir_path = tmp_path / "subdir"
        dir_path.mkdir()

        # When / Then
        with pytest.raises(ValueError, match="not a file"):
            read_env_file_from_filesystem(tmp_path, "subdir")


class TestCopyEnvFilesToWorktree:
    """Tests for copy_env_files_to_worktree() function."""

    @patch("spork.env_files.get_repo_root")
    def test_copy_all_files_success(self, mock_get_repo_root, tmp_path):
        """Given multiple .env files in workspace
        When calling copy_env_files_to_worktree()
        Then all files should be copied successfully"""
        from spork.env_files import copy_env_files_to_worktree

        # Given - setup main workspace
        main_workspace = tmp_path / "main"
        main_workspace.mkdir()
        (main_workspace / ".env").write_text("CONTENT1=value1\n")
        (main_workspace / ".env.local").write_text("CONTENT2=value2\n")
        backend_dir = main_workspace / "backend"
        backend_dir.mkdir()
        (backend_dir / ".env").write_text("CONTENT3=value3\n")

        # Setup worktree
        worktree_path = tmp_path / "worktree"
        worktree_path.mkdir()

        mock_get_repo_root.return_value = main_workspace

        # When
        result = copy_env_files_to_worktree(worktree_path)

        # Then
        assert result.files_discovered == 3
        assert result.files_copied == 3
        assert result.files_failed == 0
        assert result.success is True
        assert (worktree_path / ".env").read_text() == "CONTENT1=value1\n"
        assert (worktree_path / ".env.local").read_text() == "CONTENT2=value2\n"
        assert (worktree_path / "backend" / ".env").read_text() == "CONTENT3=value3\n"

    @patch("spork.env_files.get_repo_root")
    def test_copy_creates_parent_directories(self, mock_get_repo_root, tmp_path):
        """Given nested .env files
        When calling copy_env_files_to_worktree()
        Then parent directories should be created"""
        from spork.env_files import copy_env_files_to_worktree

        # Given
        main_workspace = tmp_path / "main"
        main_workspace.mkdir()
        nested_dir = main_workspace / "backend" / "api"
        nested_dir.mkdir(parents=True)
        (nested_dir / ".env").write_text("CONTENT=value\n")

        worktree_path = tmp_path / "worktree"
        worktree_path.mkdir()

        mock_get_repo_root.return_value = main_workspace

        # When
        result = copy_env_files_to_worktree(worktree_path)

        # Then
        assert result.files_copied == 1
        assert (worktree_path / "backend" / "api" / ".env").exists()
        assert (worktree_path / "backend" / "api" / ".env").read_text() == "CONTENT=value\n"

    @patch("spork.env_files.get_repo_root")
    def test_copy_overwrites_existing_files(self, mock_get_repo_root, tmp_path):
        """Given existing .env files in worktree
        When calling copy_env_files_to_worktree()
        Then files should be overwritten"""
        from spork.env_files import copy_env_files_to_worktree

        # Given
        main_workspace = tmp_path / "main"
        main_workspace.mkdir()
        (main_workspace / ".env").write_text("NEW_CONTENT=value\n")

        worktree_path = tmp_path / "worktree"
        worktree_path.mkdir()
        (worktree_path / ".env").write_text("OLD_CONTENT=old\n")

        mock_get_repo_root.return_value = main_workspace

        # When
        result = copy_env_files_to_worktree(worktree_path)

        # Then
        assert result.files_copied == 1
        assert (worktree_path / ".env").read_text() == "NEW_CONTENT=value\n"

    @patch("spork.env_files.get_repo_root")
    def test_copy_no_env_files(self, mock_get_repo_root, tmp_path):
        """Given workspace with no .env files
        When calling copy_env_files_to_worktree()
        Then result should indicate zero files"""
        from spork.env_files import copy_env_files_to_worktree

        # Given
        main_workspace = tmp_path / "main"
        main_workspace.mkdir()
        (main_workspace / "README.md").write_text("# readme")

        worktree_path = tmp_path / "worktree"
        worktree_path.mkdir()

        mock_get_repo_root.return_value = main_workspace

        # When
        result = copy_env_files_to_worktree(worktree_path)

        # Then
        assert result.files_discovered == 0
        assert result.files_copied == 0
        assert result.files_failed == 0

    def test_copy_invalid_worktree_path(self):
        """Given non-existent worktree path
        When calling copy_env_files_to_worktree()
        Then ValueError should be raised"""
        from spork.env_files import copy_env_files_to_worktree

        # Given
        worktree_path = Path("/nonexistent/path")

        # When / Then
        with pytest.raises(ValueError, match="does not exist"):
            copy_env_files_to_worktree(worktree_path)

    @patch("spork.env_files.get_repo_root")
    def test_copy_cannot_get_repo_root(self, mock_get_repo_root, tmp_path):
        """Given get_repo_root raises error
        When calling copy_env_files_to_worktree()
        Then RuntimeError should be raised"""
        from spork.env_files import copy_env_files_to_worktree

        # Given
        worktree_path = tmp_path / "worktree"
        worktree_path.mkdir()
        mock_get_repo_root.side_effect = RuntimeError("not a git repository")

        # When / Then
        with pytest.raises(RuntimeError, match="Cannot determine repository root"):
            copy_env_files_to_worktree(worktree_path)

    @patch("spork.env_files.get_repo_root")
    @patch("spork.env_files.read_env_file_from_filesystem")
    def test_copy_partial_success(self, mock_read, mock_get_repo_root, tmp_path):
        """Given one file with read error
        When calling copy_env_files_to_worktree()
        Then partial success should be reported"""
        from spork.env_files import copy_env_files_to_worktree

        # Given
        main_workspace = tmp_path / "main"
        main_workspace.mkdir()
        (main_workspace / ".env").write_text("CONTENT1=value1\n")
        (main_workspace / ".env.local").write_text("CONTENT2=value2\n")

        worktree_path = tmp_path / "worktree"
        worktree_path.mkdir()

        mock_get_repo_root.return_value = main_workspace
        # First file succeeds, second fails
        mock_read.side_effect = [
            "CONTENT1=value1\n",
            PermissionError("Permission denied")
        ]

        # When
        result = copy_env_files_to_worktree(worktree_path)

        # Then
        assert result.files_discovered == 2
        assert result.files_copied == 1
        assert result.files_failed == 1
        assert result.partial_success is True
        assert len(result.errors) == 1
