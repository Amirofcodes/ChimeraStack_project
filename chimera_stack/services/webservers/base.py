"""
Base Web Server Service Implementation

Defines the core interface and shared functionality for web server services,
ensuring consistent configuration and management across different web server
implementations.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

class BaseWebServer(ABC):
    """Abstract base class for web server implementations."""

    def __init__(self, project_name: str, base_path: Path):
        self.project_name = project_name
        self.base_path = base_path
        self.config: Dict[str, Any] = {}
        self.ssl_enabled = False
        self.ssl_certificate: Optional[str] = None
        self.ssl_key: Optional[str] = None
        self._allocated_ports: List[int] = []

    @abstractmethod
    def get_docker_config(self) -> Dict[str, Any]:
        """Generate Docker service configuration for the web server."""
        pass

    @abstractmethod
    def generate_server_config(self) -> None:
        """Generate server-specific configuration files."""
        pass

    def enable_ssl(self, certificate_path: str, key_path: str) -> None:
        """Enable SSL/TLS support for the web server."""
        self.ssl_enabled = True
        self.ssl_certificate = certificate_path
        self.ssl_key = key_path

    def get_default_ports(self) -> Dict[str, int]:
        """Return default ports for the web server."""
        return {
            'http': 8000,
            'https': 8443
        }

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
        # This should be implemented by child classes or moved to a project config
        return True

    def _get_php_location(self) -> str:
        """Generate PHP location configuration."""
        return r"""
    location ~ \.php$ {
        fastcgi_pass php:9000;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
        fastcgi_intercept_errors on;
        fastcgi_buffer_size 16k;
        fastcgi_buffers 4 16k;
    }
"""