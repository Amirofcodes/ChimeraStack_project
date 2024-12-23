# src/core/docker_manager.py

"""
Docker Management Module

Handles Docker operations including container management, network setup,
and volume handling for development environments.
"""

import docker
from docker.errors import DockerException
from pathlib import Path
from typing import Dict, List, Optional

class DockerManager:
    """Manages Docker operations for development environments."""

    def __init__(self, project_name: str, base_path: Path):
        self.project_name = project_name
        self.base_path = base_path
        self.client = docker.from_env()
        self.networks: Dict = {}
        self.volumes: Dict = {}
        
    def verify_docker_installation(self) -> bool:
        """Verify Docker is installed and running."""
        try:
            self.client.ping()
            return True
        except DockerException:
            return False

    def create_network(self, network_name: Optional[str] = None) -> bool:
        """Create a Docker network for the project."""
        try:
            name = network_name or f"{self.project_name}_network"
            network = self.client.networks.create(
                name,
                driver="bridge",
                labels={"project": self.project_name}
            )
            self.networks[name] = network
            return True
        except DockerException as e:
            print(f"Error creating network: {e}")
            return False

    def create_volume(self, volume_name: Optional[str] = None) -> bool:
        """Create a Docker volume for persistent data."""
        try:
            name = volume_name or f"{self.project_name}_data"
            volume = self.client.volumes.create(
                name,
                labels={"project": self.project_name}
            )
            self.volumes[name] = volume
            return True
        except DockerException as e:
            print(f"Error creating volume: {e}")
            return False

    def cleanup(self) -> bool:
        """Clean up Docker resources created for the project."""
        try:
            for network in self.networks.values():
                network.remove()
            for volume in self.volumes.values():
                volume.remove()
            return True
        except DockerException as e:
            print(f"Error during cleanup: {e}")
            return False