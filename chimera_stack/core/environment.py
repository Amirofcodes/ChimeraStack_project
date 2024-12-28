"""
Environment Management Module

Handles the creation and configuration of development environments.
"""

import os
import shutil
from typing import Dict, Optional
from pathlib import Path


class Environment:
    """Manages development environment setup and configuration."""

    def __init__(self, name: str, path: Optional[Path] = None):
        """
        Initialize environment manager.

        Args:
            name: Name of the project
            path: Optional path override. If not provided, uses current working directory
        """
        self.name = name
        self.path = path or self._get_safe_project_path()
        self.config: Dict = {}

    def _get_safe_project_path(self) -> Path:
        """
        Get a safe path for project creation that avoids the tool's directory.

        Returns:
            Path: Safe project path
        """
        cwd = Path.cwd()
        if self._is_tool_directory(cwd):
            return cwd.parent / self.name
        return cwd / self.name

    def _is_tool_directory(self, path: Path) -> bool:
        """
        Check if the given path is the tool's installation directory.

        Args:
            path: Path to check

        Returns:
            bool: True if path is tool directory
        """
        tool_indicators = [
            'pyproject.toml',
            'chimera_stack',
            'setup.py',
            'setup.cfg'
        ]
        return any((path / indicator).exists() for indicator in tool_indicators)

    def create_directory(self, path: Path) -> bool:
        """
        Safely create a directory only if needed.

        Args:
            path: Path to create

        Returns:
            bool: True if directory was created successfully
        """
        try:
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {path}: {e}")
            return False

    def setup(self) -> bool:
        """
        Initialize the development environment.
        Only creates essential directories, letting services create their own.

        Returns:
            bool: True if setup was successful
        """
        try:
            # Create project root
            self.create_directory(self.path)

            # Create essential directories
            essential_dirs = [
                self.path / 'src',
                self.path / 'public',
                self.path / 'config'
            ]

            for dir_path in essential_dirs:
                if not self.create_directory(dir_path):
                    return False

            # Create initial configuration files
            self._create_initial_files()

            return True
        except Exception as e:
            print(f"Error setting up environment: {e}")
            self.cleanup()
            return False

    def _create_initial_files(self) -> None:
        """Create initial configuration files for the project."""
        # Create empty docker-compose.yml
        docker_compose = self.path / 'docker-compose.yml'
        docker_compose.touch(exist_ok=True)

        # Create empty .env file
        env_file = self.path / '.env'
        env_file.touch(exist_ok=True)

        # Create .gitignore if it doesn't exist
        gitignore = self.path / '.gitignore'
        if not gitignore.exists():
            gitignore_content = """
# Environment files
.env
*.env

# Dependencies
/vendor/
__pycache__/
*.py[cod]
*$py.class

# IDE files
.idea/
.vscode/
*.sublime-*

# OS files
.DS_Store
Thumbs.db

# Logs
*.log

# Build artifacts
/build/
/dist/
"""
            gitignore.write_text(gitignore_content.strip())

    def cleanup(self) -> bool:
        """
        Clean up the development environment.

        Returns:
            bool: True if cleanup was successful
        """
        try:
            if self.path.exists():
                shutil.rmtree(self.path)
            return True
        except Exception as e:
            print(f"Error cleaning up environment: {e}")
            return False