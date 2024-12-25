"""
Base Framework Interface

Defines the contract that all framework implementations must follow,
ensuring consistent behavior across different programming languages and frameworks.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional, Any


class BaseFramework(ABC):
    """Abstract base class for framework implementations."""

    def __init__(self, project_name: str, base_path: Path):
        """
        Initialize the framework.
        
        Args:
            project_name: Name of the project
            base_path: Root path of the project
        """
        self.project_name = project_name
        self.base_path = base_path
        self.src_path = base_path / 'src'
        self.docker_path = base_path / 'docker'
        self.config_path = base_path / 'config'
        self.docker_requirements: Dict[str, Dict] = {}

    @abstractmethod
    def initialize_project(self) -> bool:
        """
        Initialize a new project with the framework.
        
        Returns:
            bool: True if initialization was successful
        """
        pass

    @abstractmethod
    def configure_docker(self) -> Dict[str, Any]:
        """
        Generate Docker configuration for the framework.
        
        Returns:
            Dict[str, Any]: Docker configuration dictionary
        """
        pass

    @abstractmethod
    def get_default_ports(self) -> Dict[str, int]:
        """
        Return default ports used by the framework.
        
        Returns:
            Dict[str, int]: Dictionary of service names to port numbers
        """
        pass

    @abstractmethod
    def setup_development_environment(self) -> bool:
        """
        Set up development environment for the framework.
        
        Returns:
            bool: True if setup was successful
        """
        pass

    def ensure_directories(self) -> bool:
        """
        Ensure all required directories exist.
        
        Returns:
            bool: True if all directories were created successfully
        """
        try:
            self.src_path.mkdir(exist_ok=True, parents=True)
            self.docker_path.mkdir(exist_ok=True, parents=True)
            self.config_path.mkdir(exist_ok=True, parents=True)
            return True
        except Exception as e:
            print(f"Error creating framework directories: {e}")
            return False

    def get_project_root(self) -> Path:
        """
        Get the project's root directory.
        
        Returns:
            Path: Project root directory
        """
        return self.base_path

    def get_source_path(self) -> Path:
        """
        Get the project's source directory.
        
        Returns:
            Path: Project source directory
        """
        return self.src_path