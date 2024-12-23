# src/services/databases/base.py

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

    def generate_connection_string(self) -> str:
        """Generate a connection string for the database."""
        pass

    def get_data_volume_config(self) -> Dict[str, Any]:
        """Generate volume configuration for persistent data storage."""
        volume_name = f"{self.project_name}_db_data"
        return {
            'volumes': {
                volume_name: {
                    'driver': 'local'
                }
            }
        }

    def get_health_check(self) -> Dict[str, Any]:
        """Generate health check configuration for the database service."""
        pass