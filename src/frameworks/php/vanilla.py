# src/frameworks/php/vanilla.py

"""
Vanilla PHP Implementation

Provides a clean, framework-free PHP development environment using Docker.
Focuses on creating a reliable setup for custom PHP development without
imposing any framework constraints.
"""

from pathlib import Path
from typing import Dict, Any
from frameworks.php.base_php import BasePHPFramework

class VanillaPHPFramework(BasePHPFramework):
    """Vanilla PHP implementation for framework-free development."""

    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.docker_requirements.update({
            'php': {
                'image': 'php:8.2-fpm',
                'extensions': [
                    'pdo',
                    'pdo_mysql',
                    'mbstring',
                    'zip',
                    'exif',
                    'gd'
                ]
            }
        })

    def initialize_project(self) -> bool:
        """Initialize a minimal PHP project structure."""
        try:
            project_path = self.base_path / self.project_name
            project_path.mkdir(exist_ok=True)
            
            # Create public directory for web root
            (project_path / 'public').mkdir(exist_ok=True)
            
            # Create a minimal index.php
            index_content = '''<?php
declare(strict_types=1);

phpinfo();
'''
            (project_path / 'public' / 'index.php').write_text(index_content)
            
            return True
        except Exception as e:
            print(f"Error initializing vanilla PHP project: {e}")
            return False

    def configure_docker(self) -> Dict[str, Any]:
        """Generate Docker configuration for vanilla PHP development."""
        config = {
            'services': {
                'php': {
                    'build': {
                        'context': '.',
                        'dockerfile': 'docker/php/Dockerfile'
                    },
                    'volumes': [
                        '.:/var/www/html:cached'
                    ]
                },
                'nginx': {
                    'image': 'nginx:alpine',
                    'ports': [f"{self.get_default_ports()['web']}:80"],
                    'volumes': [
                        '.:/var/www/html:cached',
                        './docker/nginx/conf.d:/etc/nginx/conf.d:ro'
                    ],
                    'depends_on': ['php']
                }
            }
        }
        
        # Add database if requested
        if self._uses_database():
            config['services']['mysql'] = {
                'image': 'mysql:8.0',
                'environment': {
                    'MYSQL_DATABASE': '${DB_NAME}',
                    'MYSQL_USER': '${DB_USER}',
                    'MYSQL_PASSWORD': '${DB_PASSWORD}',
                    'MYSQL_ROOT_PASSWORD': '${DB_ROOT_PASSWORD}'
                },
                'ports': [f"{self.get_default_ports()['database']}:3306"],
                'volumes': ['mysql_data:/var/lib/mysql']
            }
            config['volumes'] = {'mysql_data': None}
        
        return config

    def setup_development_environment(self) -> bool:
        """Set up vanilla PHP development environment."""
        try:
            self._create_docker_configs()
            return True
        except Exception as e:
            print(f"Error setting up PHP environment: {e}")
            return False

    def get_default_ports(self) -> Dict[str, int]:
        """Return default ports for PHP development."""
        return {
            'web': 8080,
            'database': 3306
        }

    def _create_docker_configs(self) -> None:
        """Create necessary Docker configuration files."""
        docker_path = self.base_path / self.project_name / 'docker'
        docker_path.mkdir(exist_ok=True)
        
        self._create_php_dockerfile(docker_path / 'php')
        self._create_nginx_config(docker_path / 'nginx')

    def _create_php_dockerfile(self, path: Path) -> None:
        """Generate PHP Dockerfile."""
        path.mkdir(exist_ok=True)
        dockerfile_content = f"""
FROM {self.docker_requirements['php']['image']}

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    zip \\
    unzip \\
    libpng-dev

# Install PHP extensions
RUN docker-php-ext-install {' '.join(self.docker_requirements['php']['extensions'])}

WORKDIR /var/www/html
"""
        (path / 'Dockerfile').write_text(dockerfile_content.strip())

    def _create_nginx_config(self, path: Path) -> None:
        """Generate Nginx configuration."""
        path.mkdir(exist_ok=True)
        nginx_config = """
server {
    listen 80;
    server_name localhost;
    root /var/www/html/public;
    index index.php index.html;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        fastcgi_pass php:9000;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }
}
"""
        (path / 'conf.d').mkdir(exist_ok=True)
        (path / 'conf.d' / 'default.conf').write_text(nginx_config.strip())