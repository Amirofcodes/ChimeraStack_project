# src/services/databases/postgresql.py

"""
PostgreSQL Database Service Implementation

Provides specialized configuration and management for PostgreSQL database services
in development environments. This implementation includes optimizations and 
best practices for both development and production scenarios.
"""

from pathlib import Path
from typing import Dict, Any
from .base import BaseDatabase

class PostgreSQLService(BaseDatabase):
    """PostgreSQL database service implementation."""

    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.config.update({
            'image': 'postgres:13',
            'restart': 'unless-stopped',
            'shm_size': '256mb'  # Shared memory for better performance
        })

    def get_docker_config(self) -> Dict[str, Any]:
        """Generate Docker service configuration for PostgreSQL."""
        volume_name = f"{self.project_name}_postgres_data"
        
        config = {
            'services': {
                'postgres': {
                    **self.config,
                    'ports': [f"{self.get_default_port()}:5432"],
                    'environment': self.get_environment_variables(),
                    'volumes': [
                        f"{volume_name}:/var/lib/postgresql/data",
                        "./docker/postgres/init:/docker-entrypoint-initdb.d:ro"
                    ],
                    'healthcheck': self.get_health_check()
                }
            },
            'volumes': {
                volume_name: None
            }
        }

        # Set up PostgreSQL configuration
        self._create_postgresql_config()
        
        return config

    def get_default_port(self) -> int:
        """Return the default port for PostgreSQL."""
        return 5432

    def get_environment_variables(self) -> Dict[str, str]:
        """Return required environment variables for PostgreSQL."""
        return {
            'POSTGRES_DB': '${DB_NAME}',
            'POSTGRES_USER': '${DB_USER}',
            'POSTGRES_PASSWORD': '${DB_PASSWORD}',
            'POSTGRES_HOST_AUTH_METHOD': 'scram-sha-256',
            'POSTGRES_INITDB_ARGS': '--auth-host=scram-sha-256'
        }

    def get_health_check(self) -> Dict[str, Any]:
        """Generate health check configuration for PostgreSQL."""
        return {
            'test': ['CMD-SHELL', 'pg_isready -U ${DB_USER} -d ${DB_NAME}'],
            'interval': '10s',
            'timeout': '5s',
            'retries': 5,
            'start_period': '30s'
        }

    def generate_connection_string(self) -> str:
        """Generate a PostgreSQL connection string."""
        return 'postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}'

    def _create_postgresql_config(self) -> None:
        """Create PostgreSQL configuration files and initialization scripts."""
        config_path = self.base_path / self.project_name / 'docker' / 'postgres'
        config_path.mkdir(parents=True, exist_ok=True)
        
        # Create initialization directory
        init_path = config_path / 'init'
        init_path.mkdir(exist_ok=True)

        # Create initial setup script
        init_script = """
#!/bin/bash
set -e

# Enable required extensions
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "hstore";
    CREATE EXTENSION IF NOT EXISTS "citext";
EOSQL
"""
        (init_path / '01_init_extensions.sh').write_text(init_script.strip())

        # Create PostgreSQL configuration
        postgres_config = """
# Memory configuration
shared_buffers = '128MB'
effective_cache_size = '512MB'
work_mem = '16MB'
maintenance_work_mem = '128MB'

# Query tuning
random_page_cost = 1.1
effective_io_concurrency = 200

# Checkpoint configuration
checkpoint_completion_target = 0.9
max_wal_size = '2GB'
min_wal_size = '1GB'

# Connection settings
listen_addresses = '*'
max_connections = 100

# Logging
log_timezone = 'UTC'
log_statement = 'none'
log_min_duration_statement = 2000
log_min_error_statement = 'error'
"""
        (config_path / 'postgresql.conf').write_text(postgres_config.strip())

        # Create access configuration
        pg_hba_config = """
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all            all                                     scram-sha-256
host    all            all             0.0.0.0/0              scram-sha-256
host    all            all             ::/0                    scram-sha-256
"""
        (config_path / 'pg_hba.conf').write_text(pg_hba_config.strip())

    def get_backup_config(self) -> Dict[str, Any]:
        """Generate backup configuration for PostgreSQL."""
        return {
            'services': {
                'postgres-backup': {
                    'image': 'prodrigestivill/postgres-backup-local',
                    'restart': 'unless-stopped',
                    'volumes': [
                        './backups:/backups'
                    ],
                    'environment': {
                        'POSTGRES_HOST': 'postgres',
                        'POSTGRES_DB': '${DB_NAME}',
                        'POSTGRES_USER': '${DB_USER}',
                        'POSTGRES_PASSWORD': '${DB_PASSWORD}',
                        'SCHEDULE': '@daily',
                        'BACKUP_KEEP_DAYS': '7',
                        'BACKUP_KEEP_WEEKS': '4',
                        'BACKUP_KEEP_MONTHS': '6'
                    },
                    'depends_on': ['postgres']
                }
            }
        }