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
            # Define and create only directories that will be used
            public_path = self.base_path / 'public'
            src_path = self.base_path / 'src'
            pages_path = src_path / 'pages'

            # Create directories only when we're about to use them
            self.create_directory(pages_path)   # Creates parent directories too

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
            # Only create php configuration directory when needed
            php_path = self.base_path / 'docker' / 'php'
            self.create_directory(php_path)

            # Create necessary configurations
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