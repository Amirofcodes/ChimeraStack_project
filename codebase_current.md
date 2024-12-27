# .gitignore

```
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
#   For a library or package, you might want to ignore these files since the code is
#   intended to run in multiple environments; otherwise, check them in:
# .python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# UV
#   Similar to Pipfile.lock, it is generally recommended to include uv.lock in version control.
#   This is especially recommended for binary packages to ensure reproducibility, and is more
#   commonly ignored for libraries.
#uv.lock

# poetry
#   Similar to Pipfile.lock, it is generally recommended to include poetry.lock in version control.
#   This is especially recommended for binary packages to ensure reproducibility, and is more
#   commonly ignored for libraries.
#   https://python-poetry.org/docs/basic-usage/#commit-your-poetrylock-file-to-version-control
#poetry.lock

# pdm
#   Similar to Pipfile.lock, it is generally recommended to include pdm.lock in version control.
#pdm.lock
#   pdm stores project-wide configurations in .pdm.toml, but it is recommended to not include it
#   in version control.
#   https://pdm.fming.dev/latest/usage/project/#working-with-version-control
.pdm.toml
.pdm-python
.pdm-build/

# PEP 582; used by e.g. github.com/David-OConnor/pyflow and github.com/pdm-project/pdm
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
#  JetBrains specific template is maintained in a separate JetBrains.gitignore that can
#  be found at https://github.com/github/gitignore/blob/main/Global/JetBrains.gitignore
#  and can be added to the global gitignore or merged into this file.  For a more nuclear
#  option (not recommended) you can uncomment the following to ignore the entire idea folder.
#.idea/

# PyPI configuration file
.pypirc


```

# chimera_stack/**init**.py

```py
# src/__init__.py
"""
ChimeraStack

A Docker-centric tool for creating consistent development environments.
"""

__version__ = "0.1.0"
__author__ = "Amirofcodes"
__license__ = "MIT"

from .core import Environment, ConfigurationManager, DockerManager
from .cli import cli

__all__ = ['Environment', 'ConfigurationManager', 'DockerManager', 'cli']
```

# chimera_stack/cli.py

```py
"""
Command Line Interface Module

Provides the main CLI functionality for ChimeraStack, including project creation,
management, and tool information.
"""

import click
from pathlib import Path
from typing import Dict, Any

from chimera_stack.core.config import ConfigurationManager
from chimera_stack.core.environment import Environment
from chimera_stack.core.docker_manager import DockerManager
from chimera_stack.core.setup_wizard import SetupWizard

# Tool information
AUTHOR = "Jaouad Bouddehbine (Amirofcodes)"
REPOSITORY = "https://github.com/Amirofcodes/chimera-stack"
VERSION = "0.1.0"

def print_version(ctx, param, value):
    """Print version information callback."""
    if not value or ctx.resilient_parsing:
        return
    click.echo(f"ChimeraStack v{VERSION}")
    click.echo(f"Author: {AUTHOR}")
    click.echo(f"Repository: {REPOSITORY}")
    ctx.exit()

@click.group(help="ChimeraStack - A Docker-centric Development Environment Management Tool\n\n"
                  "Created by Jaouad Bouddehbine (Amirofcodes)\n"
                  "Repository: https://github.com/Amirofcodes/chimera-stack")
@click.option('--version', is_flag=True, callback=print_version, expose_value=False,
              is_eager=True, help="Show the version and exit.")
def cli():
    """ChimeraStack CLI entry point."""
    pass

@cli.command()
def init():
    """Interactive guided setup for your development environment."""
    try:
        wizard = SetupWizard()
        config = wizard.run_setup()

        if config:
            create_project(**config)

    except Exception as e:
        raise click.ClickException(str(e))

@cli.command()
@click.argument('project_name')
@click.option('--language', type=click.Choice(['php', 'python']), required=True,
              help='Primary programming language for the project')
@click.option('--framework',
              type=click.Choice(['none', 'laravel', 'symfony', 'flask', 'django']),
              default='none',
              help='Web framework to use')
@click.option('--webserver',
              type=click.Choice(['nginx', 'apache']),
              default='nginx',
              help='Web server for the project')
@click.option('--database',
              type=click.Choice(['mysql', 'postgresql', 'mariadb']),
              default='mysql',
              help='Database system to use')
@click.option('--env',
              type=click.Choice(['development', 'testing', 'production']),
              default='development',
              help='Environment type')
def create(project_name: str, language: str, framework: str,
          webserver: str, database: str, env: str):
    """Create a new development environment using specified options."""
    create_project(project_name=project_name, language=language,
                  framework=framework, webserver=webserver,
                  database=database, env=env)

@cli.command()
@click.argument('project_name')
def start(project_name: str):
    """Start an existing development environment."""
    try:
        project_path = Path.cwd() / project_name
        if not project_path.exists():
            raise click.ClickException(f"Project {project_name} not found")

        click.echo(f"Starting {project_name} environment...")
        docker_manager = DockerManager(project_name, project_path)
        if docker_manager.start_environment():
            click.echo(f"✨ Environment {project_name} started successfully!")
        else:
            raise click.ClickException("Failed to start environment")

    except Exception as e:
        raise click.ClickException(str(e))

@cli.command()
@click.argument('project_name')
def stop(project_name: str):
    """Stop a running development environment."""
    try:
        project_path = Path.cwd() / project_name
        if not project_path.exists():
            raise click.ClickException(f"Project {project_name} not found")

        click.echo(f"Stopping {project_name} environment...")
        docker_manager = DockerManager(project_name, project_path)
        if docker_manager.stop_environment():
            click.echo(f"✨ Environment {project_name} stopped successfully!")
        else:
            raise click.ClickException("Failed to stop environment")

    except Exception as e:
        raise click.ClickException(str(e))

@cli.command()
def info():
    """Display information about ChimeraStack."""
    click.echo("\nChimeraStack - Docker Development Environment Tool")
    click.echo("=" * 50)
    click.echo(f"Version: {VERSION}")
    click.echo(f"Author: {AUTHOR}")
    click.echo(f"Repository: {REPOSITORY}")
    click.echo("\nSupported Languages:")
    click.echo("  - PHP (Laravel, Symfony, Vanilla)")
    click.echo("  - Python (Django, Flask, Vanilla)")
    click.echo("\nSupported Services:")
    click.echo("  - Web Servers: Nginx, Apache")
    click.echo("  - Databases: MySQL, PostgreSQL, MariaDB")
    click.echo("  - Additional: Redis, Logging, Monitoring")
    click.echo("\nFor more information, visit the repository.")

def create_project(project_name: str, language: str, framework: str,
                  webserver: str, database: str, env: str):
    """Common project creation logic used by both init and create commands."""
    try:
        project_path = Path.cwd() / project_name

        if project_path.exists():
            raise click.ClickException(f"Project directory '{project_name}' already exists")

        click.echo(f"\nCreating project: {project_name}")
        click.echo(f"Configuration:")
        click.echo(f"  Language:   {language}")
        click.echo(f"  Framework:  {framework}")
        click.echo(f"  Web Server: {webserver}")
        click.echo(f"  Database:   {database}")
        click.echo(f"  Environment:{env}")

        # Initialize environment
        environment = Environment(project_name, project_path)
        if not environment.setup():
            raise click.ClickException("Failed to create project directory structure")

        click.echo("\nInitializing project structure...")

        # Setup configuration
        config_manager = ConfigurationManager(project_name, project_path)
        if not config_manager.initialize_config(
            language=language,
            framework=framework,
            webserver=webserver,
            database=database,
            environment=env
        ):
            raise click.ClickException("Failed to initialize project configuration")

        click.echo("Project configuration created successfully")

        # Setup Docker resources
        docker_manager = DockerManager(project_name, project_path)
        if not docker_manager.verify_docker_installation():
            raise click.ClickException("Docker is not available")

        try:
            docker_manager.create_network()
            click.echo("Docker network created successfully")
        except Exception as e:
            click.echo(f"Warning: {str(e)}")
            click.echo("Using existing network...")

        try:
            docker_manager.create_volume()
            click.echo("Docker volume created successfully")
        except Exception as e:
            click.echo(f"Warning: {str(e)}")
            click.echo("Using existing volume...")

        click.echo(f"\n✨ Project {project_name} created successfully!")
        click.echo("\nNext steps:")
        click.echo(f"  1. cd {project_name}")
        click.echo(f"  2. docker-compose up -d")

    except Exception as e:
        if 'environment' in locals():
            environment.cleanup()
        raise click.ClickException(str(e))

if __name__ == '__main__':
    cli()
```

# chimera_stack/core/**init**.py

```py
"""
DevStack Factory Core Module

This module provides the core functionality for creating and managing
development environments using Docker containers.
"""

__version__ = "0.1.0"
__author__ = "Jaouad Bouddehbine"
__license__ = "MIT"

from typing import Dict, List, Optional, Union
from .environment import Environment
from .config import ConfigurationManager
from .docker_manager import DockerManager
from .setup_wizard import SetupWizard

__all__ = [
    "Environment",
    "ConfigurationManager",
    "DockerManager",
    "SetupWizard",
]
```

# chimera_stack/core/config.py

```py
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

            # Update base configuration
            self.config.update({
                'language': language,
                'framework': framework,
                'webserver': webserver,
                'database': database,
                'environment': environment
            })

            # Initialize service configurations
            self._initialize_services(language, framework, webserver, database)

            # Normalize and merge volume configurations
            self._normalize_volume_config()

            # Save configurations
            self._save_docker_compose()
            self._save_environment_file()
            self.save_config(environment)

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
                for volume_mapping in service['volumes']:
                    if ':' in volume_mapping:
                        volume_name = volume_mapping.split(':')[0]
                        if volume_name.startswith('./') or volume_name.startswith('/'):
                            continue  # Skip bind mounts
                        normalized_volumes[volume_name] = {'driver': 'local'}

        # Update the main volumes configuration
        self.config['volumes'] = normalized_volumes

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
        # Clean up configuration for docker-compose format
        compose_config = {
            'version': self.config['version'],
            'services': self.config['services'],
            'networks': self.config['networks'],
            'volumes': self.config['volumes']
        }

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
```

# chimera_stack/core/docker_manager.py

```py
"""
Docker Management Module

Handles Docker operations including container management, network setup,
and volume handling for development environments.
"""

import subprocess
from pathlib import Path
from typing import Dict, List, Optional

class DockerManager:
    """Manages Docker operations for development environments."""

    def __init__(self, project_name: str, base_path: Path):
        self.project_name = project_name
        self.base_path = base_path
        self.networks: Dict = {}
        self.volumes: Dict = {}

    def verify_docker_installation(self) -> bool:
        """Verify Docker is installed and running."""
        try:
            subprocess.run(['docker', 'info'], capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def create_network(self, network_name: Optional[str] = None) -> bool:
        """Create a Docker network for the project."""
        try:
            name = network_name or f"{self.project_name}_network"
            result = subprocess.run(
                ['docker', 'network', 'create', name],
                capture_output=True,
                text=True,
                check=True
            )
            self.networks[name] = name
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error creating network: {e.stderr}")
            return False

    def create_volume(self, volume_name: Optional[str] = None) -> bool:
        """Create a Docker volume for persistent data."""
        try:
            name = volume_name or f"{self.project_name}_data"
            result = subprocess.run(
                ['docker', 'volume', 'create', name],
                capture_output=True,
                text=True,
                check=True
            )
            self.volumes[name] = name
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error creating volume: {e.stderr}")
            return False

    def start_environment(self) -> bool:
        """Start the Docker environment using docker-compose."""
        try:
            result = subprocess.run(
                ['docker-compose', 'up', '-d'],
                cwd=self.base_path,
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error starting environment: {e.stderr}")
            return False
        except Exception as e:
            print(f"Error starting environment: {e}")
            return False

    def stop_environment(self) -> bool:
        """Stop the Docker environment using docker-compose."""
        try:
            result = subprocess.run(
                ['docker-compose', 'down'],
                cwd=self.base_path,
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error stopping environment: {e.stderr}")
            return False
        except Exception as e:
            print(f"Error stopping environment: {e}")
            return False

    def cleanup(self) -> bool:
        """Clean up Docker resources created for the project."""
        try:
            for network in self.networks.values():
                subprocess.run(
                    ['docker', 'network', 'rm', network],
                    capture_output=True,
                    check=True
                )
            for volume in self.volumes.values():
                subprocess.run(
                    ['docker', 'volume', 'rm', volume],
                    capture_output=True,
                    check=True
                )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error during cleanup: {e.stderr}")
            return False
```

# chimera_stack/core/environment.py

```py
"""
Environment Management Module

Handles the creation and configuration of development environments.
"""

import os
import shutil
from typing import Dict, Optional
from pathlib import Path


class Environment:
    """Manages development environment setup and configuration."""

    def __init__(self, name: str, path: Optional[Path] = None):
        """
        Initialize environment manager.

        Args:
            name: Name of the project
            path: Optional path override. If not provided, uses current working directory
        """
        self.name = name
        self.path = path or self._get_safe_project_path()
        self.config: Dict = {}

    def _get_safe_project_path(self) -> Path:
        """
        Get a safe path for project creation that avoids the tool's directory.

        Returns:
            Path: Safe project path
        """
        cwd = Path.cwd()
        if self._is_tool_directory(cwd):
            return cwd.parent / self.name
        return cwd / self.name

    def _is_tool_directory(self, path: Path) -> bool:
        """
        Check if the given path is the tool's installation directory.

        Args:
            path: Path to check

        Returns:
            bool: True if path is tool directory
        """
        tool_indicators = [
            'pyproject.toml',
            'chimera_stack',
            'setup.py',
            'setup.cfg'
        ]
        return any((path / indicator).exists() for indicator in tool_indicators)

    def create_directory(self, path: Path) -> bool:
        """
        Safely create a directory only if needed.

        Args:
            path: Path to create

        Returns:
            bool: True if directory was created successfully
        """
        try:
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {path}: {e}")
            return False

    def setup(self) -> bool:
        """
        Initialize the development environment with minimal directory structure.

        Returns:
            bool: True if setup was successful
        """
        try:
            # Create only the essential base directory
            self.create_directory(self.path)

            # Create only the mandatory directories
            essential_dirs = [
                self.path / 'config',  # Required for environment configurations
                self.path / 'docker',  # Base directory for Docker configurations
                self.path / 'src',     # Source code directory
                self.path / 'public'   # Public web directory
            ]

            for directory in essential_dirs:
                self.create_directory(directory)

            # Create initial configuration files
            self._create_initial_files()

            # Remove any duplicate project directories
            self._cleanup_duplicate_directories()

            return True
        except Exception as e:
            print(f"Error setting up environment: {e}")
            return False

    def _create_initial_files(self) -> None:
        """Create initial configuration files for the project."""
        # Create empty docker-compose.yml
        docker_compose = self.path / 'docker-compose.yml'
        docker_compose.touch(exist_ok=True)

        # Create empty .env file
        env_file = self.path / '.env'
        env_file.touch(exist_ok=True)

        # Create .gitignore if it doesn't exist
        gitignore = self.path / '.gitignore'
        if not gitignore.exists():
            gitignore_content = """
# Environment files
.env
*.env

# Dependencies
/vendor/

# IDE files
.idea/
.vscode/
*.sublime-*

# OS files
.DS_Store
Thumbs.db
"""
            gitignore.write_text(gitignore_content.strip())

    def _cleanup_duplicate_directories(self) -> None:
        """Remove any duplicate project directories that might have been created."""
        duplicate_dir = self.path / self.name
        if duplicate_dir.exists():
            if duplicate_dir.is_dir():
                try:
                    # If there are important files in the duplicate directory, move them up
                    self._migrate_important_files(duplicate_dir)
                    shutil.rmtree(duplicate_dir)
                except Exception as e:
                    print(f"Warning: Error cleaning up duplicate directory: {e}")

    def _migrate_important_files(self, duplicate_dir: Path) -> None:
        """
        Migrate any important files from duplicate directory to main project directory.

        Args:
            duplicate_dir: Path to the duplicate directory
        """
        try:
            for item in duplicate_dir.iterdir():
                target_path = self.path / item.name
                if not target_path.exists():
                    if item.is_dir():
                        shutil.copytree(item, target_path)
                    else:
                        shutil.copy2(item, target_path)
        except Exception as e:
            print(f"Warning: Error while migrating files: {e}")

    def cleanup(self) -> bool:
        """
        Clean up the development environment.

        Returns:
            bool: True if cleanup was successful
        """
        try:
            if self.path.exists():
                shutil.rmtree(self.path)
            return True
        except Exception as e:
            print(f"Error cleaning up environment: {e}")
            return False
```

# chimera_stack/core/setup_wizard.py

```py
"""
Setup Wizard Module

Provides an interactive, user-friendly interface for configuring development environments.
Guides users through each choice with clear explanations and confirmations.
"""

import click
from typing import Dict, Any, Optional

class SetupWizard:
    """Interactive setup wizard for development environment configuration."""

    def __init__(self):
        self.config = {}
        self.options = {
            'language': {
                'php': 'PHP - A popular general-purpose scripting language',
                'python': 'Python - A versatile programming language'
            },
            'framework': {
                'php': {
                    'none': 'Vanilla PHP - No framework, just pure PHP',
                    'laravel': 'Laravel - The PHP Framework for Web Artisans',
                    'symfony': 'Symfony - Professional PHP Framework'
                },
                'python': {
                    'none': 'Vanilla Python - No framework, just pure Python',
                    'django': 'Django - The Web framework for perfectionists',
                    'flask': 'Flask - Lightweight WSGI web application framework'
                }
            },
            'webserver': {
                'nginx': 'Nginx - High-performance HTTP server',
                'apache': 'Apache - The most widely used web server'
            },
            'database': {
                'mysql': 'MySQL - The most popular open-source database',
                'postgresql': 'PostgreSQL - The world\'s most advanced open source database',
                'mariadb': 'MariaDB - Community-developed fork of MySQL'
            },
            'environment': {
                'development': 'Development - Optimized for local development',
                'testing': 'Testing - Configured for testing and staging',
                'production': 'Production - Optimized for production deployment'
            }
        }

    def run_setup(self) -> Optional[Dict[str, str]]:
        """Run the interactive setup process.

        Returns:
            Dict containing all configuration options or None if setup was cancelled
        """
        try:
            # Get project name
            project_name = self._get_project_name()
            if not self._confirm_step("project name", project_name):
                return None

            # Get environment type
            environment = self._get_environment()
            if not self._confirm_step("environment", self.options['environment'][environment]):
                return None

            # Get programming language
            language = self._get_language()
            if not self._confirm_step("programming language", self.options['language'][language]):
                return None

            # Get framework
            framework = self._get_framework(language)
            framework_desc = self.options['framework'][language][framework]
            if not self._confirm_step("framework", framework_desc):
                return None

            # Get web server
            webserver = self._get_webserver()
            if not self._confirm_step("web server", self.options['webserver'][webserver]):
                return None

            # Get database
            database = self._get_database()
            if not self._confirm_step("database", self.options['database'][database]):
                return None

            # Show final summary
            self._show_summary({
                'Project Name': project_name,
                'Environment': environment,
                'Language': language,
                'Framework': framework,
                'Web Server': webserver,
                'Database': database
            })

            if not click.confirm('\nWould you like to create this project?'):
                click.echo("\nSetup cancelled. No changes were made.")
                return None

            return {
                'project_name': project_name,
                'environment': environment,
                'language': language,
                'framework': framework,
                'webserver': webserver,
                'database': database
            }

        except click.Abort:
            click.echo("\nSetup cancelled. No changes were made.")
            return None

    def _get_project_name(self) -> str:
        """Get project name from user with validation."""
        while True:
            name = click.prompt("\nEnter your project name", type=str)
            if name.isalnum() or (name.replace('_', '').replace('-', '').isalnum()):
                return name
            click.echo("Project name must contain only letters, numbers, underscores, or hyphens.")

    def _get_environment(self) -> str:
        """Get environment type from user."""
        click.echo("\nAvailable environments:")
        for env, desc in self.options['environment'].items():
            click.echo(f"  {env}: {desc}")

        return click.prompt(
            "\nWhich environment would you like to use?",
            type=click.Choice(self.options['environment'].keys()),
            default='development'
        )

    def _get_language(self) -> str:
        """Get programming language choice from user."""
        click.echo("\nAvailable programming languages:")
        for lang, desc in self.options['language'].items():
            click.echo(f"  {lang}: {desc}")

        return click.prompt(
            "\nWhich programming language would you like to use?",
            type=click.Choice(self.options['language'].keys())
        )

    def _get_framework(self, language: str) -> str:
        """Get framework choice from user based on selected language."""
        click.echo(f"\nAvailable frameworks for {language}:")
        for fw, desc in self.options['framework'][language].items():
            click.echo(f"  {fw}: {desc}")

        return click.prompt(
            "\nWhich framework would you like to use?",
            type=click.Choice(self.options['framework'][language].keys()),
            default='none'
        )

    def _get_webserver(self) -> str:
        """Get web server choice from user."""
        click.echo("\nAvailable web servers:")
        for ws, desc in self.options['webserver'].items():
            click.echo(f"  {ws}: {desc}")

        return click.prompt(
            "\nWhich web server would you like to use?",
            type=click.Choice(self.options['webserver'].keys()),
            default='nginx'
        )

    def _get_database(self) -> str:
        """Get database choice from user."""
        click.echo("\nAvailable databases:")
        for db, desc in self.options['database'].items():
            click.echo(f"  {db}: {desc}")

        return click.prompt(
            "\nWhich database would you like to use?",
            type=click.Choice(self.options['database'].keys()),
            default='mysql'
        )

    def _confirm_step(self, step_name: str, value: str) -> bool:
        """Confirm user's choice for a setup step."""
        click.echo(f"\nYou selected: {value}")
        if not click.confirm(f"Would you like to proceed with this {step_name}?"):
            click.echo(f"\nLet's choose a different {step_name}.")
            return False
        return True

    def _show_summary(self, config: Dict[str, str]) -> None:
        """Show summary of all selected options."""
        click.echo("\nConfiguration Summary:")
        click.echo("=====================")
        for key, value in config.items():
            # Get description for the value if available
            if key.lower() in self.options:
                desc = self.options[key.lower()].get(value, value)
            elif key == 'Framework':
                desc = self.options['framework'][config['Language']][value]
            else:
                desc = value
            click.echo(f"{key}: {desc}")
        click.echo("=====================")
```

# chimera_stack/frameworks/**init**.py

```py
# src/frameworks/__init__.py
"""
Framework Implementations

Provides framework-specific implementations for PHP and Python projects.
"""

from .php import LaravelFramework, SymfonyFramework, VanillaPHPFramework
from .python import DjangoFramework, FlaskFramework, VanillaPythonFramework

__all__ = [
    'LaravelFramework',
    'SymfonyFramework',
    'VanillaPHPFramework',
    'DjangoFramework',
    'FlaskFramework',
    'VanillaPythonFramework'
]
```

# chimera_stack/frameworks/base.py

```py
"""
Base Framework Interface

Defines the contract that all framework implementations must follow,
ensuring consistent behavior across different programming languages and frameworks.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional, Any


class BaseFramework(ABC):
    """Abstract base class for framework implementations."""

    def __init__(self, project_name: str, base_path: Path):
        """
        Initialize the framework.

        Args:
            project_name: Name of the project
            base_path: Root path of the project
        """
        self.project_name = project_name
        self.base_path = base_path
        self.src_path = base_path / 'src'
        self.docker_path = base_path / 'docker'
        self.config_path = base_path / 'config'
        self.docker_requirements: Dict[str, Dict] = {}

    @abstractmethod
    def initialize_project(self) -> bool:
        """
        Initialize a new project with the framework.

        Returns:
            bool: True if initialization was successful
        """
        pass

    @abstractmethod
    def configure_docker(self) -> Dict[str, Any]:
        """
        Generate Docker configuration for the framework.

        Returns:
            Dict[str, Any]: Docker configuration dictionary
        """
        pass

    @abstractmethod
    def get_default_ports(self) -> Dict[str, int]:
        """
        Return default ports used by the framework.

        Returns:
            Dict[str, int]: Dictionary of service names to port numbers
        """
        pass

    @abstractmethod
    def setup_development_environment(self) -> bool:
        """
        Set up development environment for the framework.

        Returns:
            bool: True if setup was successful
        """
        pass

    def create_directory(self, path: Path) -> bool:
        """
        Safely create a directory only if it will be used.

        Args:
            path: Path to create

        Returns:
            bool: True if directory was created or already exists
        """
        try:
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {path}: {e}")
            return False

    def get_project_root(self) -> Path:
        """
        Get the project's root directory.

        Returns:
            Path: Project root directory
        """
        return self.base_path

    def get_source_path(self) -> Path:
        """
        Get the project's source directory.

        Returns:
            Path: Project source directory
        """
        return self.src_path
```

# chimera_stack/frameworks/php/**init**.py

```py
"""
PHP Framework Implementations

Provides framework-specific implementations for PHP projects including Laravel,
Symfony, and vanilla PHP configurations.
"""

from .laravel import LaravelFramework
from .symfony import SymfonyFramework
from .vanilla import VanillaPHPFramework

__all__ = [
    'LaravelFramework',
    'SymfonyFramework',
    'VanillaPHPFramework'
]
```

# chimera_stack/frameworks/php/base_php.py

```py
"""
PHP Framework Base Implementation

Provides common functionality for PHP-based frameworks.
"""

from pathlib import Path
from typing import Dict, Any
from chimera_stack.frameworks.base import BaseFramework

class BasePHPFramework(BaseFramework):
    """Base class for PHP frameworks."""

    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.docker_requirements = {
            'php': {
                'image': 'php:8.2-fpm',
                'extensions': ['pdo', 'pdo_mysql', 'mbstring']
            }
        }

    def get_default_ports(self) -> Dict[str, int]:
        return {
            'web': 8080,
            'php-fpm': 9000,
            'database': 3306
        }

    def configure_docker(self) -> Dict[str, Any]:
        """Generate base PHP Docker configuration."""
        return {
            'services': {
                'php': {
                    'image': self.docker_requirements['php']['image'],
                    'volumes': [
                        f'./{self.project_name}:/var/www/html'
                    ]
                }
            }
        }
```

# chimera_stack/frameworks/php/laravel.py

```py
"""
Laravel Framework Implementation

Handles Laravel-specific Docker environment setup while maintaining the standard
Laravel installation and project structure conventions.
"""

from pathlib import Path
from typing import Dict, Any
import subprocess
from chimera_stack.frameworks.php.base_php import BasePHPFramework

class LaravelFramework(BasePHPFramework):
    """Laravel framework implementation focusing on Docker environment setup."""

    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.docker_requirements.update({
            'php': {
                'image': 'php:8.2-fpm',
                'extensions': [
                    'pdo_mysql',
                    'mbstring',
                    'exif',
                    'pcntl',
                    'bcmath',
                    'gd'
                ]
            },
            'composer': {
                'image': 'composer:latest'
            }
        })

    def initialize_project(self) -> bool:
        """Initialize Laravel project using Docker."""
        try:
            self.ensure_directories()

            # Use Composer to create Laravel project in src directory
            subprocess.run([
                'docker', 'run', '--rm',
                '-v', f'{self.base_path}:/app',
                '-w', '/app/src',
                'composer:latest',
                'create-project',
                'laravel/laravel',
                '.'
            ], check=True)

            # Create necessary Docker configurations
            self._create_docker_configs()

            return True
        except subprocess.CalledProcessError as e:
            print(f"Error initializing Laravel project: {e}")
            return False

    def configure_docker(self) -> Dict[str, Any]:
        """Generate Laravel-specific Docker configuration."""
        config = {
            'services': {
                'php': {
                    'build': {
                        'context': '.',
                        'dockerfile': 'docker/php/Dockerfile'
                    },
                    'volumes': [
                        './src:/var/www/html:cached',
                        './docker/php/local.ini:/usr/local/etc/php/conf.d/local.ini:ro'
                    ],
                    'depends_on': ['mysql']
                },
                'nginx': {
                    'image': 'nginx:alpine',
                    'ports': [f"{self.get_default_ports()['web']}:80"],
                    'volumes': [
                        './src:/var/www/html:cached',
                        './docker/nginx/conf.d:/etc/nginx/conf.d:ro'
                    ],
                    'depends_on': ['php']
                },
                'mysql': {
                    'image': 'mysql:8.0',
                    'environment': {
                        'MYSQL_DATABASE': '${DB_DATABASE}',
                        'MYSQL_USER': '${DB_USERNAME}',
                        'MYSQL_PASSWORD': '${DB_PASSWORD}',
                        'MYSQL_ROOT_PASSWORD': '${DB_ROOT_PASSWORD}'
                    },
                    'ports': [f"{self.get_default_ports()['database']}:3306"],
                    'volumes': [
                        'mysql_data:/var/lib/mysql:cached'
                    ]
                },
                'redis': {
                    'image': 'redis:alpine',
                    'ports': [f"{self.get_default_ports()['redis']}:6379"]
                }
            },
            'volumes': {
                'mysql_data': None
            }
        }
        return config

    def get_default_ports(self) -> Dict[str, int]:
        """Return default ports for Laravel development."""
        return {
            'web': 8080,
            'database': 3306,
            'redis': 6379
        }

    def setup_development_environment(self) -> bool:
        """Set up Laravel development environment configurations."""
        try:
            self._create_env_file()
            return True
        except Exception as e:
            print(f"Error setting up Laravel environment: {e}")
            return False

    def _create_docker_configs(self) -> None:
        """Create necessary Docker configuration files."""
        # Create PHP configuration
        php_path = self.docker_path / 'php'
        php_path.mkdir(exist_ok=True, parents=True)

        self._create_php_dockerfile(php_path)
        self._create_php_config(php_path)

        # Create Nginx configuration
        nginx_path = self.docker_path / 'nginx'
        nginx_path.mkdir(exist_ok=True, parents=True)

        self._create_nginx_config(nginx_path)

    def _create_php_dockerfile(self, path: Path) -> None:
        """Generate PHP Dockerfile with Laravel requirements."""
        dockerfile_content = f"""
FROM {self.docker_requirements['php']['image']}

# Install dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    libpng-dev \\
    libonig-dev \\
    libxml2-dev \\
    zip \\
    unzip

# Install PHP extensions
RUN docker-php-ext-install \\
    {' '.join(self.docker_requirements['php']['extensions'])}

# Install Composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

WORKDIR /var/www/html
"""
        (path / 'Dockerfile').write_text(dockerfile_content.strip())

    def _create_php_config(self, path: Path) -> None:
        """Generate PHP configuration file."""
        php_ini_content = """
upload_max_filesize = 40M
post_max_size = 40M
memory_limit = 512M
max_execution_time = 600
default_socket_timeout = 3600
request_terminate_timeout = 600
"""
        (path / 'local.ini').write_text(php_ini_content.strip())

    def _create_nginx_config(self, path: Path) -> None:
        """Generate Nginx configuration for Laravel."""
        conf_d_path = path / 'conf.d'
        conf_d_path.mkdir(exist_ok=True, parents=True)

        nginx_config = r"""
server {
    listen 80;
    index index.php index.html;
    server_name localhost;
    root /var/www/html/public;
    client_max_body_size 40m;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        fastcgi_pass php:9000;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
        fastcgi_read_timeout 600;
    }

    location ~ /\.(?!well-known).* {
        deny all;
    }
}
"""
        (conf_d_path / 'default.conf').write_text(nginx_config.strip())

    def _create_env_file(self) -> None:
        """Create Laravel .env file with development settings."""
        env_content = """
APP_NAME=Laravel
APP_ENV=local
APP_KEY=
APP_DEBUG=true
APP_URL=http://localhost:8080

LOG_CHANNEL=stack
LOG_DEPRECATIONS_CHANNEL=null
LOG_LEVEL=debug

DB_CONNECTION=mysql
DB_HOST=mysql
DB_PORT=3306
DB_DATABASE=laravel
DB_USERNAME=laravel
DB_PASSWORD=secret

BROADCAST_DRIVER=log
CACHE_DRIVER=redis
FILESYSTEM_DISK=local
QUEUE_CONNECTION=redis
SESSION_DRIVER=redis
SESSION_LIFETIME=120

REDIS_HOST=redis
REDIS_PASSWORD=null
REDIS_PORT=6379
"""
        env_path = self.src_path / '.env'
        env_path.write_text(env_content.strip())
```

# chimera_stack/frameworks/php/symfony.py

```py
"""
Symfony Framework Implementation

Handles Docker environment setup for Symfony projects, focusing on container configuration
and environment preparation without interfering with Symfony's structure.
"""

from pathlib import Path
from typing import Dict, Any
from chimera_stack.frameworks.php.base_php import BasePHPFramework

class SymfonyFramework(BasePHPFramework):
    """Symfony framework implementation focusing on Docker environment setup."""

    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.docker_requirements.update({
            'php': {
                'image': 'php:8.3-fpm',
                'platform': 'linux/arm64',
                'extensions': [
                    'pdo',
                    'pdo_mysql',
                    'zip',
                    'intl',
                    'opcache'
                ]
            }
        })

    def initialize_project(self) -> bool:
        """Initialize Docker environment for Symfony."""
        try:
            # Create only Docker-related directories and files
            docker_path = self.base_path / 'docker'
            docker_path.mkdir(exist_ok=True, parents=True)

            # Create Docker configurations
            self._create_docker_configs()

            return True
        except Exception as e:
            print(f"Error initializing Docker environment: {e}")
            return False

    def configure_docker(self) -> Dict[str, Any]:
        """Generate Docker Compose configuration for Symfony."""
        return {
            'services': {
                'app': {
                    'build': {
                        'context': '.',
                        'dockerfile': 'Dockerfile'
                    },
                    'container_name': f"{self.project_name}_app",
                    'volumes': [
                        '.:/var/www'
                    ],
                    'depends_on': [
                        'db',
                        'redis'
                    ]
                },
                'nginx': {
                    'image': 'nginx:alpine',
                    'container_name': f"{self.project_name}_nginx",
                    'ports': [
                        f"{self.get_default_ports()['web']}:8000"
                    ],
                    'volumes': [
                        '.:/var/www',
                        './docker/nginx/default.conf:/etc/nginx/conf.d/default.conf'
                    ],
                    'depends_on': [
                        'app'
                    ]
                },
                'db': {
                    'image': 'mysql:8.0',
                    'container_name': f"{self.project_name}_db",
                    'platform': 'linux/arm64',
                    'environment': {
                        'MYSQL_ROOT_PASSWORD': '${MYSQL_ROOT_PASSWORD}',
                        'MYSQL_DATABASE': '${MYSQL_DATABASE}',
                        'MYSQL_USER': '${MYSQL_USER}',
                        'MYSQL_PASSWORD': '${MYSQL_PASSWORD}'
                    },
                    'ports': [
                        f"{self.get_default_ports()['database']}:3306"
                    ],
                    'volumes': [
                        'db_data:/var/lib/mysql'
                    ]
                },
                'redis': {
                    'image': 'redis:alpine',
                    'container_name': f"{self.project_name}_redis",
                    'platform': 'linux/arm64',
                    'ports': [
                        f"{self.get_default_ports()['redis']}:6379"
                    ]
                }
            },
            'volumes': {
                'db_data': None
            }
        }

    def get_default_ports(self) -> Dict[str, int]:
        """Return default ports for Symfony development."""
        return {
            'web': 8000,
            'database': 3306,
            'redis': 6379
        }

    def setup_development_environment(self) -> bool:
        """Set up development environment configurations."""
        try:
            self._create_env_file()
            return True
        except Exception as e:
            print(f"Error setting up environment: {e}")
            return False

    def _create_docker_configs(self) -> None:
        """Create necessary Docker configuration files."""
        # Create Dockerfile
        dockerfile_content = """
FROM --platform=linux/arm64 php:8.3-fpm

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    unzip \\
    libzip-dev \\
    libpq-dev \\
    libonig-dev \\
    && docker-php-ext-install pdo pdo_mysql zip

# Install Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Set working directory
WORKDIR /var/www

# Copy the application
COPY . .

# Install dependencies
RUN composer install

# Set permissions
RUN chown -R www-data:www-data var
"""
        (self.base_path / 'Dockerfile').write_text(dockerfile_content.strip())

        # Create Nginx configuration
        nginx_path = self.base_path / 'docker' / 'nginx'
        nginx_path.mkdir(exist_ok=True, parents=True)

        nginx_config = """
server {
    listen 8000;
    server_name localhost;
    root /var/www/public;

    location / {
        try_files $uri /index.php$is_args$args;
    }

    location ~ ^/index\\.php(/|$) {
        fastcgi_pass app:9000;
        fastcgi_split_path_info ^(.+\\.php)(/.*)$;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param DOCUMENT_ROOT $document_root;
        internal;
    }

    location ~ \\.php$ {
        return 404;
    }

    error_log /var/log/nginx/project_error.log;
    access_log /var/log/nginx/project_access.log;
}
"""
        (nginx_path / 'default.conf').write_text(nginx_config.strip())

    def _create_env_file(self) -> None:
        """Create sample .env file with development settings."""
        env_content = f"""
###> symfony/framework-bundle ###
APP_ENV=dev
APP_SECRET=changeThisToASecureSecret
###< symfony/framework-bundle ###

###> doctrine/doctrine-bundle ###
DATABASE_URL="mysql://${{MYSQL_USER}}:${{MYSQL_PASSWORD}}@db:3306/${{MYSQL_DATABASE}}"
###< doctrine/doctrine-bundle ###

REDIS_URL=redis://redis:6379
"""
        (self.base_path / '.env').write_text(env_content.strip())

        env_dist_content = """
MYSQL_ROOT_PASSWORD=root_password
MYSQL_DATABASE=mydb
MYSQL_USER=db_user
MYSQL_PASSWORD=db_password
"""
        (self.base_path / '.env.dist').write_text(env_dist_content.strip())
```

# chimera_stack/frameworks/php/vanilla.py

```py
"""
Vanilla PHP Implementation

Provides a clean, framework-free PHP development environment using Docker.
"""

from pathlib import Path
from typing import Dict, Any
from chimera_stack.frameworks.php.base_php import BasePHPFramework

class VanillaPHPFramework(BasePHPFramework):
    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.docker_requirements.update({
            'php': {
                'image': 'php:8.2-fpm',
                'system_packages': [
                    'git',
                    'zip',
                    'unzip',
                    'libpng-dev',
                    'libonig-dev',
                    'libzip-dev'
                ],
                'extensions': {
                    'pdo': None,
                    'pdo_mysql': None,
                    'mbstring': None,
                    'zip': None,
                    'exif': None,
                    'gd': {'configure': True}
                }
            }
        })

    def initialize_project(self) -> bool:
        """Initialize a minimal PHP project structure."""
        try:
            # Create only directories we will actually use
            public_path = self.base_path / 'public'
            src_path = self.base_path / 'src'
            pages_path = src_path / 'pages'

            # Create directories only when we're about to use them
            self.create_directory(public_path)  # For index.php
            self.create_directory(pages_path)   # For home.php

            # Docker service directories will be created by their respective services

            # Create project files
            self._create_index_file(public_path)
            self._create_bootstrap_file(src_path)
            self._create_home_file(pages_path)
            self._create_env_file(self.base_path)
            self._create_gitignore(self.base_path)

            return True
        except Exception as e:
            print(f"Error initializing vanilla PHP project: {e}")
            return False

    def create_directory(self, path: Path) -> None:
        """Create a directory if it doesn't exist."""
        path.mkdir(exist_ok=True, parents=True)

    def _create_index_file(self, path: Path) -> None:
        """Create the main index.php file."""
        content = '''<?php
declare(strict_types=1);

require_once __DIR__ . '/../src/bootstrap.php';

// Basic routing
$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

// Add your routes here
switch ($uri) {
    case '/':
        require __DIR__ . '/../src/pages/home.php';
        break;
    case '/info':
        phpinfo();
        break;
    default:
        http_response_code(404);
        echo "404 Not Found";
        break;
}'''
        (path / 'index.php').write_text(content)

    def _create_bootstrap_file(self, path: Path) -> None:
        """Create the bootstrap.php file."""
        content = '''<?php
declare(strict_types=1);

// Error reporting for development
error_reporting(E_ALL);
ini_set('display_errors', '1');

// Load environment variables
if (file_exists(__DIR__ . '/../.env')) {
    $env = parse_ini_file(__DIR__ . '/../.env');
    foreach ($env as $key => $value) {
        $_ENV[$key] = $value;
        putenv("$key=$value");
    }
}

// Autoloader setup for future use
spl_autoload_register(function ($class) {
    $file = __DIR__ . '/' . str_replace('\\', '/', $class) . '.php';
    if (file_exists($file)) {
        require $file;
        return true;
    }
    return false;
});'''
        (path / 'bootstrap.php').write_text(content)

    def _create_home_file(self, path: Path) -> None:
        """Create the home.php file."""
        content = '''<?php
declare(strict_types=1);

$title = 'Welcome to ChimeraStack';
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($title) ?></title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            line-height: 1.6;
        }
        .status {
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 4px;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <h1><?= htmlspecialchars($title) ?></h1>
    <p>Your development environment is ready.</p>
    <p><a href="/info">View PHP Info</a></p>

    <!-- Database Connection Test -->
    <?php
    try {
        $dsn = "mysql:host={$_ENV['DB_HOST']};dbname={$_ENV['DB_DATABASE']}";
        $pdo = new PDO($dsn, $_ENV['DB_USERNAME'], $_ENV['DB_PASSWORD']);
        echo '<div class="status success">✓ Database connection successful!</div>';
    } catch (PDOException $e) {
        echo '<div class="status error">✗ Database connection failed: ' . htmlspecialchars($e->getMessage()) . '</div>';
    }
    ?>
</body>
</html>'''
        (path / 'home.php').write_text(content)

    def _create_env_file(self, path: Path) -> None:
        """Create the .env file with default values."""
        content = f'''# PHP Configuration
PHP_DISPLAY_ERRORS=1
PHP_ERROR_REPORTING=E_ALL
PHP_MEMORY_LIMIT=256M
PHP_MAX_EXECUTION_TIME=30
PHP_POST_MAX_SIZE=100M
PHP_UPLOAD_MAX_FILESIZE=100M

# Database Configuration
DB_CONNECTION=mysql
DB_HOST=mysql
DB_PORT=3306
DB_DATABASE={self.project_name}
DB_USERNAME={self.project_name}
DB_PASSWORD=secret
DB_ROOT_PASSWORD=rootsecret'''
        (path / '.env').write_text(content)

    def _create_gitignore(self, path: Path) -> None:
        """Create .gitignore file."""
        content = '''# Environment files
.env
*.env

# Dependencies
/vendor/

# IDE files
.idea/
.vscode/
*.sublime-*

# OS files
.DS_Store
Thumbs.db'''
        (path / '.gitignore').write_text(content)

    def setup_development_environment(self) -> bool:
        """Set up development environment configurations."""
        try:
            # Generate Docker configurations
            docker_path = self.base_path / 'docker'
            php_path = docker_path / 'php'
            self.create_directory(php_path)

            # Create necessary Docker configurations
            self._create_php_dockerfile(php_path)
            self._create_php_config(php_path)
            self._create_php_fpm_config(php_path)

            return True
        except Exception as e:
            print(f"Error setting up development environment: {e}")
            return False

    def _create_php_fpm_config(self, path: Path) -> None:
        """Create PHP-FPM pool configuration."""
        www_conf = """[global]
error_log = /var/log/php-fpm/error.log
log_level = notice

[www]
user = www-data
group = www-data

listen = 9000
listen.owner = www-data
listen.group = www-data
listen.mode = 0660

pm = dynamic
pm.max_children = 10
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
pm.max_requests = 500

php_admin_value[error_log] = /var/log/php-fpm/www-error.log
php_admin_flag[log_errors] = on

catch_workers_output = yes
decorate_workers_output = yes

env[DB_HOST] = $DB_HOST
env[DB_DATABASE] = $DB_DATABASE
env[DB_USERNAME] = $DB_USERNAME
env[DB_PASSWORD] = $DB_PASSWORD

security.limit_extensions = .php"""
        (path / 'www.conf').write_text(www_conf)

    def _create_php_dockerfile(self, path: Path) -> None:
        """Generate PHP Dockerfile."""
        path.mkdir(exist_ok=True, parents=True)
        content = f'''FROM {self.docker_requirements['php']['image']}

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    {" ".join(self.docker_requirements['php']['system_packages'])} \\
    && rm -rf /var/lib/apt/lists/*

# Install PHP extensions
RUN docker-php-ext-install pdo pdo_mysql mbstring zip exif \\
    && docker-php-ext-configure gd \\
    && docker-php-ext-install gd

# Configure PHP
COPY docker/php/php.ini /usr/local/etc/php/conf.d/custom.ini
COPY docker/php/www.conf /usr/local/etc/php-fpm.d/www.conf

# Create log directory
RUN mkdir -p /var/log/php-fpm \\
    && chown -R www-data:www-data /var/log/php-fpm

# Set proper permissions
RUN usermod -u 1000 www-data \\
    && groupmod -g 1000 www-data

WORKDIR /var/www/html

USER www-data'''
        (path / 'Dockerfile').write_text(content)

    def _create_php_config(self, path: Path) -> None:
        """Generate PHP configuration."""
        path.mkdir(exist_ok=True, parents=True)
        content = '''[PHP]
; Error handling and logging
display_errors = ${PHP_DISPLAY_ERRORS}
display_startup_errors = ${PHP_DISPLAY_ERRORS}
error_reporting = ${PHP_ERROR_REPORTING}
log_errors = On
error_log = /var/log/php-fpm/php_errors.log
log_errors_max_len = 1024
ignore_repeated_errors = Off
ignore_repeated_source = Off
report_memleaks = On
track_errors = On

; Resource limits
memory_limit = ${PHP_MEMORY_LIMIT}
max_execution_time = ${PHP_MAX_EXECUTION_TIME}
post_max_size = ${PHP_POST_MAX_SIZE}
upload_max_filesize = ${PHP_UPLOAD_MAX_FILESIZE}
max_file_uploads = 20

[Date]
date.timezone = UTC

[Session]
session.save_handler = files
session.save_path = /tmp
session.gc_maxlifetime = 1800
session.gc_probability = 1
session.gc_divisor = 100

[opcache]
opcache.enable = 1
opcache.memory_consumption = 128
opcache.interned_strings_buffer = 8
opcache.max_accelerated_files = 4000
opcache.validate_timestamps = 1
opcache.revalidate_freq = 0
opcache.fast_shutdown = 1

[mysqlnd]
mysqlnd.collect_statistics = On
mysqlnd.collect_memory_statistics = On'''
        (path / 'php.ini').write_text(content)

    def _create_nginx_config(self, path: Path) -> None:
        """Create Nginx configuration."""
        conf_d_path = path / 'conf.d'
        conf_d_path.mkdir(exist_ok=True, parents=True)

        content = r'''server {
    listen 80;
    server_name localhost;
    root /var/www/html/public;
    index index.php index.html;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Content-Type-Options "nosniff";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Health check endpoint
    location /ping {
        access_log off;
        return 200 'healthy\n';
    }

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        fastcgi_pass php:9000;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;

        fastcgi_intercept_errors on;
        fastcgi_buffer_size 16k;
        fastcgi_buffers 4 16k;
        fastcgi_connect_timeout 300;
        fastcgi_send_timeout 300;
        fastcgi_read_timeout 300;
    }

    location ~ /\.(?!well-known) {
        deny all;
        access_log off;
        log_not_found off;
    }

    # Optimization for static files
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 30d;
        access_log off;
        add_header Cache-Control "public";
    }
}'''
        (conf_d_path / 'default.conf').write_text(content)

    def get_default_ports(self) -> Dict[str, int]:
        """Return default ports for vanilla PHP development."""
        return {
            'web': 8080,
            'database': 3306
        }

    def get_service_volumes(self) -> Dict[str, Any]:
        """Get standardized volume configuration for all services."""
        return {
            'mysql_data': {
                'driver': 'local',
                'name': f"{self.project_name}_mysql_data"
            },
            'php_logs': {
                'driver': 'local',
                'name': f"{self.project_name}_php_logs"
            }
        }

    def get_service_networks(self) -> Dict[str, Any]:
        """Get standardized network configuration."""
        return {
            'app_network': {
                'driver': 'bridge',
                'name': f"{self.project_name}_network"
            }
        }

    def get_php_service_config(self) -> Dict[str, Any]:
        """Get standardized PHP service configuration."""
        return {
            'build': {
                'context': '.',
                'dockerfile': 'docker/php/Dockerfile'
            },
            'volumes': [
                '.:/var/www/html:cached',
                'php_logs:/var/log/php-fpm'
            ],
            'environment': {
                'PHP_DISPLAY_ERRORS': '${PHP_DISPLAY_ERRORS}',
                'PHP_ERROR_REPORTING': '${PHP_ERROR_REPORTING}',
                'PHP_MEMORY_LIMIT': '${PHP_MEMORY_LIMIT}',
                'PHP_MAX_EXECUTION_TIME': '${PHP_MAX_EXECUTION_TIME}',
                'PHP_POST_MAX_SIZE': '${PHP_POST_MAX_SIZE}',
                'PHP_UPLOAD_MAX_FILESIZE': '${PHP_UPLOAD_MAX_FILESIZE}'
            },
            'networks': ['app_network'],
            'healthcheck': {
                'test': ["CMD", "php-fpm", "-t"],
                'interval': '10s',
                'timeout': '5s',
                'retries': 3
            }
        }

    def get_nginx_service_config(self) -> Dict[str, Any]:
        """Get standardized Nginx service configuration."""
        return {
            'image': 'nginx:alpine',
            'ports': [f"{self.get_default_ports()['web']}:80"],
            'volumes': [
                '.:/var/www/html:cached',
                './docker/nginx/conf.d:/etc/nginx/conf.d:ro'
            ],
            'depends_on': ['php'],
            'networks': ['app_network'],
            'healthcheck': {
                'test': ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/ping"],
                'interval': '10s',
                'timeout': '5s',
                'retries': 3
            }
        }

    def get_mysql_service_config(self) -> Dict[str, Any]:
        """Get standardized MySQL service configuration."""
        return {
            'image': 'mysql:8.0',
            'environment': {
                'MYSQL_DATABASE': '${DB_DATABASE}',
                'MYSQL_USER': '${DB_USERNAME}',
                'MYSQL_PASSWORD': '${DB_PASSWORD}',
                'MYSQL_ROOT_PASSWORD': '${DB_ROOT_PASSWORD}'
            },
            'ports': [f"{self.get_default_ports()['database']}:3306"],
            'volumes': ['mysql_data:/var/lib/mysql'],
            'networks': ['app_network'],
            'healthcheck': {
                'test': ["CMD", "mysqladmin", "ping", "-h", "localhost"],
                'interval': '10s',
                'timeout': '5s',
                'retries': 3
            }
        }

    def configure_docker(self) -> Dict[str, Any]:
        """Generate Docker configuration for vanilla PHP development."""
        config = {
            'services': {
                'php': self.get_php_service_config(),
                'nginx': self.get_nginx_service_config(),
                'mysql': self.get_mysql_service_config()
            },
            'networks': self.get_service_networks(),
            'volumes': self.get_service_volumes()
        }
        return config

    def _create_bootstrap_file(self, path: Path) -> None:
        """Create the bootstrap.php file."""
        content = '''<?php
declare(strict_types=1);

// Error reporting for development
error_reporting(E_ALL);
ini_set('display_errors', '1');

// Load environment variables
if (file_exists(__DIR__ . '/../.env')) {
    $env = parse_ini_file(__DIR__ . '/../.env');
    foreach ($env as $key => $value) {
        $_ENV[$key] = $value;
        putenv("$key=$value");
    }
}

// PSR-4 style autoloader
spl_autoload_register(function ($class) {
    // Convert namespace separators to directory separators
    $file = __DIR__ . DIRECTORY_SEPARATOR .
            str_replace(['\\\\', '/'], DIRECTORY_SEPARATOR, $class) . '.php';

    if (file_exists($file)) {
        require_once $file;
        return true;
    }
    return false;
});

// Register Composer autoloader if available
$composerAutoloader = __DIR__ . '/../vendor/autoload.php';
if (file_exists($composerAutoloader)) {
    require_once $composerAutoloader;
}'''
        (path / 'bootstrap.php').write_text(content)
```

# chimera_stack/frameworks/python/**init**.py

```py
"""
Python Framework Implementations

Provides framework-specific implementations for Python projects including Django,
Flask, and vanilla Python configurations.
"""

from .django import DjangoFramework
from .flask import FlaskFramework
from .vanilla import VanillaPythonFramework

__all__ = [
    'DjangoFramework',
    'FlaskFramework',
    'VanillaPythonFramework'
]
```

# chimera_stack/frameworks/python/base_python.py

```py
"""
Python Framework Base Implementation

Provides common functionality for Python-based frameworks including virtual
environment management and package handling.
"""

from pathlib import Path
import subprocess
import venv
from typing import Dict, Any
from chimera_stack.frameworks.base import BaseFramework

class BasePythonFramework(BaseFramework):
    """Base class for Python frameworks providing shared functionality."""

    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.docker_requirements = {
            'python': {
                'image': 'python:3.11-slim',
                'environment': {
                    'PYTHONUNBUFFERED': '1',
                    'PYTHONDONTWRITEBYTECODE': '1'
                }
            }
        }
        self.venv_path = self.base_path / self.project_name / 'venv'

    def get_default_ports(self) -> Dict[str, int]:
        return {
            'web': 8000,
            'database': 5432,
            'cache': 6379
        }

    def _setup_virtual_environment(self) -> bool:
        """Create and configure a Python virtual environment."""
        try:
            venv.create(self.venv_path, with_pip=True)
            return True
        except Exception as e:
            print(f"Error creating virtual environment: {e}")
            return False

    def configure_docker(self) -> Dict[str, Any]:
        """Generate base Python Docker configuration."""
        return {
            'services': {
                'app': {
                    'build': {
                        'context': '.',
                        'dockerfile': 'Dockerfile'
                    },
                    'volumes': [
                        f'./{self.project_name}:/app'
                    ],
                    'environment': self.docker_requirements['python']['environment']
                }
            }
        }

    def _generate_dockerfile(self) -> bool:
        """Generate a Dockerfile for the Python application."""
        try:
            dockerfile_content = f"""
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \\
    PYTHONDONTWRITEBYTECODE=1 \\
    PIP_NO_CACHE_DIR=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
"""
            dockerfile_path = self.base_path / self.project_name / 'Dockerfile'
            dockerfile_path.write_text(dockerfile_content.strip())
            return True
        except Exception as e:
            print(f"Error generating Dockerfile: {e}")
            return False
```

# chimera_stack/frameworks/python/django.py

```py
"""
Django Framework Implementation

Provides Docker environment configuration for Django projects while preserving
Django's standard project structure and conventions. This implementation focuses
on creating a production-ready Docker environment that aligns with Django's
recommended deployment practices.
"""

from pathlib import Path
from typing import Dict, Any
import subprocess
from chimera_stack.frameworks.python.base_python import BasePythonFramework

class DjangoFramework(BasePythonFramework):
    """Django framework implementation focusing on Docker environment setup."""

    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.docker_requirements.update({
            'python': {
                'image': 'python:3.11-slim',
                'environment': {
                    'DJANGO_SETTINGS_MODULE': 'config.settings',
                    'PYTHONUNBUFFERED': '1',
                    'DATABASE_URL': 'postgresql://postgres:postgres@db:5432/postgres'
                }
            }
        })

    def initialize_project(self) -> bool:
        """Initialize a Django project using Docker."""
        try:
            project_path = self.base_path / self.project_name

            # Create project using Django's startproject through Docker
            subprocess.run([
                'docker', 'run', '--rm',
                '-v', f'{self.base_path}:/app',
                '-w', '/app',
                self.docker_requirements['python']['image'],
                'bash', '-c',
                f'pip install django && django-admin startproject config {self.project_name}'
            ], check=True)

            # Create requirements.txt
            requirements = [
                'django>=4.2.0',
                'psycopg2-binary>=2.9.0',
                'gunicorn>=20.1.0',
                'python-dotenv>=1.0.0'
            ]
            (project_path / 'requirements.txt').write_text('\n'.join(requirements))

            return True
        except subprocess.CalledProcessError as e:
            print(f"Error initializing Django project: {e}")
            return False

    def configure_docker(self) -> Dict[str, Any]:
        """Generate Django-specific Docker configuration."""
        config = {
            'services': {
                'web': {
                    'build': {
                        'context': '.',
                        'dockerfile': 'docker/python/Dockerfile'
                    },
                    'command': 'gunicorn config.wsgi:application --bind 0.0.0.0:8000',
                    'volumes': [
                        '.:/app:cached',
                        'static_volume:/app/staticfiles',
                        'media_volume:/app/media'
                    ],
                    'ports': [f"{self.get_default_ports()['web']}:8000"],
                    'environment': self.docker_requirements['python']['environment'],
                    'depends_on': ['db']
                },
                'db': {
                    'image': 'postgres:13',
                    'volumes': ['postgres_data:/var/lib/postgresql/data/'],
                    'environment': {
                        'POSTGRES_DB': '${POSTGRES_DB}',
                        'POSTGRES_USER': '${POSTGRES_USER}',
                        'POSTGRES_PASSWORD': '${POSTGRES_PASSWORD}'
                    },
                    'ports': [f"{self.get_default_ports()['database']}:5432"]
                }
            },
            'volumes': {
                'postgres_data': None,
                'static_volume': None,
                'media_volume': None
            }
        }
        return config

    def get_default_ports(self) -> Dict[str, int]:
        """Return default ports for Django development."""
        return {
            'web': 8000,
            'database': 5432
        }

    def setup_development_environment(self) -> bool:
        """Set up Django development environment configurations."""
        try:
            self._create_docker_configs()
            self._create_env_file()
            return True
        except Exception as e:
            print(f"Error setting up Django environment: {e}")
            return False

    def _create_docker_configs(self) -> None:
        """Create necessary Docker configuration files."""
        docker_path = self.base_path / self.project_name / 'docker'
        docker_path.mkdir(exist_ok=True)

        self._create_python_dockerfile(docker_path / 'python')

    def _create_python_dockerfile(self, path: Path) -> None:
        """Generate Python Dockerfile for Django."""
        path.mkdir(exist_ok=True)
        dockerfile_content = f"""
FROM {self.docker_requirements['python']['image']}

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create directory for static files
RUN mkdir -p /app/staticfiles /app/media

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "config.wsgi:application"]
"""
        (path / 'Dockerfile').write_text(dockerfile_content.strip())

    def _create_env_file(self) -> None:
        """Create .env file with development settings."""
        env_content = '''
DEBUG=1
SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=config.settings
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgresql://postgres:postgres@db:5432/postgres
'''
        env_path = self.base_path / self.project_name / '.env'
        env_path.write_text(env_content.strip())
```

# chimera_stack/frameworks/python/flask.py

```py
"""
Flask Framework Implementation

Handles Flask-specific Docker environment setup while maintaining simplicity
and flexibility. This implementation focuses on creating a production-ready
Docker environment without imposing specific project structure decisions.
"""

from pathlib import Path
from typing import Dict, Any
import subprocess
from chimera_stack.frameworks.python.base_python import BasePythonFramework

class FlaskFramework(BasePythonFramework):
    """Flask framework implementation focusing on Docker environment setup."""

    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.docker_requirements.update({
            'python': {
                'image': 'python:3.11-slim',
                'environment': {
                    'FLASK_APP': 'app',
                    'FLASK_ENV': 'development',
                    'PYTHONUNBUFFERED': '1',
                }
            }
        })

    def initialize_project(self) -> bool:
        """Initialize a minimal Flask project using pip."""
        try:
            project_path = self.base_path / self.project_name
            project_path.mkdir(exist_ok=True)

            # Create requirements.txt
            requirements = [
                'flask>=2.0.0',
                'python-dotenv>=1.0.0',
                'gunicorn>=20.1.0'
            ]
            (project_path / 'requirements.txt').write_text('\n'.join(requirements))

            # Create minimal app.py
            app_content = '''
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Flask Docker Development Environment'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
'''
            (project_path / 'app.py').write_text(app_content.strip())

            return True
        except Exception as e:
            print(f"Error initializing Flask project: {e}")
            return False

    def configure_docker(self) -> Dict[str, Any]:
        """Generate Flask-specific Docker configuration."""
        config = {
            'services': {
                'web': {
                    'build': {
                        'context': '.',
                        'dockerfile': 'docker/python/Dockerfile'
                    },
                    'ports': [f"{self.get_default_ports()['web']}:5000"],
                    'volumes': [
                        '.:/app:cached'
                    ],
                    'environment': self.docker_requirements['python']['environment'],
                    'depends_on': ['redis'] if self._uses_redis() else []
                }
            }
        }

        # Add Redis if specified
        if self._uses_redis():
            config['services']['redis'] = {
                'image': 'redis:alpine',
                'ports': [f"{self.get_default_ports()['cache']}:6379"]
            }

        return config

    def get_default_ports(self) -> Dict[str, int]:
        """Return default ports for Flask development."""
        return {
            'web': 5000,
            'cache': 6379
        }

    def setup_development_environment(self) -> bool:
        """Set up Flask development environment configurations."""
        try:
            self._create_docker_configs()
            self._create_env_file()
            return True
        except Exception as e:
            print(f"Error setting up Flask environment: {e}")
            return False

    def _create_docker_configs(self) -> None:
        """Create necessary Docker configuration files."""
        docker_path = self.base_path / self.project_name / 'docker'
        docker_path.mkdir(exist_ok=True)

        self._create_python_dockerfile(docker_path / 'python')

    def _create_python_dockerfile(self, path: Path) -> None:
        """Generate Python Dockerfile for Flask."""
        path.mkdir(exist_ok=True)
        dockerfile_content = f"""
FROM {self.docker_requirements['python']['image']}

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
"""
        (path / 'Dockerfile').write_text(dockerfile_content.strip())

    def _create_env_file(self) -> None:
        """Create .env file with development settings."""
        env_content = '''
FLASK_APP=app
FLASK_ENV=development
FLASK_DEBUG=1
'''
        env_path = self.base_path / self.project_name / '.env'
        env_path.write_text(env_content.strip())

    def _uses_redis(self) -> bool:
        """Check if the project uses Redis."""
        requirements_path = self.base_path / self.project_name / 'requirements.txt'
        return requirements_path.exists() and 'redis' in requirements_path.read_text()
```

# chimera_stack/frameworks/python/vanilla.py

```py
# src/frameworks/python/vanilla.py

"""
Vanilla Python Implementation

Provides a Docker-based development environment for pure Python applications
without framework constraints. This implementation focuses on creating a reliable,
production-ready setup for custom Python development projects.
"""

from pathlib import Path
from typing import Dict, Any
from chimera_stack.frameworks.python.base_python import BasePythonFramework

class VanillaPythonFramework(BasePythonFramework):
    def initialize_project(self) -> bool:
        try:
            project_path = self.base_path / self.project_name

            # Create project structure
            src_path = project_path / 'src'
            tests_path = project_path / 'tests'
            for path in [src_path, tests_path]:
                path.mkdir(exist_ok=True, parents=True)

            # Create main application module
            app_content = '''"""
Application entry point.

This module provides a basic WSGI application structure that can be extended
as needed. It includes basic routing and request handling capabilities.
"""
import os
import json
from typing import Callable, Dict, Tuple, Any
from wsgiref.simple_server import make_server

class Application:
    def __init__(self):
        self.routes: Dict[str, Callable] = {}
        self._register_routes()

    def _register_routes(self) -> None:
        """Register application routes."""
        self.routes = {
            '/': self.home,
            '/health': self.health_check
        }

    def home(self, environ: Dict) -> Tuple[str, Dict[str, str], str]:
        """Handle home route."""
        return '200 OK', {'Content-Type': 'application/json'}, json.dumps({
            'message': 'Python Development Environment Ready',
            'status': 'active'
        })

    def health_check(self, environ: Dict) -> Tuple[str, Dict[str, str], str]:
        """Handle health check route."""
        return '200 OK', {'Content-Type': 'application/json'}, json.dumps({
            'status': 'healthy',
            'version': os.getenv('APP_VERSION', '1.0.0')
        })

    def __call__(self, environ: Dict, start_response: Callable) -> Any:
        """WSGI application callable."""
        path = environ.get('PATH_INFO', '/')
        handler = self.routes.get(path)

        if handler is None:
            status = '404 Not Found'
            headers = {'Content-Type': 'application/json'}
            response_body = json.dumps({'error': 'Not Found'})
        else:
            try:
                status, headers, response_body = handler(environ)
            except Exception as e:
                status = '500 Internal Server Error'
                headers = {'Content-Type': 'application/json'}
                response_body = json.dumps({'error': str(e)})

        start_response(status, list(headers.items()))
        return [response_body.encode('utf-8')]

def create_app() -> Application:
    """Create and configure the application."""
    return Application()

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 8000))

    with make_server('', port, app) as httpd:
        print(f'Serving on port {port}...')
        httpd.serve_forever()
'''
            (src_path / 'app.py').write_text(app_content)

            # Create requirements.txt with development tools
            requirements = [
                'gunicorn>=20.1.0',
                'python-dotenv>=1.0.0',
                'pytest>=7.0.0',
                'pytest-cov>=4.0.0',
                'black>=22.0.0',
                'isort>=5.0.0',
                'pylint>=2.0.0'
            ]
            (project_path / 'requirements.txt').write_text('\n'.join(requirements))

            # Create basic test
            test_content = '''"""Basic application tests."""
import json
from src.app import create_app

def test_home_route():
    """Test the home route response."""
    app = create_app()
    environ = {'PATH_INFO': '/'}

    def start_response(status, headers):
        assert status == '200 OK'
        assert ('Content-Type', 'application/json') in headers

    response = app(environ, start_response)
    response_data = json.loads(response[0].decode('utf-8'))

    assert 'message' in response_data
    assert 'status' in response_data
    assert response_data['status'] == 'active'

def test_health_check():
    """Test the health check route."""
    app = create_app()
    environ = {'PATH_INFO': '/health'}

    def start_response(status, headers):
        assert status == '200 OK'

    response = app(environ, start_response)
    response_data = json.loads(response[0].decode('utf-8'))

    assert response_data['status'] == 'healthy'
'''
            (tests_path / 'test_app.py').write_text(test_content)

            return True

        except Exception as e:
            print(f"Error initializing vanilla Python project: {e}")
            return False

    def _create_python_dockerfile(self, path: Path) -> None:
        """Generate enhanced Python Dockerfile."""
        path.mkdir(exist_ok=True)
        dockerfile_content = f"""
FROM {self.docker_requirements['python']['image']}

# Set working directory
WORKDIR /app

# Install system dependencies and development tools
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set Python path and environment
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--reload", "src.app:create_app()"]
"""
        (path / 'Dockerfile').write_text(dockerfile_content.strip())
```

# chimera_stack/services/**init**.py

```py
# src/services/__init__.py
"""
Service Implementations

Provides configurations for various services like databases and web servers.
"""

from .databases import MySQLService, PostgreSQLService, MariaDBService
from .webservers import NginxService, ApacheService

__all__ = [
    'MySQLService',
    'PostgreSQLService',
    'MariaDBService',
    'NginxService',
    'ApacheService'
]
```

# chimera_stack/services/databases/**init**.py

```py
# src/services/databases/__init__.py
"""
Database Service Implementations

Provides specialized configurations for different database systems.
"""

from .mysql import MySQLService
from .postgresql import PostgreSQLService
from .mariadb import MariaDBService

__all__ = ['MySQLService', 'PostgreSQLService', 'MariaDBService']
```

# chimera_stack/services/databases/base.py

```py
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
```

# chimera_stack/services/databases/mariadb.py

```py
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
```

# chimera_stack/services/databases/mysql.py

```py
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
        volume_name = self.get_volume_name('mysql')
        port = self._get_available_port(3306, 3400)  # Try ports between 3306 and 3400

        config = {
            'services': {
                'mysql': {
                    **self.config,
                    'ports': [f"{port}:3306"],
                    'environment': self.get_environment_variables(),
                    'volumes': [
                        f"{volume_name}:/var/lib/mysql",
                        "./docker/mysql/my.cnf:/etc/mysql/conf.d/my.cnf:ro"
                    ],
                    'healthcheck': self.get_health_check(),
                    'networks': ['app_network']
                }
            },
            'volumes': {
                volume_name: {
                    'driver': 'local'
                }
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
        """Return the default port for MySQL."""
        return 3306

    def get_environment_variables(self) -> Dict[str, str]:
        """Return required environment variables for MySQL."""
        return {
            'MYSQL_DATABASE': '${DB_DATABASE}',
            'MYSQL_USER': '${DB_USERNAME}',
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

    def generate_server_config(self) -> bool:
        """Generate server-specific configuration files."""
        try:
            config_path = self.base_path / 'docker' / 'mysql'
            config_path.mkdir(parents=True, exist_ok=True)

            mysql_config = """[mysqld]
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
```

# chimera_stack/services/databases/postgresql.py

```py
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
        port = self._get_available_port(5432, 5500)  # Try ports between 5432 and 5500

        config = {
            'services': {
                'postgres': {
                    **self.config,
                    'ports': [f"{port}:5432"],
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
```

# chimera_stack/services/webservers/**init**.py

```py
# src/services/webservers/__init__.py
"""
Web Server Implementations

Provides specialized configurations for different web servers.
"""

from .nginx import NginxService
from .apache import ApacheService

__all__ = ['NginxService', 'ApacheService']
```

# chimera_stack/services/webservers/apache.py

```py
"""
Apache Web Server Service Implementation

Provides comprehensive configuration and management for Apache web server services.
This implementation focuses on creating a production-ready Apache environment
with support for both PHP and Python applications, incorporating security
best practices and performance optimizations.
"""

from pathlib import Path
from typing import Dict, Any, List
from .base import BaseWebServer

class ApacheService(BaseWebServer):
    """Apache web server service implementation."""

    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.config.update({
            'image': 'httpd:2.4-alpine',
            'restart': 'unless-stopped'
        })

    def get_docker_config(self) -> Dict[str, Any]:
        """Generate Docker service configuration for Apache."""
        http_port = self._get_available_port(8000, 8100)  # Try ports between 8000 and 8100
        https_port = self._get_available_port(8443, 8543)  # Try ports between 8443 and 8543

        config = {
            'services': {
                'apache': {
                    **self.config,
                    'ports': [
                        f"{http_port}:80",
                        f"{https_port}:443" if self.ssl_enabled else None
                    ],
                    'volumes': [
                        '.:/var/www/html:cached',
                        './docker/apache/conf/httpd.conf:/usr/local/apache2/conf/httpd.conf:ro',
                        './docker/apache/conf/extra:/usr/local/apache2/conf/extra:ro',
                        'apache_logs:/var/log/apache2'
                    ],
                    'environment': {
                        'APACHE_RUN_USER': 'www-data',
                        'APACHE_RUN_GROUP': 'www-data'
                    },
                    'depends_on': self._get_dependencies(),
                    'healthcheck': self.get_health_check()
                }
            },
            'volumes': {
                'apache_logs': None
            }
        }

        # Remove None values from ports list
        config['services']['apache']['ports'] = [p for p in config['services']['apache']['ports'] if p is not None]

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
        """Return the default port for Apache."""
        return 8000

    def get_health_check(self) -> Dict[str, Any]:
        """Generate health check configuration for Apache."""
        return {
            'test': ['CMD', 'wget', '--quiet', '--tries=1', '--spider', 'http://localhost/server-status'],
            'interval': '10s',
            'timeout': '5s',
            'retries': 3
        }

    def _get_dependencies(self) -> List[str]:
        """Determine service dependencies based on project configuration."""
        dependencies = []
        if self._uses_php():
            dependencies.append('php')
        return dependencies

    def _uses_php(self) -> bool:
        """Determine if the project uses PHP."""
        return True  # For now, always return True

    def get_default_ports(self) -> Dict[str, int]:
        """Return default ports for Apache development."""
        return {
            'http': 8000,
            'https': 8443
        }

    def generate_server_config(self) -> None:
        """Generate Apache configuration files."""
        config_path = self.base_path / 'docker' / 'apache'
        config_path.mkdir(parents=True, exist_ok=True)

        # Create configuration directories
        conf_path = config_path / 'conf'
        conf_path.mkdir(exist_ok=True)

        # Generate main configuration files
        self._create_main_config(conf_path)
        self._create_vhost_config(conf_path)
        self._create_security_config(conf_path)
        self._create_performance_config(conf_path)

        if self.ssl_enabled:
            self._create_ssl_config(conf_path)

    def _create_main_config(self, config_path: Path) -> None:
        """Create main Apache configuration."""
        main_config = """
ServerRoot "/usr/local/apache2"
Listen 80

# Load essential modules
LoadModule mpm_event_module modules/mod_mpm_event.so
LoadModule authz_core_module modules/mod_authz_core.so
LoadModule dir_module modules/mod_dir.so
LoadModule env_module modules/mod_env.so
LoadModule mime_module modules/mod_mime.so
LoadModule rewrite_module modules/mod_rewrite.so
LoadModule unixd_module modules/mod_unixd.so
LoadModule status_module modules/mod_status.so

# PHP module configuration if needed
<IfModule proxy_module>
    <IfModule proxy_fcgi_module>
        <FilesMatch "\\.php$">
            SetHandler "proxy:fcgi://php:9000"
        </FilesMatch>
    </IfModule>
</IfModule>

# Server configuration
ServerAdmin webmaster@localhost
ServerName localhost

# Document root configuration
DocumentRoot /var/www/html/public

# Include additional configuration files
IncludeOptional conf/extra/*.conf
"""
        (config_path / 'httpd.conf').write_text(main_config.strip())

    def _create_vhost_config(self, config_path: Path) -> None:
        """Create virtual host configuration."""
        vhost_config = f"""
<VirtualHost *:80>
    ServerName localhost
    DocumentRoot /var/www/html/public

    <Directory /var/www/html/public>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted

        # Enable .htaccess files
        <IfModule mod_rewrite.c>
            RewriteEngine On
            RewriteCond %{{REQUEST_FILENAME}} !-d
            RewriteCond %{{REQUEST_FILENAME}} !-f
            RewriteRule ^ index.php [L]
        </IfModule>
    </Directory>

    # Logging configuration
    ErrorLog /var/log/apache2/error.log
    CustomLog /var/log/apache2/access.log combined

    # Security headers
    Header set X-Content-Type-Options "nosniff"
    Header set X-Frame-Options "SAMEORIGIN"
    Header set X-XSS-Protection "1; mode=block"
</VirtualHost>
"""
        (config_path / 'extra' / 'vhost.conf').write_text(vhost_config.strip())

    def _create_security_config(self, config_path: Path) -> None:
        """Create security configuration."""
        security_config = r"""
# Server security configuration
ServerTokens Prod
ServerSignature Off
TraceEnable Off

# Directory security
<Directory />
    Options None
    AllowOverride None
    Require all denied
</Directory>

# Prevent access to .htaccess and other hidden files
<FilesMatch "^\.">
    Require all denied
</FilesMatch>

# Disable directory browsing
Options -Indexes

# Enable HTTP Strict Transport Security
Header always set Strict-Transport-Security "max-age=63072000"
"""
        (config_path / 'extra' / 'security.conf').write_text(security_config.strip())

    def _create_performance_config(self, config_path: Path) -> None:
        """Create performance optimization configuration."""
        performance_config = """
# MPM Configuration
<IfModule mpm_event_module>
    StartServers             3
    MinSpareThreads         75
    MaxSpareThreads        250
    ThreadLimit            64
    ThreadsPerChild        25
    MaxRequestWorkers     400
    MaxConnectionsPerChild  0
</IfModule>

# Enable compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/json
    AddOutputFilterByType DEFLATE application/x-javascript
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE text/html
    AddOutputFilterByType DEFLATE text/javascript
    AddOutputFilterByType DEFLATE text/plain
    AddOutputFilterByType DEFLATE text/xml
</IfModule>

# Enable caching
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresDefault "access plus 1 month"
    ExpiresByType text/css "access plus 1 year"
    ExpiresByType application/javascript "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
</IfModule>
"""
        (config_path / 'extra' / 'performance.conf').write_text(performance_config.strip())

    def _get_port_mappings(self) -> List[str]:
        """Generate port mappings for the service."""
        ports = [f"{self.get_default_port()}:80"]
        if self.ssl_enabled:
            ports.append("443:443")
        return ports

    def _get_volume_mappings(self) -> List[str]:
        """Generate volume mappings for the service."""
        return [
            '.:/var/www/html:cached',
            './docker/apache/conf/httpd.conf:/usr/local/apache2/conf/httpd.conf:ro',
            './docker/apache/conf/extra:/usr/local/apache2/conf/extra:ro',
            'apache_logs:/var/log/apache2'
        ]

    def _get_dependencies(self) -> List[str]:
        """Determine service dependencies based on project configuration."""
        dependencies = []
        if self._uses_php():
            dependencies.append('php')
        return dependencies

    def _uses_php(self) -> bool:
        """Determine if the project uses PHP."""
        # This could be enhanced to check project configuration
        return True
```

# chimera_stack/services/webservers/base.py

```py
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
```

# chimera_stack/services/webservers/nginx.py

```py
"""
Nginx Web Server Service Implementation

Provides a production-grade Nginx configuration system designed for modern web applications.
This implementation focuses on performance, security, and maintainability while supporting
both PHP and Python applications in development and production environments.
"""

from pathlib import Path
from typing import Dict, Any, List
from .base import BaseWebServer

class NginxService(BaseWebServer):
    """Nginx web server implementation optimized for development and production use."""

    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.config.update({
            'image': 'nginx:stable-alpine',
            'restart': 'unless-stopped',
            'user': '${NGINX_USER:-nginx}'  # Allow user override but default to nginx
        })

    def get_docker_config(self) -> Dict[str, Any]:
        """Generate Docker service configuration for Nginx."""
        http_port = self._get_available_port(8000, 8100)
        https_port = self._get_available_port(8443, 8543) if self.ssl_enabled else None

        config = {
            'services': {
                'nginx': {
                    **self.config,
                    'ports': [
                        f"{http_port}:80",
                        f"{https_port}:443" if https_port else None
                    ],
                    'volumes': [
                        '.:/var/www/html:cached',
                        './docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro',
                        './docker/nginx/conf.d:/etc/nginx/conf.d:ro',
                        'nginx_logs:/var/log/nginx'  # Add persistent log volume
                    ],
                    'depends_on': ['php'] if self._uses_php() else [],
                    'healthcheck': self.get_health_check(),
                    'networks': ['app_network']
                }
            },
            'volumes': {
                'nginx_logs': {
                    'driver': 'local'
                }
            }
        }

        # Remove None values from ports list
        config['services']['nginx']['ports'] = [p for p in config['services']['nginx']['ports'] if p]

        return config

    def generate_server_config(self) -> bool:
        """Generate Nginx configuration files."""
        try:
            config_path = self.base_path / 'docker' / 'nginx'
            conf_d_path = config_path / 'conf.d'

            # Create necessary directories
            self.create_directory(config_path)
            self.create_directory(conf_d_path)

            # Generate configuration files
            self._create_main_config(config_path)
            self._create_app_config(conf_d_path)

            # Create logs directory with proper permissions
            logs_path = config_path / 'logs'
            self.create_directory(logs_path)

            return True
        except Exception as e:
            print(f"Error generating Nginx configuration: {e}")
            return False

    def _create_main_config(self, config_path: Path) -> None:
        """Create main Nginx configuration."""
        main_config = """
user nginx;
worker_processes auto;
worker_rlimit_nofile 65535;

error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;

events {
    multi_accept on;
    worker_connections 65535;
}

http {
    charset utf-8;
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    server_tokens off;
    log_not_found off;
    types_hash_max_size 2048;
    client_max_body_size 16M;

    # MIME
    include mime.types;
    default_type application/octet-stream;

    # Logging
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                     '$status $body_bytes_sent "$http_referer" '
                     '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;
    error_log   /var/log/nginx/error.log warn;

    # Limits
    limit_req_log_level warn;
    limit_req_zone $binary_remote_addr zone=login:10m rate=10r/s;

    # SSL
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript application/rss+xml application/atom+xml image/svg+xml;

    # Include virtual host configs
    include /etc/nginx/conf.d/*.conf;
}
"""
        (config_path / 'nginx.conf').write_text(main_config.strip())

    def _create_app_config(self, config_path: Path) -> None:
        """Create application-specific server configuration."""
        app_config = r"""
map $uri $blogname {
    ~^(?P<blogpath>/[^/]+/)files/(.*)       $blogpath ;
}

server {
    listen 80;
    server_name localhost;
    root /var/www/html/public;
    index index.php index.html;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Health check endpoint
    location /ping {
        access_log off;
        return 200 'healthy\n';
    }

    # PHP handling
    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        try_files $uri =404;
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        fastcgi_pass php:9000;
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_param PATH_INFO $fastcgi_path_info;

        fastcgi_buffering on;
        fastcgi_buffer_size 16k;
        fastcgi_buffers 16 16k;

        fastcgi_connect_timeout 300;
        fastcgi_send_timeout 300;
        fastcgi_read_timeout 300;
    }

    # Deny access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    # Static file handling
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires max;
        log_not_found off;
    }

    # Enable directory listing for development
    location ~ ^/(src|public)/ {
        autoindex on;
    }
}
"""
        (config_path / 'default.conf').write_text(app_config.strip())

    def get_health_check(self) -> Dict[str, Any]:
        """Generate health check configuration for Nginx."""
        return {
            'test': ['CMD', 'wget', '--quiet', '--tries=1', '--spider', 'http://localhost/ping'],
            'interval': '10s',
            'timeout': '5s',
            'retries': 3,
            'start_period': '10s'
        }

    def get_default_port(self) -> int:
        """Return the default port for Nginx."""
        return 8000
```

# chimera_stack/templates/**init**.py

```py

```

# LICENSE

```
MIT License

Copyright (c) 2024 Jaouad Bouddehbine

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

```

# pyproject.toml

```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "chimera-stack"
version = "0.1.0"
description = "A Docker-centric development environment factory for PHP and Python projects"
readme = "README.md"
authors = [{ name = "Amirofcodes", email = "j.bouddehbine@it-students.fr" }]
license = { file = "LICENSE" }
classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
keywords = ["docker", "development", "environment", "php", "python"]
dependencies = [
    "click>=8.0.0",
    "docker>=6.0.0",
    "pyyaml>=6.0",
    "python-dotenv>=1.0.0",
]
requires-python = ">=3.8"

[project.urls]
Homepage = "https://github.com/Amirofcodes/chimera-stack"
Repository = "https://github.com/Amirofcodes/chimera-stack.git"

[project.scripts]
chimera = "chimera_stack.cli:cli"

[tool.setuptools]
packages = ["chimera_stack"]
```

# requirements.txt

```txt
# requirements.txt
click>=8.0.0
docker>=6.0.0
pyyaml>=6.0
python-dotenv>=1.0.0
```
