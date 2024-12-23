"""
Symfony Framework Implementation

Handles Symfony-specific Docker environment setup while maintaining the standard
Symfony installation and project structure conventions.
"""

from pathlib import Path
from typing import Dict, Any
import subprocess
from frameworks.php.base_php import BasePHPFramework

class SymfonyFramework(BasePHPFramework):
    """Symfony framework implementation focusing on Docker environment setup."""

    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.docker_requirements.update({
            'php': {
                'image': 'php:8.2-fpm',
                'extensions': [
                    'intl',
                    'pdo_mysql',
                    'pdo_pgsql',
                    'zip',
                    'xml',
                    'curl',
                    'opcache',
                    'mbstring'
                ]
            },
            'composer': {
                'image': 'composer:latest'
            }
        })

    def initialize_project(self) -> bool:
        """Initialize Symfony project using Docker."""
        try:
            # Use Composer through Docker to create the Symfony project
            subprocess.run([
                'docker', 'run', '--rm',
                '-v', f'{self.base_path}:/app',
                '-w', '/app',
                'composer:latest',
                'create-project',
                'symfony/skeleton',
                self.project_name
            ], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error initializing Symfony project: {e}")
            return False

    def configure_docker(self) -> Dict[str, Any]:
        """Generate Symfony-specific Docker configuration."""
        config = {
            'services': {
                'php': {
                    'build': {
                        'context': '.',
                        'dockerfile': 'php/Dockerfile'
                    },
                    'volumes': [
                        '.:/var/www/symfony:cached',
                        './php/conf.d/symfony.ini:/usr/local/etc/php/conf.d/symfony.ini:ro'
                    ],
                    'depends_on': ['database']
                },
                'nginx': {
                    'image': 'nginx:alpine',
                    'ports': [f"{self.get_default_ports()['web']}:80"],
                    'volumes': [
                        '.:/var/www/symfony:cached',
                        './nginx/conf.d/default.conf:/etc/nginx/conf.d/default.conf:ro'
                    ],
                    'depends_on': ['php']
                },
                'database': {
                    'image': 'mysql:8.0',
                    'environment': {
                        'MYSQL_ROOT_PASSWORD': '${MYSQL_ROOT_PASSWORD}',
                        'MYSQL_DATABASE': '${MYSQL_DATABASE}',
                        'MYSQL_USER': '${MYSQL_USER}',
                        'MYSQL_PASSWORD': '${MYSQL_PASSWORD}'
                    },
                    'ports': [f"{self.get_default_ports()['database']}:3306"],
                    'volumes': [
                        'db-data:/var/lib/mysql:cached'
                    ]
                }
            },
            'volumes': {
                'db-data': None
            }
        }
        return config

    def setup_development_environment(self) -> bool:
        """Set up Symfony development environment configurations."""
        try:
            self._create_docker_configs()
            self._create_env_file()
            return True
        except Exception as e:
            print(f"Error setting up Symfony environment: {e}")
            return False

    def get_default_ports(self) -> Dict[str, int]:
        """Return default ports for Symfony development."""
        return {
            'web': 8080,
            'database': 3306
        }

    def _create_docker_configs(self) -> None:
        """Create necessary Docker configuration files."""
        docker_path = self.base_path / self.project_name / 'docker'
        docker_path.mkdir(exist_ok=True)
        
        # Create PHP configuration
        self._create_php_dockerfile(docker_path / 'php')
        
        # Create Nginx configuration
        self._create_nginx_config(docker_path / 'nginx')

    def _create_php_dockerfile(self, path: Path) -> None:
        """Generate PHP Dockerfile with required extensions."""
        path.mkdir(exist_ok=True)
        dockerfile_content = f"""
FROM {self.docker_requirements['php']['image']}

RUN apt-get update && apt-get install -y \\
    git \\
    unzip \\
    libicu-dev \\
    zlib1g-dev \\
    libxml2-dev \\
    && docker-php-ext-install \\
    {' '.join(self.docker_requirements['php']['extensions'])}

WORKDIR /var/www/symfony

RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer
"""
        (path / 'Dockerfile').write_text(dockerfile_content.strip())

    def _create_nginx_config(self, path: Path) -> None:
        """Generate Nginx configuration for Symfony."""
        path.mkdir(exist_ok=True)
        nginx_config = """
server {
    listen 80;
    server_name localhost;
    root /var/www/symfony/public;

    location / {
        try_files $uri /index.php$is_args$args;
    }

    location ~ ^/index\\.php(/|$) {
        fastcgi_pass php:9000;
        fastcgi_split_path_info ^(.+\\.php)(/.*)$;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        fastcgi_param DOCUMENT_ROOT $realpath_root;
        internal;
    }

    location ~ \\.php$ {
        return 404;
    }

    error_log /var/log/nginx/project_error.log;
    access_log /var/log/nginx/project_access.log;
}
"""
        (path / 'conf.d').mkdir(exist_ok=True)
        (path / 'conf.d' / 'default.conf').write_text(nginx_config.strip())