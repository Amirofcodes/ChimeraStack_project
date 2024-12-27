"""
Base Web Server Service Implementation

Defines the core interface and shared functionality for web server services,
ensuring consistent configuration and management across different web server
implementations.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional

class BaseWebServer(ABC):
    """Abstract base class for web server implementations."""

    def __init__(self, project_name: str, base_path: Path):
        self.project_name = project_name
        self.base_path = base_path
        self.config: Dict[str, Any] = {}
        self.ssl_enabled = False
        self._allocated_ports: List[int] = []

    @abstractmethod
    def get_docker_config(self) -> Dict[str, Any]:
        """Generate Docker service configuration for the web server."""
        pass

    @abstractmethod
    def generate_server_config(self) -> bool:
        """Generate server-specific configuration files."""
        pass

    def create_directory(self, path: Path) -> bool:
        """Create a directory if it doesn't exist."""
        try:
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {path}: {e}")
            return False

    def _get_available_port(self, start_port: int, end_port: int) -> int:
        """Find an available port in the specified range."""
        import socket
        for port in range(start_port, end_port + 1):
            if port in self._allocated_ports:
                continue
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('', port))
                    self._allocated_ports.append(port)
                    return port
                except OSError:
                    continue
        return start_port  # Fallback to default if no ports are available

    def get_allocated_ports(self) -> List[int]:
        """Return list of ports allocated by this service."""
        return self._allocated_ports.copy()

    def release_ports(self) -> None:
        """Release all allocated ports."""
        self._allocated_ports.clear()

    def _uses_php(self) -> bool:
        """Determine if the project uses PHP."""
        return False