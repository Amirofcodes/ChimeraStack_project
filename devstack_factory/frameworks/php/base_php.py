"""
PHP Framework Base Implementation

Provides common functionality for PHP-based frameworks.
"""

from pathlib import Path
from typing import Dict, Any
from devstack_factory.frameworks.base import BaseFramework

class BasePHPFramework(BaseFramework):
    """Base class for PHP frameworks."""

    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.docker_requirements = {
            'php': {
                'image': 'php:8.2-fpm',
                'extensions': ['pdo', 'pdo_mysql', 'mbstring']
            }
        }

    def get_default_ports(self) -> Dict[str, int]:
        return {
            'web': 8080,
            'php-fpm': 9000,
            'database': 3306
        }

    def configure_docker(self) -> Dict[str, Any]:
        """Generate base PHP Docker configuration."""
        return {
            'services': {
                'php': {
                    'image': self.docker_requirements['php']['image'],
                    'volumes': [
                        f'./{self.project_name}:/var/www/html'
                    ]
                }
            }
        }