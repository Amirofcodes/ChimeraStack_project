"""
MariaDB Database Service Implementation

Provides specialized configuration and management for MariaDB database services.
This implementation focuses on MySQL compatibility while leveraging MariaDB-specific
optimizations and features for development environments.
"""

from pathlib import Path
from typing import Dict, Any
from .base import BaseDatabase

class MariaDBService(BaseDatabase):
    """MariaDB database service implementation."""

    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.config.update({
            'image': 'mariadb:10.11',  # Latest stable version
            'restart': 'unless-stopped',
            'command': '--character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci'
        })

    def get_docker_config(self) -> Dict[str, Any]:
        """Generate Docker service configuration for MariaDB."""
        volume_name = f"{self.project_name}_mariadb_data"
        port = self._get_available_port(3306, 3400)  # Try ports between 3306 and 3400

        config = {
            'services': {
                'mariadb': {
                    **self.config,
                    'ports': [f"{port}:3306"],
                    'environment': self.get_environment_variables(),
                    'volumes': [
                        f"{volume_name}:/var/lib/mysql",
                        "./docker/mariadb/conf.d:/etc/mysql/conf.d:ro",
                        "./docker/mariadb/init:/docker-entrypoint-initdb.d:ro"
                    ],
                    'healthcheck': self.get_health_check()
                }
            },
            'volumes': {
                volume_name: None
            }
        }

        return config

    def _get_available_port(self, start_port: int, end_port: int) -> int:
        """Find an available port in the specified range."""
        import socket
        for port in range(start_port, end_port + 1):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('', port))
                    return port
                except OSError:
                    continue
        return start_port  # Fallback to default if no ports are available

    def get_default_port(self) -> int:
        """Return the default port for MariaDB."""
        return 3306

    def get_environment_variables(self) -> Dict[str, str]:
        """Return required environment variables for MariaDB."""
        return {
            'MARIADB_DATABASE': '${DB_NAME}',
            'MARIADB_USER': '${DB_USER}',
            'MARIADB_PASSWORD': '${DB_PASSWORD}',
            'MARIADB_ROOT_PASSWORD': '${DB_ROOT_PASSWORD}',
            'TZ': 'UTC'
        }

    def get_health_check(self) -> Dict[str, Any]:
        """Generate health check configuration for MariaDB."""
        return {
            'test': ['CMD', 'healthcheck.sh', '--connect', '--innodb_initialized'],
            'interval': '10s',
            'timeout': '5s',
            'retries': 3,
            'start_period': '30s'
        }

    def generate_connection_string(self) -> str:
        """Generate a MariaDB connection string."""
        return 'mysql://${DB_USER}:${DB_PASSWORD}@mariadb:3306/${DB_NAME}'

    def _create_mariadb_config(self) -> None:
        """Create MariaDB configuration files and initialization scripts."""
        config_path = self.base_path / self.project_name / 'docker' / 'mariadb'
        config_path.mkdir(parents=True, exist_ok=True)

        # Create configuration directory
        conf_d_path = config_path / 'conf.d'
        conf_d_path.mkdir(exist_ok=True)

        # Create custom configuration
        server_config = """
[mysqld]
# Performance Optimization
innodb_buffer_pool_size = 256M
innodb_log_file_size = 64M
innodb_flush_log_at_trx_commit = 2
innodb_flush_method = O_DIRECT

# Connection and Thread Settings
max_connections = 100
thread_cache_size = 8
thread_stack = 256K

# Query Cache Configuration
query_cache_type = 1
query_cache_limit = 1M
query_cache_size = 16M

# Character Set Configuration
character_set_server = utf8mb4
collation_server = utf8mb4_unicode_ci

# InnoDB Settings
innodb_file_per_table = 1
innodb_strict_mode = 1

# Logging Configuration
slow_query_log = 1
slow_query_log_file = /var/log/mysql/mariadb-slow.log
long_query_time = 2
"""
        (conf_d_path / 'server.cnf').write_text(server_config.strip())

        # Create initialization directory
        init_path = config_path / 'init'
        init_path.mkdir(exist_ok=True)

        # Create initialization script
        init_script = """
#!/bin/bash
set -e

mysql -u root -p${MARIADB_ROOT_PASSWORD} <<-EOSQL
    SET GLOBAL log_bin_trust_function_creators = 1;
    SET GLOBAL max_allowed_packet = 64 * 1024 * 1024;
    
    # Create additional databases if needed
    # CREATE DATABASE IF NOT EXISTS test_db;
    # GRANT ALL ON test_db.* TO '${MARIADB_USER}'@'%';
    
    FLUSH PRIVILEGES;
EOSQL
"""
        (init_path / '01_init_db.sh').write_text(init_script.strip())

    def get_backup_config(self) -> Dict[str, Any]:
        """Generate backup configuration for MariaDB."""
        return {
            'services': {
                'mariadb-backup': {
                    'image': 'mariadb:10.11',
                    'command': '/backup.sh',
                    'volumes': [
                        './backups:/backups',
                        './docker/mariadb/scripts/backup.sh:/backup.sh:ro'
                    ],
                    'environment': {
                        'MARIADB_HOST': 'mariadb',
                        'MARIADB_DATABASE': '${DB_NAME}',
                        'MARIADB_USER': '${DB_USER}',
                        'MARIADB_PASSWORD': '${DB_PASSWORD}',
                        'BACKUP_KEEP_DAYS': '7',
                        'BACKUP_KEEP_WEEKS': '4',
                        'BACKUP_KEEP_MONTHS': '6'
                    },
                    'depends_on': ['mariadb']
                }
            }
        }