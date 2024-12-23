"""
Flask Framework Implementation

Handles Flask-specific Docker environment setup while maintaining simplicity 
and flexibility. This implementation focuses on creating a production-ready
Docker environment without imposing specific project structure decisions.
"""

from pathlib import Path
from typing import Dict, Any
import subprocess
from frameworks.python.base_python import BasePythonFramework

class FlaskFramework(BasePythonFramework):
    """Flask framework implementation focusing on Docker environment setup."""

    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.docker_requirements.update({
            'python': {
                'image': 'python:3.11-slim',
                'environment': {
                    'FLASK_APP': 'app',
                    'FLASK_ENV': 'development',
                    'PYTHONUNBUFFERED': '1',
                }
            }
        })

    def initialize_project(self) -> bool:
        """Initialize a minimal Flask project using pip."""
        try:
            project_path = self.base_path / self.project_name
            project_path.mkdir(exist_ok=True)
            
            # Create requirements.txt
            requirements = [
                'flask>=2.0.0',
                'python-dotenv>=1.0.0',
                'gunicorn>=20.1.0'
            ]
            (project_path / 'requirements.txt').write_text('\n'.join(requirements))
            
            # Create minimal app.py
            app_content = '''
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Flask Docker Development Environment'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
'''
            (project_path / 'app.py').write_text(app_content.strip())
            
            return True
        except Exception as e:
            print(f"Error initializing Flask project: {e}")
            return False

    def configure_docker(self) -> Dict[str, Any]:
        """Generate Flask-specific Docker configuration."""
        config = {
            'services': {
                'web': {
                    'build': {
                        'context': '.',
                        'dockerfile': 'docker/python/Dockerfile'
                    },
                    'ports': [f"{self.get_default_ports()['web']}:5000"],
                    'volumes': [
                        '.:/app:cached'
                    ],
                    'environment': self.docker_requirements['python']['environment'],
                    'depends_on': ['redis'] if self._uses_redis() else []
                }
            }
        }

        # Add Redis if specified
        if self._uses_redis():
            config['services']['redis'] = {
                'image': 'redis:alpine',
                'ports': [f"{self.get_default_ports()['cache']}:6379"]
            }

        return config

    def get_default_ports(self) -> Dict[str, int]:
        """Return default ports for Flask development."""
        return {
            'web': 5000,
            'cache': 6379
        }

    def setup_development_environment(self) -> bool:
        """Set up Flask development environment configurations."""
        try:
            self._create_docker_configs()
            self._create_env_file()
            return True
        except Exception as e:
            print(f"Error setting up Flask environment: {e}")
            return False

    def _create_docker_configs(self) -> None:
        """Create necessary Docker configuration files."""
        docker_path = self.base_path / self.project_name / 'docker'
        docker_path.mkdir(exist_ok=True)
        
        self._create_python_dockerfile(docker_path / 'python')

    def _create_python_dockerfile(self, path: Path) -> None:
        """Generate Python Dockerfile for Flask."""
        path.mkdir(exist_ok=True)
        dockerfile_content = f"""
FROM {self.docker_requirements['python']['image']}

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
"""
        (path / 'Dockerfile').write_text(dockerfile_content.strip())

    def _create_env_file(self) -> None:
        """Create .env file with development settings."""
        env_content = '''
FLASK_APP=app
FLASK_ENV=development
FLASK_DEBUG=1
'''
        env_path = self.base_path / self.project_name / '.env'
        env_path.write_text(env_content.strip())

    def _uses_redis(self) -> bool:
        """Check if the project uses Redis."""
        requirements_path = self.base_path / self.project_name / 'requirements.txt'
        return requirements_path.exists() and 'redis' in requirements_path.read_text()