"""
Vanilla PHP Implementation

Provides a clean, framework-free PHP development environment using Docker.
Focuses on creating a production-ready setup that follows best practices.
"""

from pathlib import Path
from typing import Dict, Any
from chimera_stack.frameworks.php.base_php import BasePHPFramework

class VanillaPHPFramework(BasePHPFramework):
    def __init__(self, project_name: str, base_path: Path):
        """Initialize VanillaPHPFramework with specific requirements."""
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
            # Create essential directories
            public_path = self.base_path / 'public'
            src_path = self.base_path / 'src'
            pages_path = src_path / 'pages'

            # Create directories in order
            for path in [public_path, src_path, pages_path]:
                path.mkdir(exist_ok=True, parents=True)

            # Create essential files
            self._create_index_file(public_path)
            self._create_bootstrap_file(src_path)
            self._create_home_file(pages_path)
            self._create_env_file(self.base_path)
            self._create_gitignore(self.base_path)

            # Create only necessary Docker directories
            docker_path = self.base_path / 'docker'
            (docker_path / 'nginx' / 'conf.d').mkdir(parents=True, exist_ok=True)
            (docker_path / 'php').mkdir(parents=True, exist_ok=True)
            (docker_path / 'mysql').mkdir(parents=True, exist_ok=True)

            return True
        except Exception as e:
            print(f"Error initializing vanilla PHP project: {e}")
            return False

    def _create_index_file(self, path: Path) -> None:
        """Create the main index.php file."""
        content = r'''<?php
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
        content = r'''<?php
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
        content = r'''<?php
    declare(strict_types=1);

    $title = 'Welcome to ChimeraStack';
    ?>

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title><?= htmlspecialchars($title) ?></title>
    </head>
    <body>
        <h1><?= htmlspecialchars($title) ?></h1>
        <p>Your development environment is ready.</p>
        <p><a href="/info">View PHP Info</a></p>
        
        <!-- Database Connection Test -->
        <?php
        try {
            $dsn = "mysql:host={$_ENV['DB_HOST']};dbname={$_ENV['DB_DATABASE']}";
            $pdo = new PDO($dsn, $_ENV['DB_USERNAME'], $_DB_PASSWORD);
            echo '<p style="color: green;">✓ Database connection successful!</p>';
        } catch (PDOException $e) {
            echo '<p style="color: red;">✗ Database connection failed: ' . htmlspecialchars($e->getMessage()) . '</p>';
        }
        ?>
    </body>
    </html>'''
        (path / 'home.php').write_text(content)  # Fixed: just create home.php in the provided path

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
            self._create_docker_configs()
            return True
        except Exception as e:
            print(f"Error setting up development environment: {e}")
            return False

    def _create_docker_configs(self) -> None:
        """Create necessary Docker configuration files."""
        docker_path = self.base_path / 'docker'
        docker_path.mkdir(exist_ok=True)

        self._create_php_dockerfile(docker_path / 'php')
        self._create_php_config(docker_path / 'php')
        self._create_nginx_config(docker_path / 'nginx')

    def configure_docker(self) -> Dict[str, Any]:
        """Generate Docker configuration for vanilla PHP development."""
        config = {
            'version': '3.8',
            'services': {
                'php': {
                    'build': {
                        'context': '.',
                        'dockerfile': 'docker/php/Dockerfile'
                    },
                    'volumes': [
                        '.:/var/www/html:cached'
                    ],
                    'environment': {
                        'PHP_DISPLAY_ERRORS': '${PHP_DISPLAY_ERRORS}',
                        'PHP_ERROR_REPORTING': '${PHP_ERROR_REPORTING}',
                        'PHP_MEMORY_LIMIT': '${PHP_MEMORY_LIMIT}',
                        'PHP_MAX_EXECUTION_TIME': '${PHP_MAX_EXECUTION_TIME}',
                        'PHP_POST_MAX_SIZE': '${PHP_POST_MAX_SIZE}',
                        'PHP_UPLOAD_MAX_FILESIZE': '${PHP_UPLOAD_MAX_FILESIZE}'
                    },
                    'networks': ['app_network']
                },
                'nginx': {
                    'image': 'nginx:alpine',
                    'ports': [f"{self.get_default_ports()['web']}:80"],
                    'volumes': [
                        '.:/var/www/html:cached',
                        './docker/nginx/conf.d:/etc/nginx/conf.d:ro'
                    ],
                    'depends_on': ['php'],
                    'networks': ['app_network']
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
                    'volumes': ['mysql_data:/var/lib/mysql'],
                    'networks': ['app_network']
                }
            },
            'networks': {
                'app_network': {
                    'driver': 'bridge'
                }
            },
            'volumes': {
                'mysql_data': {
                    'driver': 'local'
                }
            }
        }
        return config

    def _create_php_dockerfile(self, path: Path) -> None:
        """Generate PHP Dockerfile."""
        path.mkdir(exist_ok=True, parents=True)
        content = r'''FROM php:8.2-fpm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git zip unzip libpng-dev libonig-dev libzip-dev \
    && rm -rf /var/lib/apt/lists/*

# Install PHP extensions
RUN docker-php-ext-install pdo pdo_mysql mbstring zip exif \
    && docker-php-ext-configure gd \
    && docker-php-ext-install gd

# Configure PHP
COPY docker/php/php.ini /usr/local/etc/php/conf.d/custom.ini

WORKDIR /var/www/html'''
        (path / 'Dockerfile').write_text(content)

    def _create_php_config(self, path: Path) -> None:
        """Generate PHP configuration."""
        path.mkdir(exist_ok=True, parents=True)
        content = r'''[PHP]
display_errors = ${PHP_DISPLAY_ERRORS}
error_reporting = ${PHP_ERROR_REPORTING}
memory_limit = ${PHP_MEMORY_LIMIT}
max_execution_time = ${PHP_MAX_EXECUTION_TIME}
post_max_size = ${PHP_POST_MAX_SIZE}
upload_max_filesize = ${PHP_UPLOAD_MAX_FILESIZE}

[Date]
date.timezone = UTC

[Session]
session.save_handler = files
session.save_path = /tmp
session.gc_maxlifetime = 1800

[opcache]
opcache.enable=1
opcache.memory_consumption=128
opcache.interned_strings_buffer=8
opcache.max_accelerated_files=4000
opcache.validate_timestamps=1
opcache.revalidate_freq=60'''
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