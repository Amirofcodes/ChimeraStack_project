"""
Base Framework Interface

Defines the contract that all framework implementations must follow,
ensuring consistent behavior across different programming languages and frameworks.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional

class BaseFramework(ABC):
    """Abstract base class for framework implementations."""

    def __init__(self, project_name: str, base_path: Path):
        self.project_name = project_name
        self.base_path = base_path
        self.docker_requirements: Dict[str, Dict] = {}

    @abstractmethod
    def initialize_project(self) -> bool:
        """Initialize a new project with the framework."""
        pass

    @abstractmethod
    def configure_docker(self) -> Dict[str, Any]:
        """Generate Docker configuration for the framework."""
        pass

    @abstractmethod
    def get_default_ports(self) -> Dict[str, int]:
        """Return default ports used by the framework."""
        pass

    @abstractmethod
    def setup_development_environment(self) -> bool:
        """Set up development environment for the framework."""
        pass