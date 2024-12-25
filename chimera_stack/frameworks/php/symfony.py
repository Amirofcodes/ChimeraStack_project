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