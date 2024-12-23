# src/core/config.py

"""
Configuration Management Module

Handles configuration loading, validation, and management for development environments.
Supports multiple environment types (development, testing, production) and framework-specific settings.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass

@dataclass
class ServiceConfig:
    """Configuration settings for individual services."""
    name: str
    image: str
    ports: list[str]
    volumes: list[str]
    environment: Dict[str, str]

class ConfigurationManager:
    """Manages configuration for development environments."""

    DEFAULT_CONFIG = {
        'version': '3.8',
        'environment': 'development',
        'services': {},
        'networks': ['app_network'],
        'volumes': ['app_data']
    }

    def __init__(self, project_name: str, base_path: Path):
        self.project_name = project_name
        self.base_path = base_path
        self.config_path = base_path / 'config'
        self.config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()
        self.environment_vars: Dict[str, str] = {}

    def load_config(self, environment: str = 'development') -> bool:
        """Load configuration for specified environment."""
        try:
            self.config_path.mkdir(exist_ok=True)
            config_file = self.config_path / f'{environment}.yaml'
            
            if config_file.exists():
                with open(config_file, 'r') as f:
                    env_config = yaml.safe_load(f)
                self.config.update(env_config)
            
            self._load_environment_variables(environment)
            return True
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False

    def save_config(self, environment: str = 'development') -> bool:
        """Save current configuration to file."""
        try:
            config_file = self.config_path / f'{environment}.yaml'
            with open(config_file, 'w') as f:
                yaml.safe_dump(self.config, f)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False

    def _load_environment_variables(self, environment: str) -> None:
        """Load environment-specific variables."""
        env_file = self.base_path / f'.env.{environment}'
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        self.environment_vars[key] = value

    def generate_docker_compose(self) -> Dict[str, Any]:
        """Generate Docker Compose configuration."""
        return {
            'version': self.config['version'],
            'services': self._generate_services_config(),
            'networks': {name: {'driver': 'bridge'} 
                        for name in self.config['networks']},
            'volumes': {name: {'driver': 'local'} 
                       for name in self.config['volumes']}
        }

    def _generate_services_config(self) -> Dict[str, Any]:
        """Generate configuration for all services."""
        services_config = {}
        for service_name, service_data in self.config['services'].items():
            service_config = S