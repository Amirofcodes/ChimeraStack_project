# src/cli.py

"""
Command Line Interface Module

The main entry point for the DevStack Factory tool. Provides a user-friendly
command-line interface for creating and managing development environments.
"""

import click
import os
from pathlib import Path
from typing import Dict, Any

from core.config import ConfigurationManager
from core.environment import Environment
from core.docker_manager import DockerManager

@click.group()
@click.version_option(version='0.1.0')
def cli():
    """DevStack Factory - Development Environment Management Tool"""
    pass

@cli.command()
@click.argument('project_name')
@click.option('--language', type=click.Choice(['php', 'python']), required=True,
              help='Primary programming language for the project')
@click.option('--framework', 
              type=click.Choice(['none', 'laravel', 'symfony', 'flask', 'django']),
              default='none',
              help='Web framework to use')
@click.option('--webserver', 
              type=click.Choice(['nginx', 'apache']),
              default='nginx',
              help='Web server for the project')
@click.option('--database', 
              type=click.Choice(['mysql', 'postgresql', 'mariadb']),
              default='mysql',
              help='Database system to use')
@click.option('--env', 
              type=click.Choice(['development', 'testing', 'production']),
              default='development',
              help='Environment type')
def create(project_name: str, language: str, framework: str, 
          webserver: str, database: str, env: str):
    """Create a new development environment."""
    try:
        base_path = Path.cwd()
        
        # Initialize environment
        environment = Environment(project_name, base_path)
        if not environment.setup():
            raise click.ClickException("Failed to initialize environment")

        # Setup configuration
        config_manager = ConfigurationManager(project_name, base_path)
        config_manager.initialize_config(
            language=language,
            framework=framework,
            webserver=webserver,
            database=database,
            environment=env
        )

        # Initialize Docker resources
        docker_manager = DockerManager(project_name, base_path)
        if not docker_manager.verify_docker_installation():
            raise click.ClickException("Docker is not available")
        
        docker_manager.create_network()
        docker_manager.create_volume()

        click.echo(f"\nProject {project_name} created successfully!")
        click.echo("\nNext steps:")
        click.echo(f"1. cd {project_name}")
        click.echo("2. docker-compose up -d")
        
    except Exception as e:
        raise click.ClickException(str(e))

@cli.command()
@click.argument('project_name')
def start(project_name: str):
    """Start an existing development environment."""
    try:
        base_path = Path.cwd()
        project_path = base_path / project_name
        
        if not project_path.exists():
            raise click.ClickException(f"Project {project_name} not found")
        
        # Load configuration
        config_manager = ConfigurationManager(project_name, base_path)
        config_manager.load_config()

        click.echo(f"Starting {project_name} environment...")
        # Add Docker Compose up implementation
        
    except Exception as e:
        raise click.ClickException(str(e))

@cli.command()
@click.argument('project_name')
def stop(project_name: str):
    """Stop a running development environment."""
    try:
        base_path = Path.cwd()
        project_path = base_path / project_name
        
        if not project_path.exists():
            raise click.ClickException(f"Project {project_name} not found")
        
        click.echo(f"Stopping {project_name} environment...")
        # Add Docker Compose down implementation
        
    except Exception as e:
        raise click.ClickException(str(e))

if __name__ == '__main__':
    cli()