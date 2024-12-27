"""
Base Database Service Implementation

Provides the foundation for all database service handlers, ensuring consistent
configuration and management across different database systems. This implementation
establishes standard interfaces and shared functionality for database services.
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

    def get_volume_name(self, service_name: str = None) -> str:
        """Generate a consistent volume name for the database.
        
        Args:
            service_name: Optional service identifier. If not provided, uses the database type.
        
        Returns:
            str: Consistent volume name for the service
        """
        if not service_name:
            service_name = self.__class__.__name__.lower().replace('service', '')
        return f"{service_name}_data"

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
                    'driver': 'local'
                }
            }
        }

    def generate_connection_string(self) -> str:
        """Generate a connection string for the database."""
        pass

    def get_health_check(self) -> Dict[str, Any]:
        """Generate health check configuration for the database service."""
        pass