"""
Base Database Service Implementation

Provides the foundation for all database service handlers, ensuring consistent
configuration and management across different database systems.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional

class BaseDatabase(ABC):
    """Abstract base class for database service implementations."""

    def __init__(self, project_name: str, base_path: Path):
        self.project_name = project_name
        self.base_path = base_path
        self.config: Dict[str, Any] = {}

    @abstractmethod
    def get_docker_config(self) -> Dict[str, Any]:
        """Generate Docker service configuration for the database."""
        pass

    @abstractmethod
    def get_default_port(self) -> int:
        """Return the default port for the database service."""
        pass

    @abstractmethod
    def get_environment_variables(self) -> Dict[str, str]:
        """Return required environment variables for the database service."""
        pass

    def create_directory(self, path: Path, required: bool = False) -> bool:
        """
        Safely create a directory.

        Args:
            path: Path to create
            required: If True, directory will be created even if empty

        Returns:
            bool: True if directory was created successfully
        """
        try:
            # Only create directory if it's required or has content
            if required or any(path.iterdir()) if path.exists() else required:
                if not path.exists():
                    path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {path}: {e}")
            return False

    def get_volume_name(self, service_name: str = None) -> str:
        """Generate a consistent volume name for the database.

        Args:
            service_name: Optional service identifier. If not provided, uses the database type.

        Returns:
            str: Consistent volume name for the service
        """
        if not service_name:
            service_name = self.__class__.__name__.lower().replace('service', '')
        return f"{self.project_name}_{service_name}_data"

    def get_data_volume_config(self, volume_name: Optional[str] = None) -> Dict[str, Any]:
        """Generate volume configuration for persistent data storage.

        Args:
            volume_name: Optional volume name override.

        Returns:
            Dict[str, Any]: Volume configuration dictionary
        """
        volume_name = volume_name or self.get_volume_name()
        return {
            'volumes': {
                volume_name: {
                    'driver': 'local',
                    'name': f"{self.project_name}_{volume_name}"
                }
            }
        }