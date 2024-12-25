"""
Command Line Interface Module
"""

import click
from pathlib import Path
from typing import Dict, Any

from chimera_stack.core.config import ConfigurationManager
from chimera_stack.core.environment import Environment
from chimera_stack.core.docker_manager import DockerManager
from chimera_stack.core.setup_wizard import SetupWizard

@click.group()
def cli():
    """ChimeraStack - Development Environment Management Tool"""
    pass

@cli.command()
def init():
    """Interactive guided setup for your development environment."""
    try:
        wizard = SetupWizard()
        config = wizard.run_setup()

        if config:
            create_project(**config)

    except Exception as e:
        raise click.ClickException(str(e))

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
    """Create a new development environment using specified options."""
    create_project(project_name, language, framework, webserver, database, env)

def create_project(project_name: str, language: str, framework: str,
                  webserver: str, database: str, env: str):
    """Common project creation logic used by both init and create commands."""
    try:
        project_path = Path.cwd() / project_name
        
        if project_path.exists():
            raise click.ClickException(f"Project directory '{project_name}' already exists")
        
        click.echo(f"\nCreating project: {project_name}")
        click.echo(f"Configuration:")
        click.echo(f"  Language:   {language}")
        click.echo(f"  Framework:  {framework}")
        click.echo(f"  Web Server: {webserver}")
        click.echo(f"  Database:   {database}")
        click.echo(f"  Environment:{env}")
        
        # Initialize environment
        environment = Environment(project_name, project_path)
        if not environment.setup():
            raise click.ClickException("Failed to create project directory structure")
            
        click.echo("\nInitializing project structure...")

        # Setup configuration
        config_manager = ConfigurationManager(project_name, project_path)
        if not config_manager.initialize_config(
            language=language,
            framework=framework,
            webserver=webserver,
            database=database,
            environment=env
        ):
            raise click.ClickException("Failed to initialize project configuration")
        
        click.echo("Project configuration created successfully")

        # Setup Docker resources
        docker_manager = DockerManager(project_name, project_path)
        if not docker_manager.verify_docker_installation():
            raise click.ClickException("Docker is not available")
        
        try:
            docker_manager.create_network()
            click.echo("Docker network created successfully")
        except Exception as e:
            click.echo(f"Warning: {str(e)}")
            click.echo("Using existing network...")
        
        try:
            docker_manager.create_volume()
            click.echo("Docker volume created successfully")
        except Exception as e:
            click.echo(f"Warning: {str(e)}")
            click.echo("Using existing volume...")

        click.echo(f"\n✨ Project {project_name} created successfully!")
        click.echo("\nNext steps:")
        click.echo(f"  1. cd {project_name}")
        click.echo(f"  2. docker-compose up -d")
        
    except Exception as e:
        if 'environment' in locals():
            environment.cleanup()
        raise click.ClickException(str(e))

@cli.command()
@click.argument('project_name')
def start(project_name: str):
    """Start an existing development environment."""
    try:
        project_path = Path.cwd() / project_name
        if not project_path.exists():
            raise click.ClickException(f"Project {project_name} not found")
        
        click.echo(f"Starting {project_name} environment...")
        # Implement Docker Compose up
        
    except Exception as e:
        raise click.ClickException(str(e))

@cli.command()
@click.argument('project_name')
def stop(project_name: str):
    """Stop a running development environment."""
    try:
        project_path = Path.cwd() / project_name
        if not project_path.exists():
            raise click.ClickException(f"Project {project_name} not found")
        
        click.echo(f"Stopping {project_name} environment...")
        # Implement Docker Compose down
        
    except Exception as e:
        raise click.ClickException(str(e))

if __name__ == '__main__':
    cli()