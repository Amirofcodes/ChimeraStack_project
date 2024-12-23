# src/services/webservers/base.py

"""
Base Web Server Service Implementation

Defines the core interface and shared functionality for web server services,
ensuring consistent configuration and management across different web server
implementations.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List

class BaseWebServer(ABC):
    """Abstract base class for web server implementations."""

    def __init__(self, project_name: str, base_path: Path):
        self.project_name = project_name
        self.base_path = base_path
        self.config: Dict[str, Any] = {}
        self.ssl_enabled = False

    @abstractmethod
    def get_docker_config(self) -> Dict[str, Any]:
        """Generate Docker service configuration for the web server."""
        pass

    @abstractmethod
    def get_default_port(self) -> int:
        """Return the default port for the web server."""
        pass

    @abstractmethod
    def generate_server_config(self) -> None:
        """Generate server-specific configuration files."""
        pass

    def enable_ssl(self, certificate_path: str, key_path: str) -> None:
        """Enable SSL/TLS support for the web server."""
        self.ssl_enabled = True
        self.ssl_certificate = certificate_path
        self.ssl_key = key_path

class NginxService(BaseWebServer):
    """Nginx web server service implementation."""

    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.config.update({
            'image': 'nginx:alpine',
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
                    'depends_on': ['php'] if self._uses_php() else [],
                    'healthcheck': self.get_health_check()
                }
            }
        }
        
        # Generate Nginx configuration files
        self.generate_server_config()
        
        return config

    def get_default_port(self) -> int:
        """Return the default port for Nginx."""
        return 80

    def get_health_check(self) -> Dict[str, Any]:
        """Generate health check configuration for Nginx."""
        return {
            'test': ['CMD', 'wget', '--quiet', '--tries=1', '--spider', 'http://localhost'],
            'interval': '10s',
            'timeout': '5s',
            'retries': 3
        }

    def generate_server_config(self) -> None:
        """Generate Nginx configuration files."""
        config_path = self.base_path / self.project_name / 'docker' / 'nginx'
        config_path.mkdir(parents=True, exist_ok=True)

        # Create conf.d directory
        conf_d_path = config_path / 'conf.d'
        conf_d_path.mkdir(exist_ok=True)

        # Generate main configuration
        self._create_main_config(conf_d_path)
        
        # Generate SSL configuration if enabled
        if self.ssl_enabled:
            self._create_ssl_config(conf_d_path)

        # Generate optimization configuration
        self._create_optimization_config(config_path)

    def _create_main_config(self, config_path: Path) -> None:
        """Create main Nginx server configuration."""
        main_config = f"""
server {{
    listen 80;
    server_name localhost;
    root /var/www/html/public;
    index index.php index.html;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Content-Type-Options "nosniff";

    # Logging configuration
    access_log /var/log/nginx/access.log combined buffer=512k flush=1m;
    error_log /var/log/nginx/error.log warn;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types text/plain text/css application/json application/javascript application/x-javascript text/xml application/xml application/xml+rss text/javascript;

    location / {{
        try_files $uri $uri/ /index.php?$query_string;
    }}

    {self._get_php_location() if self._uses_php() else ''}

    # Deny access to sensitive files
    location ~ /\. {{
        deny all;
        access_log off;
        log_not_found off;
    }}
}}
"""
        (config_path / 'default.conf').write_text(main_config.strip())

    def _create_ssl_config(self, config_path: Path) -> None:
        """Create SSL configuration for Nginx."""
        ssl_config = f"""
server {{
    listen 443 ssl http2;
    server_name localhost;
    root /var/www/html/public;

    ssl_certificate {self.ssl_certificate};
    ssl_certificate_key {self.ssl_key};
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;
    # Add your SSL specific configurations here
}}
"""
        (config_path / 'ssl.conf').write_text(ssl_config.strip())

    def _create_optimization_config(self, config_path: Path) -> None:
        """Create performance optimization configuration."""
        optimization_config = """
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
    log_not_found off;
    types_hash_max_size 2048;
    client_max_body_size 16M;

    # MIME
    include mime.types;
    default_type application/octet-stream;

    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log warn;

    # Load configs
    include /etc/nginx/conf.d/*.conf;
}
"""
        (config_path / 'nginx.conf').write_text(optimization_config.strip())

    def _get_port_mappings(self) -> List[str]:
        """Generate port mappings for the service."""
        ports = [f"{self.get_default_port()}:80"]
        if self.ssl_enabled:
            ports.append("443:443")
        return ports

    def _get_volume_mappings(self) -> List[str]:
        """Generate volume mappings for the service."""
        return [
            '.:/var/www/html:cached',
            './docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro',
            './docker/nginx/conf.d:/etc/nginx/conf.d:ro',
            'nginx_logs:/var/log/nginx'
        ]

    def _uses_php(self) -> bool:
        """Determine if the project uses PHP."""
        # This could be enhanced to check project configuration
        return True

    def _get_php_location(self) -> str:
        """Generate PHP location configuration."""
        return """
    location ~ \.php$ {
        fastcgi_pass php:9000;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
        fastcgi_intercept_errors on;
        fastcgi_buffer_size 16k;
        fastcgi_buffers 4 16k;
    }
"""