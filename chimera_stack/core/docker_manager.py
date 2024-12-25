"""
Docker Management Module

Handles Docker operations including container management, network setup,
and volume handling for development environments.
"""

import subprocess
from pathlib import Path
from typing import Dict, List, Optional

class DockerManager:
    """Manages Docker operations for development environments."""

    def __init__(self, project_name: str, base_path: Path):
        self.project_name = project_name
        self.base_path = base_path
        self.networks: Dict = {}
        self.volumes: Dict = {}

    def verify_docker_installation(self) -> bool:
        """Verify Docker is installed and running."""
        try:
            subprocess.run(['docker', 'info'], capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def create_network(self, network_name: Optional[str] = None) -> bool:
        """Create a Docker network for the project."""
        try:
            name = network_name or f"{self.project_name}_network"
            result = subprocess.run(
                ['docker', 'network', 'create', name],
                capture_output=True,
                text=True,
                check=True
            )
            self.networks[name] = name
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error creating network: {e.stderr}")
            return False

    def create_volume(self, volume_name: Optional[str] = None) -> bool:
        """Create a Docker volume for persistent data."""
        try:
            name = volume_name or f"{self.project_name}_data"
            result = subprocess.run(
                ['docker', 'volume', 'create', name],
                capture_output=True,
                text=True,
                check=True
            )
            self.volumes[name] = name
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error creating volume: {e.stderr}")
            return False

    def start_environment(self) -> bool:
        """Start the Docker environment using docker-compose."""
        try:
            result = subprocess.run(
                ['docker-compose', 'up', '-d'],
                cwd=self.base_path,
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error starting environment: {e.stderr}")
            return False
        except Exception as e:
            print(f"Error starting environment: {e}")
            return False

    def stop_environment(self) -> bool:
        """Stop the Docker environment using docker-compose."""
        try:
            result = subprocess.run(
                ['docker-compose', 'down'],
                cwd=self.base_path,
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error stopping environment: {e.stderr}")
            return False
        except Exception as e:
            print(f"Error stopping environment: {e}")
            return False

    def cleanup(self) -> bool:
        """Clean up Docker resources created for the project."""
        try:
            for network in self.networks.values():
                subprocess.run(
                    ['docker', 'network', 'rm', network],
                    capture_output=True,
                    check=True
                )
            for volume in self.volumes.values():
                subprocess.run(
                    ['docker', 'volume', 'rm', volume],
                    capture_output=True,
                    check=True
                )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error during cleanup: {e.stderr}")
            return False