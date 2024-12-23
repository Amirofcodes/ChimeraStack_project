"""
Django Framework Implementation

Handles Django-specific project setup and configuration, including database
setup and static file handling.
"""

import subprocess
from pathlib import Path
from typing import Dict, Any
from frameworks.python.base_python import BasePythonFramework

class DjangoFramework(BasePythonFramework):
    """Django framework implementation."""

    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.requirements = [
            'django',
            'gunicorn',
            'psycopg2-binary',
            'python-dotenv'
        ]

    def initialize_project(self) -> bool:
        """Initialize a new Django project."""
        try:
            project_path = self.base_path / self.project_name
            project_path.mkdir(exist_ok=True)
            
            # Create virtual environment
            if not self._setup_virtual_environment():
                return False
            
            # Install Django and create project
            subprocess.run([
                'docker', 'run', '--rm',
                '-v', f'{project_path}:/app',
                '-w', '/app',
                self.docker_requirements['python']['image'],
                'pip', 'install', 'django'
            ], check=True)
            
            subprocess.run([
                'docker', 'run', '--rm',
                '-v', f'{project_path}:/app',
                '-w', '/app',
                self.docker_requirements['python']['image'],
                'django-admin', 'startproject',
                'config', '.'
            ], check=True)
            
            return self._generate_dockerfile() and self._create_requirements_file()
        except Exception as e:
            print(f"Error initializing Django project: {e}")
            return False

    def setup_development_environment(self) -> bool:
        """Set up Django development environment."""
        try:
            project_path = self.base_path / self.project_name
            
            # Create necessary directories
            (project_path / 'static').mkdir(exist_ok=True)
            (project_path / 'media').mkdir(exist_ok=True)
            
            # Generate Django configuration
            self._generate_django_settings()
            self._generate_env_file()
            
            return True
        except Exception as e:
            print(f"Error setting up Django environment: {e}")
            return False

    def configure_docker(self) -> Dict[str, Any]:
        """Generate Django-specific Docker configuration."""
        base_config = super().configure_docker()
        
        # Add Django-specific services
        base_config['services'].update({
            'db': {
                'image': 'postgres:13',
                'ports': [f"{self.get_default_ports()['database']}:5432"],
                'environment': {
                    'POSTGRES_DB': '${DB_NAME}',
                    'POSTGRES_USER': '${DB_USER}',
                    'POSTGRES_PASSWORD': '${DB_PASSWORD}'
                }
            }
        })
        
        return base_config

    def _create_requirements_file(self) -> bool:
        """Create requirements.txt with necessary packages."""
        try:
            requirements_path = self.base_path / self.project_name / 'requirements.txt'
            requirements_path.write_text('\n'.join(self.requirements))
            return True
        except Exception as e:
            print(f"Error creating requirements.txt: {e}")
            return False