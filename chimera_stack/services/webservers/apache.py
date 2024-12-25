# src/services/webservers/apache.py

"""
Apache Web Server Service Implementation

Provides comprehensive configuration and management for Apache web server services.
This implementation focuses on creating a production-ready Apache environment
with support for both PHP and Python applications, incorporating security
best practices and performance optimizations.
"""

from pathlib import Path
from typing import Dict, Any, List
from .base import BaseWebServer

class ApacheService(BaseWebServer):
    """Apache web server service implementation."""

    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.config.update({
            'image': 'httpd:2.4-alpine',
            'restart': 'unless-stopped'
        })

    def get_docker_config(self) -> Dict[str, Any]:
        """Generate Docker service configuration for Apache."""
        config = {
            'services': {
                'apache': {
                    **self.config,
                    'ports': self._get_port_mappings(),
                    'volumes': self._get_volume_mappings(),
                    'depends_on': self._get_dependencies(),
                    'environment': {
                        'APACHE_RUN_USER': 'www-data',
                        'APACHE_RUN_GROUP': 'www-data'
                    },
                    'healthcheck': self.get_health_check()
                }
            },
            'volumes': {
                'apache_logs': None
            }
        }
        
        # Generate Apache configuration files
        self.generate_server_config()
        
        return config

    def get_default_port(self) -> int:
        """Return the default port for Apache."""
        return 80

    def get_health_check(self) -> Dict[str, Any]:
        """Generate health check configuration for Apache."""
        return {
            'test': ['CMD', 'wget', '--quiet', '--tries=1', '--spider', 'http://localhost/server-status'],
            'interval': '10s',
            'timeout': '5s',
            'retries': 3
        }

    def generate_server_config(self) -> None:
        """Generate Apache configuration files."""
        config_path = self.base_path / self.project_name / 'docker' / 'apache'
        config_path.mkdir(parents=True, exist_ok=True)

        # Create configuration directories
        conf_path = config_path / 'conf'
        conf_path.mkdir(exist_ok=True)
        
        # Generate main configuration files
        self._create_main_config(conf_path)
        self._create_vhost_config(conf_path)
        self._create_security_config(conf_path)
        self._create_performance_config(conf_path)

        if self.ssl_enabled:
            self._create_ssl_config(conf_path)

    def _create_main_config(self, config_path: Path) -> None:
        """Create main Apache configuration."""
        main_config = """
ServerRoot "/usr/local/apache2"
Listen 80

# Load essential modules
LoadModule mpm_event_module modules/mod_mpm_event.so
LoadModule authz_core_module modules/mod_authz_core.so
LoadModule dir_module modules/mod_dir.so
LoadModule env_module modules/mod_env.so
LoadModule mime_module modules/mod_mime.so
LoadModule rewrite_module modules/mod_rewrite.so
LoadModule unixd_module modules/mod_unixd.so
LoadModule status_module modules/mod_status.so

# PHP module configuration if needed
<IfModule proxy_module>
    <IfModule proxy_fcgi_module>
        <FilesMatch "\\.php$">
            SetHandler "proxy:fcgi://php:9000"
        </FilesMatch>
    </IfModule>
</IfModule>

# Server configuration
ServerAdmin webmaster@localhost
ServerName localhost

# Document root configuration
DocumentRoot /var/www/html/public

# Include additional configuration files
IncludeOptional conf/extra/*.conf
"""
        (config_path / 'httpd.conf').write_text(main_config.strip())

    def _create_vhost_config(self, config_path: Path) -> None:
        """Create virtual host configuration."""
        vhost_config = f"""
<VirtualHost *:80>
    ServerName localhost
    DocumentRoot /var/www/html/public
    
    <Directory /var/www/html/public>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
        
        # Enable .htaccess files
        <IfModule mod_rewrite.c>
            RewriteEngine On
            RewriteCond %{{REQUEST_FILENAME}} !-d
            RewriteCond %{{REQUEST_FILENAME}} !-f
            RewriteRule ^ index.php [L]
        </IfModule>
    </Directory>
    
    # Logging configuration
    ErrorLog /var/log/apache2/error.log
    CustomLog /var/log/apache2/access.log combined
    
    # Security headers
    Header set X-Content-Type-Options "nosniff"
    Header set X-Frame-Options "SAMEORIGIN"
    Header set X-XSS-Protection "1; mode=block"
</VirtualHost>
"""
        (config_path / 'extra' / 'vhost.conf').write_text(vhost_config.strip())

    def _create_security_config(self, config_path: Path) -> None:
        """Create security configuration."""
        security_config = r"""
# Server security configuration
ServerTokens Prod
ServerSignature Off
TraceEnable Off

# Directory security
<Directory />
    Options None
    AllowOverride None
    Require all denied
</Directory>

# Prevent access to .htaccess and other hidden files
<FilesMatch "^\.">
    Require all denied
</FilesMatch>

# Disable directory browsing
Options -Indexes

# Enable HTTP Strict Transport Security
Header always set Strict-Transport-Security "max-age=63072000"
"""
        (config_path / 'extra' / 'security.conf').write_text(security_config.strip())

    def _create_performance_config(self, config_path: Path) -> None:
        """Create performance optimization configuration."""
        performance_config = """
# MPM Configuration
<IfModule mpm_event_module>
    StartServers             3
    MinSpareThreads         75
    MaxSpareThreads        250
    ThreadLimit            64
    ThreadsPerChild        25
    MaxRequestWorkers     400
    MaxConnectionsPerChild  0
</IfModule>

# Enable compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/json
    AddOutputFilterByType DEFLATE application/x-javascript
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE text/html
    AddOutputFilterByType DEFLATE text/javascript
    AddOutputFilterByType DEFLATE text/plain
    AddOutputFilterByType DEFLATE text/xml
</IfModule>

# Enable caching
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresDefault "access plus 1 month"
    ExpiresByType text/css "access plus 1 year"
    ExpiresByType application/javascript "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
</IfModule>
"""
        (config_path / 'extra' / 'performance.conf').write_text(performance_config.strip())

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
            './docker/apache/conf/httpd.conf:/usr/local/apache2/conf/httpd.conf:ro',
            './docker/apache/conf/extra:/usr/local/apache2/conf/extra:ro',
            'apache_logs:/var/log/apache2'
        ]

    def _get_dependencies(self) -> List[str]:
        """Determine service dependencies based on project configuration."""
        dependencies = []
        if self._uses_php():
            dependencies.append('php')
        return dependencies

    def _uses_php(self) -> bool:
        """Determine if the project uses PHP."""
        # This could be enhanced to check project configuration
        return True