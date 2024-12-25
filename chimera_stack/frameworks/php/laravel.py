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