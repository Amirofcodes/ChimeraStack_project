# src/services/databases/mysql.py

"""
MySQL Database Service Implementation

Provides specialized configuration and management for MySQL database services
in development environments. This implementation includes optimizations and 
configurations suitable for development and production use.
"""

from pathlib import Path
from typing import Dict, Any
from .base import BaseDatabase

class MySQLService(BaseDatabase):
    """MySQL database service implementation."""

    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.config.update({
            'image': 'mysql:8.0',
            'command': '--default-authentication-plugin=mysql_native_password',
            'restart': 'unless-stopped'
        })

    def get_docker_config(self) -> Dict[str, Any]:
        """Generate Docker service configuration for MySQL."""
        volume_name = f"{self.project_name}_mysql_data"
        
        config = {
            'services': {
                'mysql': {
                    **self.config,
                    'ports': [f"{self.get_default_port()}:3306"],
                    'environment': self.get_environment_variables(),
                    'volumes': [
                        f"{volume_name}:/var/lib/mysql"
                    ],
                    'healthcheck': self.get_health_check()
                }
            },
            'volumes': {
                volume_name: None
            }
        }
        
        # Add custom MySQL configuration
        self._create_mysql_config()
        
        return config

    def get_default_port(self) -> int:
        """Return the default port for MySQL."""
        return 3306

    def get_environment_variables(self) -> Dict[str, str]:
        """Return required environment variables for MySQL."""
        return {
            'MYSQL_DATABASE': '${DB_NAME}',
            'MYSQL_USER': '${DB_USER}',
            'MYSQL_PASSWORD': '${DB_PASSWORD}',
            'MYSQL_ROOT_PASSWORD': '${DB_ROOT_PASSWORD}'
        }

    def get_health_check(self) -> Dict[str, Any]:
        """Generate health check configuration for MySQL."""
        return {
            'test': ["CMD", "mysqladmin", "ping", "-h", "localhost"],
            'interval': '10s',
            'timeout': '5s',
            'retries': 5
        }

    def generate_connection_string(self) -> str:
        """Generate a MySQL connection string."""
        return 'mysql://${DB_USER}:${DB_PASSWORD}@mysql:3306/${DB_NAME}'

    def _create_mysql_config(self) -> None:
        """Create custom MySQL configuration file."""
        mysql_config = """
[mysqld]
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
default-authentication-plugin = mysql_native_password
max_allowed_packet = 64M
sql_mode = STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION

[mysql]
default-character-set = utf8mb4

[client]
default-character-set = utf8mb4
"""
        config_path = self.base_path / self.project_name / 'docker' / 'mysql'
        config_path.mkdir(parents=True, exist_ok=True)
        (config_path / 'my.cnf').write_text(mysql_config.strip())