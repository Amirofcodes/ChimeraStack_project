"""
DevStack Factory Core Module

This module provides the core functionality for creating and managing
development environments using Docker containers.
"""

__version__ = "0.1.0"
__author__ = "Jaouad Bouddehbine"
__license__ = "MIT"

from typing import Dict, List, Optional, Union
from .environment import Environment
from .config import ConfigurationManager
from .docker_manager import DockerManager
from .setup_wizard import SetupWizard

__all__ = [
    "Environment",
    "ConfigurationManager",
    "DockerManager",
    "SetupWizard",
]