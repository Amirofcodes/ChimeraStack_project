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
                        f"{volume_name}:/var/lib/mysql",
                        "./docker/mysql/my.cnf:/etc/mysql/conf.d/my.cnf:ro"
                    ],
                    'healthcheck': self.get_health_check()
                }
            },
            'volumes': {
                volume_name: None
            }
        }
        
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
            'retries': 5,
            'start_period': '30s'
        }

    def generate_connection_string(self) -> str:
        """Generate a MySQL connection string."""
        return 'mysql://${DB_USER}:${DB_PASSWORD}@mysql:3306/${DB_NAME}'

    def generate_server_config(self) -> bool:
        """Generate server-specific configuration files."""
        try:
            config_path = self.base_path / 'docker' / 'mysql'
            config_path.mkdir(parents=True, exist_ok=True)
            
            # Create MySQL configuration
            mysql_config = """
[mysqld]
# Character Set Configuration
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
default-authentication-plugin = mysql_native_password

# Connection and Thread Settings
max_connections = 100
thread_cache_size = 8
thread_stack = 256K

# Buffer Pool Configuration
innodb_buffer_pool_size = 256M
innodb_buffer_pool_instances = 4
innodb_log_file_size = 64M
innodb_flush_method = O_DIRECT
innodb_flush_log_at_trx_commit = 2

# Query Cache Configuration
query_cache_type = 1
query_cache_limit = 1M
query_cache_size = 16M

# Temporary Table Settings
tmp_table_size = 32M
max_heap_table_size = 32M

# General Settings
max_allowed_packet = 64M
sql_mode = STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION

# InnoDB Settings
innodb_file_per_table = 1
innodb_strict_mode = 1

# Logging Configuration
slow_query_log = 1
slow_query_log_file = /var/log/mysql/mysql-slow.log
long_query_time = 2

[mysql]
default-character-set = utf8mb4

[client]
default-character-set = utf8mb4
"""
            (config_path / 'my.cnf').write_text(mysql_config.strip())
            
            return True
        except Exception as e:
            print(f"Error generating MySQL configuration: {e}")
            return False

    def get_backup_config(self) -> Dict[str, Any]:
        """Generate backup configuration for MySQL."""
        return {
            'services': {
                'mysql-backup': {
                    'image': 'databack/mysql-backup',
                    'environment': {
                        'DB_DUMP_TARGET': '/backup',
                        'DB_USER': '${DB_USER}',
                        'DB_PASS': '${DB_PASSWORD}',
                        'DB_DUMP_FREQ': '24',
                        'DB_DUMP_BEGIN': '0000',
                        'DB_SERVER': 'mysql'
                    },
                    'volumes': [
                        './backups:/backup'
                    ],
                    'depends_on': ['mysql']
                }
            }
        }