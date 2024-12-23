"""
Python Framework Base Implementation

Provides common functionality for Python-based frameworks including virtual
environment management and package handling.
"""

from pathlib import Path
import subprocess
import venv
from typing import Dict, Any
from frameworks.base import BaseFramework

class BasePythonFramework(BaseFramework):
    """Base class for Python frameworks providing shared functionality."""

    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.docker_requirements = {
            'python': {
                'image': 'python:3.11-slim',
                'environment': {
                    'PYTHONUNBUFFERED': '1',
                    'PYTHONDONTWRITEBYTECODE': '1'
                }
            }
        }
        self.venv_path = self.base_path / self.project_name / 'venv'

    def get_default_ports(self) -> Dict[str, int]:
        return {
            'web': 8000,
            'database': 5432,
            'cache': 6379
        }

    def _setup_virtual_environment(self) -> bool:
        """Create and configure a Python virtual environment."""
        try:
            venv.create(self.venv_path, with_pip=True)
            return True
        except Exception as e:
            print(f"Error creating virtual environment: {e}")
            return False

    def configure_docker(self) -> Dict[str, Any]:
        """Generate base Python Docker configuration."""
        return {
            'services': {
                'app': {
                    'build': {
                        'context': '.',
                        'dockerfile': 'Dockerfile'
                    },
                    'volumes': [
                        f'./{self.project_name}:/app'
                    ],
                    'environment': self.docker_requirements['python']['environment']
                }
            }
        }

    def _generate_dockerfile(self) -> bool:
        """Generate a Dockerfile for the Python application."""
        try:
            dockerfile_content = f"""
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \\
    PYTHONDONTWRITEBYTECODE=1 \\
    PIP_NO_CACHE_DIR=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
"""
            dockerfile_path = self.base_path / self.project_name / 'Dockerfile'
            dockerfile_path.write_text(dockerfile_content.strip())
            return True
        except Exception as e:
            print(f"Error generating Dockerfile: {e}")
            return False