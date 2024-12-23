# src/frameworks/python/vanilla.py

"""
Vanilla Python Implementation

Provides a Docker-based development environment for pure Python applications
without framework constraints. This implementation focuses on creating a reliable,
production-ready setup for custom Python development projects.
"""

from pathlib import Path
from typing import Dict, Any
from devstack_factory.frameworks.python.base_python import BasePythonFramework

class VanillaPythonFramework(BasePythonFramework):
    """Vanilla Python implementation for framework-free development."""

    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.docker_requirements.update({
            'python': {
                'image': 'python:3.11-slim',
                'environment': {
                    'PYTHONUNBUFFERED': '1',
                    'PYTHONDONTWRITEBYTECODE': '1',
                    'PYTHON_ENV': 'development'
                }
            }
        })

    def initialize_project(self) -> bool:
        """Initialize a minimal Python project structure."""
        try:
            project_path = self.base_path / self.project_name
            project_path.mkdir(exist_ok=True)
            
            # Create a minimal application entry point
            app_content = '''"""
Main application module.

This module serves as the entry point for the application.
"""

def main():
    """Main application function."""
    print("Python Development Environment Ready")

if __name__ == "__main__":
    main()
'''
            (project_path / 'main.py').write_text(app_content)
            
            # Create requirements.txt with basic development tools
            requirements = [
                'pytest>=7.0.0',
                'python-dotenv>=1.0.0'
            ]
            (project_path / 'requirements.txt').write_text('\n'.join(requirements))
            
            return True
        except Exception as e:
            print(f"Error initializing vanilla Python project: {e}")
            return False

    def configure_docker(self) -> Dict[str, Any]:
        """Generate Docker configuration for vanilla Python development."""
        config = {
            'services': {
                'app': {
                    'build': {
                        'context': '.',
                        'dockerfile': 'docker/python/Dockerfile'
                    },
                    'volumes': [
                        '.:/app:cached'
                    ],
                    'environment': self.docker_requirements['python']['environment'],
                    'command': 'python main.py'
                }
            }
        }

        if self._uses_database():
            config['services']['db'] = {
                'image': 'postgres:13',
                'environment': {
                    'POSTGRES_DB': '${POSTGRES_DB}',
                    'POSTGRES_USER': '${POSTGRES_USER}',
                    'POSTGRES_PASSWORD': '${POSTGRES_PASSWORD}'
                },
                'ports': [f"{self.get_default_ports()['database']}:5432"],
                'volumes': ['postgres_data:/var/lib/postgresql/data']
            }
            config['volumes'] = {'postgres_data': None}
            
        return config

    def setup_development_environment(self) -> bool:
        """Set up vanilla Python development environment."""
        try:
            self._create_docker_configs()
            self._create_env_file()
            return True
        except Exception as e:
            print(f"Error setting up Python environment: {e}")
            return False

    def get_default_ports(self) -> Dict[str, int]:
        """Return default ports for Python development."""
        return {
            'database': 5432
        }

    def _create_docker_configs(self) -> None:
        """Create necessary Docker configuration files."""
        docker_path = self.base_path / self.project_name / 'docker'
        docker_path.mkdir(exist_ok=True)
        
        self._create_python_dockerfile(docker_path / 'python')

    def _create_python_dockerfile(self, path: Path) -> None:
        """Generate Python Dockerfile."""
        path.mkdir(exist_ok=True)
        dockerfile_content = f"""
FROM {self.docker_requirements['python']['image']}

# Set working directory
WORKDIR /app

# Install system dependencies and development tools
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set Python path
ENV PYTHONPATH=/app

CMD ["python", "main.py"]
"""
        (path / 'Dockerfile').write_text(dockerfile_content.strip())

    def _create_env_file(self) -> None:
        """Create .env file with development settings."""
        env_content = '''
PYTHON_ENV=development
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
'''
        env_path = self.base_path / self.project_name / '.env'
        env_path.write_text(env_content.strip())

    def _uses_database(self) -> bool:
        """Determine if the project requires a database."""
        # This could be enhanced to check configuration or prompt the user
        return True