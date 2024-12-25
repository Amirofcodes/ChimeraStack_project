"""
Django Framework Implementation

Provides Docker environment configuration for Django projects while preserving
Django's standard project structure and conventions. This implementation focuses
on creating a production-ready Docker environment that aligns with Django's
recommended deployment practices.
"""

from pathlib import Path
from typing import Dict, Any
import subprocess
from chimera_stack.frameworks.python.base_python import BasePythonFramework

class DjangoFramework(BasePythonFramework):
    """Django framework implementation focusing on Docker environment setup."""

    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.docker_requirements.update({
            'python': {
                'image': 'python:3.11-slim',
                'environment': {
                    'DJANGO_SETTINGS_MODULE': 'config.settings',
                    'PYTHONUNBUFFERED': '1',
                    'DATABASE_URL': 'postgresql://postgres:postgres@db:5432/postgres'
                }
            }
        })

    def initialize_project(self) -> bool:
        """Initialize a Django project using Docker."""
        try:
            project_path = self.base_path / self.project_name
            
            # Create project using Django's startproject through Docker
            subprocess.run([
                'docker', 'run', '--rm',
                '-v', f'{self.base_path}:/app',
                '-w', '/app',
                self.docker_requirements['python']['image'],
                'bash', '-c',
                f'pip install django && django-admin startproject config {self.project_name}'
            ], check=True)

            # Create requirements.txt
            requirements = [
                'django>=4.2.0',
                'psycopg2-binary>=2.9.0',
                'gunicorn>=20.1.0',
                'python-dotenv>=1.0.0'
            ]
            (project_path / 'requirements.txt').write_text('\n'.join(requirements))
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error initializing Django project: {e}")
            return False

    def configure_docker(self) -> Dict[str, Any]:
        """Generate Django-specific Docker configuration."""
        config = {
            'services': {
                'web': {
                    'build': {
                        'context': '.',
                        'dockerfile': 'docker/python/Dockerfile'
                    },
                    'command': 'gunicorn config.wsgi:application --bind 0.0.0.0:8000',
                    'volumes': [
                        '.:/app:cached',
                        'static_volume:/app/staticfiles',
                        'media_volume:/app/media'
                    ],
                    'ports': [f"{self.get_default_ports()['web']}:8000"],
                    'environment': self.docker_requirements['python']['environment'],
                    'depends_on': ['db']
                },
                'db': {
                    'image': 'postgres:13',
                    'volumes': ['postgres_data:/var/lib/postgresql/data/'],
                    'environment': {
                        'POSTGRES_DB': '${POSTGRES_DB}',
                        'POSTGRES_USER': '${POSTGRES_USER}',
                        'POSTGRES_PASSWORD': '${POSTGRES_PASSWORD}'
                    },
                    'ports': [f"{self.get_default_ports()['database']}:5432"]
                }
            },
            'volumes': {
                'postgres_data': None,
                'static_volume': None,
                'media_volume': None
            }
        }
        return config

    def get_default_ports(self) -> Dict[str, int]:
        """Return default ports for Django development."""
        return {
            'web': 8000,
            'database': 5432
        }

    def setup_development_environment(self) -> bool:
        """Set up Django development environment configurations."""
        try:
            self._create_docker_configs()
            self._create_env_file()
            return True
        except Exception as e:
            print(f"Error setting up Django environment: {e}")
            return False

    def _create_docker_configs(self) -> None:
        """Create necessary Docker configuration files."""
        docker_path = self.base_path / self.project_name / 'docker'
        docker_path.mkdir(exist_ok=True)
        
        self._create_python_dockerfile(docker_path / 'python')

    def _create_python_dockerfile(self, path: Path) -> None:
        """Generate Python Dockerfile for Django."""
        path.mkdir(exist_ok=True)
        dockerfile_content = f"""
FROM {self.docker_requirements['python']['image']}

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create directory for static files
RUN mkdir -p /app/staticfiles /app/media

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "config.wsgi:application"]
"""
        (path / 'Dockerfile').write_text(dockerfile_content.strip())

    def _create_env_file(self) -> None:
        """Create .env file with development settings."""
        env_content = '''
DEBUG=1
SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=config.settings
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgresql://postgres:postgres@db:5432/postgres
'''
        env_path = self.base_path / self.project_name / '.env'
        env_path.write_text(env_content.strip())