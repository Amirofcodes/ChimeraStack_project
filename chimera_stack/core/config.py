"""
Configuration Management Module

Handles configuration loading, validation, and management for development environments.
Supports multiple environment types and framework-specific settings.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass

from chimera_stack.services.databases import (
    MySQLService, PostgreSQLService, MariaDBService
)
from chimera_stack.services.webservers import (
    NginxService, ApacheService
)
from chimera_stack.frameworks.php import (
    LaravelFramework, SymfonyFramework, VanillaPHPFramework
)
from chimera_stack.frameworks.python import (
    DjangoFramework, FlaskFramework, VanillaPythonFramework
)

class ConfigurationManager:
    """Manages configuration for development environments."""

    DEFAULT_CONFIG = {
        'version': '3.8',
        'services': {},
        'networks': {
            'app_network': {
                'driver': 'bridge'
            }
        },
        'volumes': {}
    }

    def __init__(self, project_name: str, base_path: Path):
        self.project_name = project_name
        self.base_path = base_path
        self.config_path = base_path / 'config'
        self.config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()
        self.environment_vars: Dict[str, str] = {
            # PHP Configuration
            'PHP_DISPLAY_ERRORS': '1',
            'PHP_ERROR_REPORTING': 'E_ALL',
            'PHP_MEMORY_LIMIT': '256M',
            'PHP_MAX_EXECUTION_TIME': '30',
            'PHP_POST_MAX_SIZE': '100M',
            'PHP_UPLOAD_MAX_FILESIZE': '100M',
            # Database Configuration
            'DB_CONNECTION': 'mysql',
            'DB_HOST': 'mysql',
            'DB_PORT': '3306',
            'DB_DATABASE': self.project_name,
            'DB_USERNAME': self.project_name,
            'DB_PASSWORD': 'secret',
            'DB_ROOT_PASSWORD': 'rootsecret'
        }

    def initialize_config(
        self,
        language: str,
        framework: str,
        webserver: str,
        database: str,
        environment: str
    ) -> bool:
        """Initialize project configuration and create necessary files."""
        try:
            # Create configuration directory
            self.config_path.mkdir(exist_ok=True, parents=True)

            # Basic project metadata
            self.config.update({
                'language': language,
                'framework': framework,
                'webserver': webserver,
                'database': database,
                'environment': environment
            })

            # Initialize service configurations
            self._initialize_services(language, framework, webserver, database)

            # Normalize configurations
            self._normalize_volume_config()
            self._normalize_network_config()
            self._normalize_env_vars()

            # Save configurations
            self._save_docker_compose()
            self._save_environment_file()
            self._save_env_config(environment)

            return True
        except Exception as e:
            print(f"Error initializing config: {e}")
            return False

    def _normalize_volume_config(self) -> None:
        """Normalize volume configurations to prevent duplicates and ensure consistency."""
        if 'volumes' not in self.config:
            self.config['volumes'] = {}

        # Collect all volume definitions
        normalized_volumes = {}
        for service in self.config.get('services', {}).values():
            if isinstance(service, dict) and 'volumes' in service:
                # Extract volume names from volume mappings
                for volume_mapping in service.get('volumes', []):
                    if ':' in volume_mapping:
                        volume_name = volume_mapping.split(':')[0]
                        # Skip bind mounts (paths starting with . or /)
                        if not volume_name.startswith(('.', '/')):
                            normalized_volumes[volume_name] = {
                                'driver': 'local',
                                'name': f"{self.project_name}_{volume_name}"
                            }

        # Update the main volumes configuration
        self.config['volumes'] = normalized_volumes

    def _normalize_network_config(self) -> None:
        """Normalize network configurations."""
        if 'networks' not in self.config:
            self.config['networks'] = {}

        # Ensure app network exists and is configured consistently
        self.config['networks']['app_network'] = {
            'driver': 'bridge',
            'name': f"{self.project_name}_network"
        }

    def _normalize_env_vars(self) -> None:
        """Organize and normalize environment variables."""
        # Group environment variables by service
        self.environment_vars = {
            # PHP Configuration
            'PHP_DISPLAY_ERRORS': '1',
            'PHP_ERROR_REPORTING': 'E_ALL',
            'PHP_MEMORY_LIMIT': '256M',
            'PHP_MAX_EXECUTION_TIME': '30',
            'PHP_POST_MAX_SIZE': '100M',
            'PHP_UPLOAD_MAX_FILESIZE': '100M',
            'PHP_LOG_LEVEL': 'debug',
            'PHP_LOG_ERRORS': '1',
            'PHP_ERROR_LOG': '/var/log/php-fpm/php_errors.log',

            # Database Configuration
            'DB_CONNECTION': self.config.get('database', 'mysql'),
            'DB_HOST': f"{self.config.get('database', 'mysql')}",
            'DB_PORT': '3306' if self.config.get('database') in ['mysql', 'mariadb'] else '5432',
            'DB_DATABASE': self.project_name,
            'DB_USERNAME': self.project_name,
            'DB_PASSWORD': 'secret',
            'DB_ROOT_PASSWORD': 'rootsecret',

            # Service Configuration
            'COMPOSE_PROJECT_NAME': self.project_name,
            'PROJECT_ROOT': str(self.base_path)
        }

    def _initialize_services(self, language: str, framework: str,
                           webserver: str, database: str) -> None:
        """Initialize service configurations based on selected options."""
        # Initialize database service
        db_service = self._get_database_service(database)
        if db_service:
            self._create_database_config(db_service)

        # Initialize web server service
        web_service = self._get_webserver_service(webserver)
        if web_service:
            self._create_webserver_config(web_service)

        # Initialize framework
        framework_service = self._get_framework_service(language, framework)
        if framework_service:
            self._create_framework_config(framework_service)

    def _get_database_service(self, database: str):
        """Get appropriate database service instance."""
        services = {
            'mysql': MySQLService,
            'postgresql': PostgreSQLService,
            'mariadb': MariaDBService
        }
        service_class = services.get(database)
        if service_class:
            return service_class(self.project_name, self.base_path)
        return None

    def _get_webserver_service(self, webserver: str):
        """Get appropriate web server service instance."""
        services = {
            'nginx': NginxService,
            'apache': ApacheService
        }
        service_class = services.get(webserver)
        if service_class:
            return service_class(self.project_name, self.base_path)
        return None

    def _get_framework_service(self, language: str, framework: str):
        """Get appropriate framework service instance."""
        frameworks = {
            'php': {
                'laravel': LaravelFramework,
                'symfony': SymfonyFramework,
                'none': VanillaPHPFramework
            },
            'python': {
                'django': DjangoFramework,
                'flask': FlaskFramework,
                'none': VanillaPythonFramework
            }
        }
        if language in frameworks and framework in frameworks[language]:
            framework_class = frameworks[language][framework]
            return framework_class(self.project_name, self.base_path)
        return None

    def _create_database_config(self, service) -> None:
        """Create database configuration files."""
        docker_path = self.base_path / 'docker' / 'database'
        docker_path.mkdir(parents=True, exist_ok=True)
        
        # Generate service configuration
        config = service.get_docker_config()
        self.config['services'].update(config.get('services', {}))
        
        if 'volumes' in config:
            self.config['volumes'].update(config.get('volumes', {}))
        
        # Generate configuration files
        service.generate_server_config()

    def _create_webserver_config(self, service) -> None:
        """Create web server configuration files."""
        docker_path = self.base_path / 'docker' / 'webserver'
        docker_path.mkdir(parents=True, exist_ok=True)
        
        # Generate service configuration
        config = service.get_docker_config()
        self.config['services'].update(config.get('services', {}))
        
        # Generate configuration files
        service.generate_server_config()

    def _create_framework_config(self, service) -> None:
        """Create framework-specific configuration files."""
        # Initialize framework project
        service.initialize_project()
        
        # Generate framework configuration
        config = service.configure_docker()
        self.config['services'].update(config.get('services', {}))
        
        if 'volumes' in config:
            self.config['volumes'].update(config.get('volumes', {}))
        
        # Set up development environment
        service.setup_development_environment()

    def _save_docker_compose(self) -> None:
        """Save Docker Compose configuration file."""
        # Create a clean configuration for docker-compose
        compose_config = {
            'services': self.config['services'],
            'networks': self.config['networks'],
            'volumes': self.config['volumes']
        }

        # Remove any empty configurations
        for key in list(compose_config.keys()):
            if not compose_config[key]:
                del compose_config[key]

        docker_compose_path = self.base_path / 'docker-compose.yml'
        with open(docker_compose_path, 'w') as f:
            yaml.dump(compose_config, f, sort_keys=False)

    def _save_environment_file(self) -> None:
        """Save environment variables file."""
        env_path = self.base_path / '.env'
        env_content = []
        
        # Add PHP environment variables
        env_content.append("# PHP Configuration")
        for key in ['PHP_DISPLAY_ERRORS', 'PHP_ERROR_REPORTING', 'PHP_MEMORY_LIMIT',
                   'PHP_MAX_EXECUTION_TIME', 'PHP_POST_MAX_SIZE', 'PHP_UPLOAD_MAX_FILESIZE']:
            env_content.append(f"{key}={self.environment_vars[key]}")
        
        # Add database environment variables
        env_content.append("\n# Database Configuration")
        for key in ['DB_CONNECTION', 'DB_HOST', 'DB_PORT', 'DB_DATABASE',
                   'DB_USERNAME', 'DB_PASSWORD', 'DB_ROOT_PASSWORD']:
            env_content.append(f"{key}={self.environment_vars[key]}")
        
        with open(env_path, 'w') as f:
            f.write('\n'.join(env_content))

    def load_config(self, environment: str = 'development') -> bool:
        """Load configuration for specified environment."""
        try:
            config_file = self.config_path / f'{environment}.yaml'
            
            if config_file.exists():
                with open(config_file, 'r') as f:
                    env_config = yaml.safe_load(f)
                self.config.update(env_config)
            
            return True
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False

    def save_config(self, environment: str = 'development') -> bool:
        """Save current configuration to file."""
        try:
            config_file = self.config_path / f'{environment}.yaml'
            with open(config_file, 'w') as f:
                yaml.safe_dump(self.config, f)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def _save_env_config(self, environment: str) -> None:
        """Save environment-specific configuration."""
        env_config = {
            'project': {
                'name': self.project_name,
                'language': self.config.get('language'),
                'framework': self.config.get('framework'),
                'environment': environment
            },
            'services': {
                name: self._clean_service_config(config)
                for name, config in self.config.get('services', {}).items()
            },
            'volumes': self.config.get('volumes', {}),
            'networks': self.config.get('networks', {})
        }

        config_file = self.config_path / f'{environment}.yaml'
        with open(config_file, 'w') as f:
            yaml.safe_dump(env_config, f, sort_keys=False)

    def _clean_service_config(self, config: Dict) -> Dict:
        """Clean service configuration for environment file."""
        # Remove build context and other docker-compose specific fields
        cleaned = config.copy()
        keys_to_remove = ['build', 'user', 'restart']
        for key in keys_to_remove:
            cleaned.pop(key, None)
        return cleaned