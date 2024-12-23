# src/frameworks/php/laravel.py

"""
Laravel Framework Implementation

Handles Laravel-specific project setup and configuration.
"""

from pathlib import Path
from typing import Dict, Any
from frameworks.php.base_php import BasePHPFramework
import subprocess

class LaravelFramework(BasePHPFramework):
    """Laravel framework implementation."""

    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.docker_requirements.update({
            'composer': {
                'image': 'composer:latest'
            },
            'node': {
                'image': 'node:18-alpine'
            }
        })

    def initialize_project(self) -> bool:
        """Initialize a new Laravel project."""
        try:
            # Use Docker to create Laravel project
            subprocess.run([
                'docker', 'run', '--rm',
                '-v', f'{self.base_path}:/app',
                '-w', '/app',
                'composer:latest',
                'create-project',
                'laravel/laravel',
                self.project_name
            ], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error initializing Laravel project: {e}")
            return False

    def setup_development_environment(self) -> bool:
        """Set up Laravel development environment."""
        try:
            project_path = self.base_path / self.project_name
            
            # Copy .env.example to .env
            env_example = project_path / '.env.example'
            env_file = project_path / '.env'
            if env_example.exists():
                env_example.rename(env_file)
            
            # Generate application key
            subprocess.run([
                'docker', 'run', '--rm',
                '-v', f'{project_path}:/var/www/html',
                '-w', '/var/www/html',
                self.docker_requirements['php']['image'],
                'php', 'artisan', 'key:generate'
            ], check=True)
            
            return True
        except Exception as e:
            print(f"Error setting up Laravel environment: {e}")
            return False

    def configure_docker(self) -> Dict[str, Any]:
        """Generate Laravel-specific Docker configuration."""
        base_config = super().configure_docker()
        
        # Add Laravel-specific services
        base_config['services'].update({
            'nginx': {
                'image': 'nginx:alpine',
                'ports': [f"{self.get_default_ports()['web']}:80"],
                'volumes': [
                    f'./{self.project_name}:/var/www/html',
                    './docker/nginx/conf.d:/etc/nginx/conf.d'
                ]
            },
            'mysql': {
                'image': 'mysql:8.0',
                'ports': [f"{self.get_default_ports()['database']}:3306"]
            }
        })
        
        return base_config