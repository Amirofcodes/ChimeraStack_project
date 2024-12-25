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
            # Create essential directories
            public_path = self.base_path / 'public'
            src_path = self.base_path / 'src'
            pages_path = src_path / 'pages'
            
            for path in [public_path, src_path, pages_path]:
                path.mkdir(exist_ok=True, parents=True)
            
            # Create index.php
            index_content = '''<?php
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
}
'''
            (public_path / 'index.php').write_text(index_content)
            
            # Create bootstrap.php
            bootstrap_content = '''<?php
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
});
'''
            (src_path / 'bootstrap.php').write_text(bootstrap_content)
            
            # Create home.php
            home_content = '''<?php
declare(strict_types=1);

$title = 'Welcome to DevStack Factory';
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
</body>
</html>
'''
            (pages_path / 'home.php').write_text(home_content)
            
            return True
            
        except Exception as e:
            print(f"Error initializing vanilla PHP project: {e}")
            return False

    def setup_development_environment(self) -> bool:
        """Set up development environment configurations."""
        try:
            # Create docker configurations
            self._create_docker_configs()
            
            # Create .gitignore
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
            (self.base_path / '.gitignore').write_text(gitignore_content.strip())
            
            return True
        except Exception as e:
            print(f"Error setting up development environment: {e}")
            return False

    def _create_php_dockerfile(self, path: Path) -> None:
        """Generate enhanced PHP Dockerfile with proper extension installation."""
        path.mkdir(exist_ok=True, parents=True)
        
        # Prepare system packages installation command
        system_packages = ' '.join(self.docker_requirements['php']['system_packages'])
        
        # Prepare PHP extensions installation commands
        extension_commands = []
        for ext, config in self.docker_requirements['php']['extensions'].items():
            if config and config.get('configure'):
                extension_commands.append(f'docker-php-ext-configure {ext}')
            extension_commands.append(f'docker-php-ext-install {ext}')
        
        extensions_installation = ' && \\\n    '.join(extension_commands)
        
        dockerfile_content = f"""FROM {self.docker_requirements['php']['image']}

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    {system_packages} \\
    && rm -rf /var/lib/apt/lists/*

# Install PHP extensions
RUN {extensions_installation}

# Configure PHP
COPY docker/php/php.ini /usr/local/etc/php/conf.d/custom.ini

WORKDIR /var/www/html
"""
        (path / 'Dockerfile').write_text(dockerfile_content.strip())

    def _create_docker_configs(self) -> None:
        """Create necessary Docker configuration files."""
        docker_path = self.base_path / 'docker'
        docker_path.mkdir(exist_ok=True)
        
        self._create_php_dockerfile(docker_path / 'php')
        self._create_php_config(docker_path / 'php')

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
                }
            }
        }
        
        if self._uses_database():
            config['services']['mysql'] = {
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
            config['volumes'] = {
                'mysql_data': {
                    'driver': 'local'
                }
            }
        
        return config

    def _create_php_config(self, path: Path) -> None:
        """Generate PHP configuration."""
        path.mkdir(exist_ok=True, parents=True)
        php_config = """
[PHP]
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
opcache.revalidate_freq=60
"""
        (path / 'php.ini').write_text(php_config.strip())

    def _uses_database(self) -> bool:
        """Determine if the project uses a database."""
        return True  # For now, always return True

    def get_default_ports(self) -> Dict[str, int]:
        """Return default ports for PHP development."""
        return {
            'web': 8080,
            'database': 3306
        }