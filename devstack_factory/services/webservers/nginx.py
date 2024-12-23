# src/services/webservers/nginx.py

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
            'restart': 'unless-stopped'
        })

    def get_docker_config(self) -> Dict[str, Any]:
        """Generate Docker service configuration for Nginx."""
        config = {
            'services': {
                'nginx': {
                    **self.config,
                    'ports': self._get_port_mappings(),
                    'volumes': self._get_volume_mappings(),
                    'depends_on': self._get_dependencies(),
                    'healthcheck': self.get_health_check(),
                    'environment': {
                        'NGINX_ENVSUBST_TEMPLATE_DIR': '/etc/nginx/templates',
                        'NGINX_ENVSUBST_TEMPLATE_SUFFIX': '.template',
                        'NGINX_ENVSUBST_OUTPUT_DIR': '/etc/nginx/conf.d'
                    }
                }
            },
            'volumes': {
                'nginx_logs': None
            }
        }
        
        self.generate_server_config()
        return config

    def _get_dependencies(self) -> List[str]:
        """Determine service dependencies based on project type."""
        dependencies = []
        if self._is_php_project():
            dependencies.append('php')
        elif self._is_python_project():
            dependencies.append('app')
        return dependencies

    def generate_server_config(self) -> None:
        """Generate Nginx configuration structure and files."""
        config_root = self.base_path / self.project_name / 'docker' / 'nginx'
        config_root.mkdir(parents=True, exist_ok=True)

        self._create_directory_structure(config_root)
        self._generate_base_config(config_root)
        self._generate_app_config(config_root)
        self._generate_security_config(config_root)
        self._generate_optimization_config(config_root)

    def _create_directory_structure(self, config_root: Path) -> None:
        """Create Nginx configuration directory structure."""
        (config_root / 'conf.d').mkdir(exist_ok=True)
        (config_root / 'templates').mkdir(exist_ok=True)
        (config_root / 'includes').mkdir(exist_ok=True)

    def _generate_base_config(self, config_root: Path) -> None:
        """Generate main Nginx configuration."""
        base_config = """
user nginx;
worker_processes auto;
worker_rlimit_nofile 65535;

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
    types_hash_max_size 2048;
    client_max_body_size 16M;

    # MIME types
    include mime.types;
    default_type application/octet-stream;

    # SSL
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main buffer=512k flush=1m;
    error_log /var/log/nginx/error.log warn;

    # Includes
    include /etc/nginx/conf.d/*.conf;
}
"""
        (config_root / 'nginx.conf').write_text(base_config.strip())

    def _generate_app_config(self, config_root: Path) -> None:
        """Generate application-specific server configuration."""
        app_config = self._get_application_template()
        templates_path = config_root / 'templates'
        (templates_path / 'default.conf.template').write_text(app_config)

    def _get_application_template(self) -> str:
        """Get application-specific Nginx configuration template."""
        if self._is_php_project():
            return self._get_php_template()
        elif self._is_python_project():
            return self._get_python_template()
        return self._get_static_template()

    def _get_php_template(self) -> str:
        """Generate PHP application Nginx template."""
        return """
server {
    listen ${NGINX_PORT:-80};
    server_name ${NGINX_HOST:-localhost};
    root /var/www/html/public;
    index index.php index.html;

    include /etc/nginx/includes/security.conf;
    include /etc/nginx/includes/optimization.conf;

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
    }

    location ~ /\.(?!well-known) {
        deny all;
        access_log off;
        log_not_found off;
    }
}
"""

    def _get_python_template(self) -> str:
        """Generate Python application Nginx template."""
        return """
server {
    listen ${NGINX_PORT:-80};
    server_name ${NGINX_HOST:-localhost};

    include /etc/nginx/includes/security.conf;
    include /etc/nginx/includes/optimization.conf;

    location / {
        proxy_pass http://app:${APP_PORT:-8000};
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""

    def _is_php_project(self) -> bool:
        """Determine if the current project is PHP-based."""
        # Implementation will depend on project configuration
        return True

    def _is_python_project(self) -> bool:
        """Determine if the current project is Python-based."""
        # Implementation will depend on project configuration
        return False

    def _get_volume_mappings(self) -> List[str]:
        """Define volume mappings for Nginx service."""
        return [
            '.:/var/www/html:cached',
            './docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro',
            './docker/nginx/templates:/etc/nginx/templates:ro',
            './docker/nginx/includes:/etc/nginx/includes:ro',
            'nginx_logs:/var/log/nginx'
        ]

    def get_health_check(self) -> Dict[str, Any]:
        """Define health check configuration."""
        return {
            'test': ['CMD', 'wget', '--quiet', '--tries=1', '--spider', 'http://localhost/ping'],
            'interval': '10s',
            'timeout': '5s',
            'retries': 3,
            'start_period': '5s'
        }