# src/frameworks/python/vanilla.py

"""
Vanilla Python Implementation

Provides a Docker-based development environment for pure Python applications
without framework constraints. This implementation focuses on creating a reliable,
production-ready setup for custom Python development projects.
"""

from pathlib import Path
from typing import Dict, Any
from chimera_stack.frameworks.python.base_python import BasePythonFramework

class VanillaPythonFramework(BasePythonFramework):
    def initialize_project(self) -> bool:
        try:
            project_path = self.base_path / self.project_name
            
            # Create project structure
            src_path = project_path / 'src'
            tests_path = project_path / 'tests'
            for path in [src_path, tests_path]:
                path.mkdir(exist_ok=True, parents=True)
            
            # Create main application module
            app_content = '''"""
Application entry point.

This module provides a basic WSGI application structure that can be extended
as needed. It includes basic routing and request handling capabilities.
"""
import os
import json
from typing import Callable, Dict, Tuple, Any
from wsgiref.simple_server import make_server

class Application:
    def __init__(self):
        self.routes: Dict[str, Callable] = {}
        self._register_routes()

    def _register_routes(self) -> None:
        """Register application routes."""
        self.routes = {
            '/': self.home,
            '/health': self.health_check
        }

    def home(self, environ: Dict) -> Tuple[str, Dict[str, str], str]:
        """Handle home route."""
        return '200 OK', {'Content-Type': 'application/json'}, json.dumps({
            'message': 'Python Development Environment Ready',
            'status': 'active'
        })

    def health_check(self, environ: Dict) -> Tuple[str, Dict[str, str], str]:
        """Handle health check route."""
        return '200 OK', {'Content-Type': 'application/json'}, json.dumps({
            'status': 'healthy',
            'version': os.getenv('APP_VERSION', '1.0.0')
        })

    def __call__(self, environ: Dict, start_response: Callable) -> Any:
        """WSGI application callable."""
        path = environ.get('PATH_INFO', '/')
        handler = self.routes.get(path)

        if handler is None:
            status = '404 Not Found'
            headers = {'Content-Type': 'application/json'}
            response_body = json.dumps({'error': 'Not Found'})
        else:
            try:
                status, headers, response_body = handler(environ)
            except Exception as e:
                status = '500 Internal Server Error'
                headers = {'Content-Type': 'application/json'}
                response_body = json.dumps({'error': str(e)})

        start_response(status, list(headers.items()))
        return [response_body.encode('utf-8')]

def create_app() -> Application:
    """Create and configure the application."""
    return Application()

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 8000))
    
    with make_server('', port, app) as httpd:
        print(f'Serving on port {port}...')
        httpd.serve_forever()
'''
            (src_path / 'app.py').write_text(app_content)
            
            # Create requirements.txt with development tools
            requirements = [
                'gunicorn>=20.1.0',
                'python-dotenv>=1.0.0',
                'pytest>=7.0.0',
                'pytest-cov>=4.0.0',
                'black>=22.0.0',
                'isort>=5.0.0',
                'pylint>=2.0.0'
            ]
            (project_path / 'requirements.txt').write_text('\n'.join(requirements))
            
            # Create basic test
            test_content = '''"""Basic application tests."""
import json
from src.app import create_app

def test_home_route():
    """Test the home route response."""
    app = create_app()
    environ = {'PATH_INFO': '/'}
    
    def start_response(status, headers):
        assert status == '200 OK'
        assert ('Content-Type', 'application/json') in headers
    
    response = app(environ, start_response)
    response_data = json.loads(response[0].decode('utf-8'))
    
    assert 'message' in response_data
    assert 'status' in response_data
    assert response_data['status'] == 'active'

def test_health_check():
    """Test the health check route."""
    app = create_app()
    environ = {'PATH_INFO': '/health'}
    
    def start_response(status, headers):
        assert status == '200 OK'
    
    response = app(environ, start_response)
    response_data = json.loads(response[0].decode('utf-8'))
    
    assert response_data['status'] == 'healthy'
'''
            (tests_path / 'test_app.py').write_text(test_content)
            
            return True
            
        except Exception as e:
            print(f"Error initializing vanilla Python project: {e}")
            return False

    def _create_python_dockerfile(self, path: Path) -> None:
        """Generate enhanced Python Dockerfile."""
        path.mkdir(exist_ok=True)
        dockerfile_content = f"""
FROM {self.docker_requirements['python']['image']}

# Set working directory
WORKDIR /app

# Install system dependencies and development tools
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set Python path and environment
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--reload", "src.app:create_app()"]
"""
        (path / 'Dockerfile').write_text(dockerfile_content.strip())