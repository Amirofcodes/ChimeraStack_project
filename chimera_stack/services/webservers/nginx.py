"""
Nginx Web Server Service Implementation

Provides a production-grade Nginx configuration system designed for modern web applications.
"""

from pathlib import Path
from typing import Dict, Any, List
from .base import BaseWebServer

class NginxService(BaseWebServer):
    """Nginx web server implementation."""

    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.config.update({
            'image': 'nginx:stable-alpine',
            'restart': 'unless-stopped'
        })

    def get_docker_config(self) -> Dict[str, Any]:
        """Generate Docker service configuration for Nginx."""
        http_port = self._get_available_port(8000, 8100)

        config = {
            'services': {
                'nginx': {
                    **self.config,
                    'ports': [f"{http_port}:80"],
                    'volumes': [
                        '.:/var/www/html:cached',
                        './docker/nginx/conf.d:/etc/nginx/conf.d:ro'
                    ],
                    'depends_on': ['php'] if self._uses_php() else [],
                    'healthcheck': self.get_health_check(),
                    'networks': ['app_network']
                }
            }
        }
        return config

    def generate_server_config(self) -> bool:
        """Generate Nginx configuration files."""
        try:
            # Create necessary directories first
            nginx_path = self.base_path / 'docker' / 'nginx'
            conf_d_path = nginx_path / 'conf.d'
            
            # Force create these directories as they're required
            nginx_path.mkdir(parents=True, exist_ok=True)
            conf_d_path.mkdir(parents=True, exist_ok=True)

            # Create configuration files
            self._create_default_conf(conf_d_path)
            return True
        except Exception as e:
            print(f"Error generating Nginx configuration: {e}")
            return False

    def _create_default_conf(self, path: Path) -> None:
        """Create default.conf file with optimized settings."""
        nginx_config = r'''server {
    listen 80;
    server_name localhost;
    root /var/www/html/public;
    index index.php index.html;

    charset utf-8;
    client_max_body_size 128M;
    fastcgi_read_timeout 1800;
    fastcgi_buffers 16 16k;
    fastcgi_buffer_size 32k;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Built-in health check location (no PHP processing needed)
    location = /health {
        access_log off;
        add_header Content-Type text/plain;
        return 200 'healthy';
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

    # Static file handling
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires max;
        access_log off;
        add_header Cache-Control "public";
    }

    # Enable directory listing for development
    location ~ ^/(src|public)/ {
        autoindex on;
    }
}'''
        config_file = path / 'default.conf'
        config_file.write_text(nginx_config)

    def get_health_check(self) -> Dict[str, Any]:
        """Generate health check configuration for Nginx."""
        return {
            'test': ['CMD', 'curl', '-f', 'http://localhost/health'],
            'interval': '10s',
            'timeout': '5s',
            'retries': 3,
            'start_period': '10s'
        }

    def get_default_port(self) -> int:
        """Return the default port for Nginx."""
        return 8080

    def _uses_php(self) -> bool:
        """Determine if the project uses PHP."""
        return True