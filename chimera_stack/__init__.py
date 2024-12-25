# src/__init__.py
"""
ChimeraStack

A Docker-centric tool for creating consistent development environments.
"""

__version__ = "0.1.0"
__author__ = "Amirofcodes"
__license__ = "MIT"

from .core import Environment, ConfigurationManager, DockerManager
from .cli import cli

__all__ = ['Environment', 'ConfigurationManager', 'DockerManager', 'cli']