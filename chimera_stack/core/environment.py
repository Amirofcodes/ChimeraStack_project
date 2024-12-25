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
        
        # Define standard directory structure
        self.dirs = {
            'docker': self.path / 'docker',
            'config': self.path / 'config',
            'src': self.path / 'src'
        }

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
            'devstack_factory',
            'setup.py',
            'setup.cfg'
        ]
        return any((path / indicator).exists() for indicator in tool_indicators)

    def setup(self) -> bool:
        """
        Initialize the development environment with proper directory structure.
        
        Returns:
            bool: True if setup was successful
        """
        try:
            # Create main project directory if it doesn't exist
            self.path.mkdir(exist_ok=True, parents=True)
            
            # Create standard directory structure
            for dir_path in self.dirs.values():
                dir_path.mkdir(exist_ok=True, parents=True)
            
            # Create initial configuration files
            self._create_initial_files()
            
            # Remove any duplicate project directories
            self._cleanup_duplicate_directories()
            
            return True
        except Exception as e:
            print(f"Error setting up environment: {e}")
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

# Docker
.docker/

# IDE files
.idea/
.vscode/
*.sublime-*

# OS files
.DS_Store
Thumbs.db
"""
            gitignore.write_text(gitignore_content.strip())

    def _cleanup_duplicate_directories(self) -> None:
        """Remove any duplicate project directories that might have been created."""
        duplicate_dir = self.path / self.name
        if duplicate_dir.exists():
            if duplicate_dir.is_dir():
                # If there are important files in the duplicate directory, move them up
                self._migrate_important_files(duplicate_dir)
                shutil.rmtree(duplicate_dir)

    def _migrate_important_files(self, duplicate_dir: Path) -> None:
        """
        Migrate any important files from duplicate directory to main project directory.
        
        Args:
            duplicate_dir: Path to the duplicate directory
        """
        try:
            for item in duplicate_dir.iterdir():
                target_path = self.path / item.name
                if not target_path.exists():
                    if item.is_dir():
                        shutil.copytree(item, target_path)
                    else:
                        shutil.copy2(item, target_path)
        except Exception as e:
            print(f"Warning: Error while migrating files: {e}")

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