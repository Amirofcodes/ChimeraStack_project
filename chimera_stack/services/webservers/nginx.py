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
        http_port = self._get_available_port(8000, 8100)  # Try ports between 8000 and 8100
        https_port = self._get_available_port(8443, 8543)  # Try ports between 8443 and 8543
        
        config = {
            'services': {
                'nginx': {
                    **self.config,
                    'ports': [
                        f"{http_port}:80",
                        f"{https_port}:443" if self.ssl_enabled else None
                    ],
                    'volumes': [
                        '.:/var/www/html:cached',
                        './docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro',
                        './docker/nginx/conf.d:/etc/nginx/conf.d:ro'
                    ],
                    'depends_on': ['php'] if self._uses_php() else [],
                    'healthcheck': self.get_health_check()
                }
            }
        }
        
        # Remove None values from ports list
        config['services']['nginx']['ports'] = [p for p in config['services']['nginx']['ports'] if p is not None]
        
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
        """Return the default port for Nginx."""
        return 8000

    def get_health_check(self) -> Dict[str, Any]:
        """Generate health check configuration for Nginx."""
        return {
            'test': ['CMD', 'wget', '--quiet', '--tries=1', '--spider', 'http://localhost/ping'],
            'interval': '10s',
            'timeout': '5s',
            'retries': 3
        }

    def generate_server_config(self) -> bool:
        """Generate Nginx configuration files."""
        try:
            config_path = self.base_path / 'docker' / 'nginx'
            config_path.mkdir(parents=True, exist_ok=True)

            # Create configuration directories
            conf_d_path = config_path / 'conf.d'
            conf_d_path.mkdir(exist_ok=True)

            # Generate main configuration files
            self._create_main_config(config_path)
            self._create_app_config(conf_d_path)

            return True
        except Exception as e:
            print(f"Error generating Nginx configuration: {e}")
            return False

    def _create_main_config(self, config_path: Path) -> None:
        """Create main Nginx configuration."""
        main_config = """
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

    # MIME
    include mime.types;
    default_type application/octet-stream;

    # Logging
    access_log /var/log/nginx/access.log combined buffer=512k flush=1m;
    error_log /var/log/nginx/error.log warn;

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
        app_config = """
server {
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
}
"""
        (config_path / 'default.conf').write_text(app_config.strip())

    def _uses_php(self) -> bool:
        """Determine if the project uses PHP."""
        return True  # For now, always return True for PHP projects