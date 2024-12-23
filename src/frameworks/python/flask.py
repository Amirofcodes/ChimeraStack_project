"""
Flask Framework Implementation

Handles Flask-specific project setup and configuration. Creates a production-ready
Flask application structure following best practices and the Application Factory pattern.
"""

import subprocess
from pathlib import Path
from typing import Dict, Any
from frameworks.python.base_python import BasePythonFramework

class FlaskFramework(BasePythonFramework):
    """Flask framework implementation with production-ready configuration."""

    def __init__(self, project_name: str, base_path: Path):
        super().__init__(project_name, base_path)
        self.requirements = [
            'flask',
            'python-dotenv',
            'flask-sqlalchemy',
            'flask-migrate',
            'gunicorn',
            'redis'
        ]

    def initialize_project(self) -> bool:
        """Initialize a new Flask project with a modular structure."""
        try:
            project_path = self.base_path / self.project_name
            project_path.mkdir(exist_ok=True)
            
            # Create project structure
            app_path = project_path / 'app'
            app_path.mkdir(exist_ok=True)
            
            # Create package directories
            self._create_package_structure(app_path)
            
            # Generate initial files
            self._generate_app_files(project_path)
            self._generate_dockerfile()
            self._create_requirements_file()
            
            return True
        except Exception as e:
            print(f"Error initializing Flask project: {e}")
            return False

    def _create_package_structure(self, app_path: Path) -> None:
        """Create a modular Flask application structure."""
        directories = [
            'static',
            'templates',
            'models',
            'views',
            'services',
            'utils'
        ]
        
        for directory in directories:
            (app_path / directory).mkdir(exist_ok=True)
            (app_path / directory / '__init__.py').touch()

        # Create main application files
        self._generate_init_file(app_path)
        self._generate_config_file(app_path)

    def _generate_init_file(self, app_path: Path) -> None:
        """Generate the main Flask application factory."""
        content = '''
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    from .views import main_bp
    app.register_blueprint(main_bp)
    
    return app
'''
        (app_path / '__init__.py').write_text(content.strip())

    def _generate_config_file(self, app_path: Path) -> None:
        """Generate configuration classes for different environments."""
        content = '''
import os
from pathlib import Path

basedir = Path(__file__).parent.parent

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + str(basedir / 'data-dev.sqlite')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + str(basedir / 'data.sqlite')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
'''
        (app_path / 'config.py').write_text(content.strip())

    def configure_docker(self) -> Dict[str, Any]:
        """Generate Flask-specific Docker configuration."""
        base_config = super().configure_docker()
        
        # Update Python service configuration
        base_config['services']['app'].update({
            'command': 'gunicorn -b 0.0.0.0:5000 "app:create_app()"',
            'ports': [f"{self.get_default_ports()['web']}:5000"],
            'environment': {
                'FLASK_APP': 'app',
                'FLASK_ENV': 'development',
                'DATABASE_URL': 'postgresql://postgres:postgres@db:5432/postgres'
            }
        })
        
        # Add additional services
        base_config['services'].update({
            'db': {
                'image': 'postgres:13',
                'environment': {
                    'POSTGRES_DB': '${DB_NAME}',
                    'POSTGRES_USER': '${DB_USER}',
                    'POSTGRES_PASSWORD': '${DB_PASSWORD}'
                },
                'ports': [f"{self.get_default_ports()['database']}:5432"]
            },
            'redis': {
                'image': 'redis:6-alpine',
                'ports': [f"{self.get_default_ports()['cache']}:6379"]
            }
        })
        
        return base_config

    def setup_development_environment(self) -> bool:
        """Set up Flask development environment."""
        try:
            project_path = self.base_path / self.project_name
            
            # Create .env file
            env_content = '''
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://postgres:postgres@db:5432/postgres
'''
            (project_path / '.env').write_text(env_content.strip())
            
            # Create example test
            self._create_example_test(project_path)
            
            return True
        except Exception as e:
            print(f"Error setting up Flask environment: {e}")
            return False

    def _create_example_test(self, project_path: Path) -> None:
        """Create an example test file."""
        test_content = '''
import unittest
from app import create_app, db

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
'''
        tests_dir = project_path / 'tests'
        tests_dir.mkdir(exist_ok=True)
        (tests_dir / '__init__.py').touch()
        (tests_dir / 'test_basics.py').write_text(test_content.strip())