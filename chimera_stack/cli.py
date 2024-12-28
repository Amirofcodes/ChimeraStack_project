"""
Command Line Interface Module

Provides the main CLI functionality for ChimeraStack, including project creation,
management, and tool information.
"""

import click
from pathlib import Path
from typing import Dict, Any

from chimera_stack.core.config import ConfigurationManager
from chimera_stack.core.environment import Environment
from chimera_stack.core.docker_manager import DockerManager
from chimera_stack.core.setup_wizard import SetupWizard

# Tool information
AUTHOR = "Jaouad Bouddehbine (Amirofcodes)"
REPOSITORY = "https://github.com/Amirofcodes/chimera-stack"
VERSION = "0.1.0"

def print_version(ctx, param, value):
    """Print version information callback."""
    if not value or ctx.resilient_parsing:
        return
    click.echo(f"ChimeraStack v{VERSION}")
    click.echo(f"Author: {AUTHOR}")
    click.echo(f"Repository: {REPOSITORY}")
    ctx.exit()

@click.group(help="ChimeraStack - A Docker-centric Development Environment Management Tool\n\n"
                  "Created by Jaouad Bouddehbine (Amirofcodes)\n"
                  "Repository: https://github.com/Amirofcodes/chimera-stack")
@click.option('--version', is_flag=True, callback=print_version, expose_value=False,
              is_eager=True, help="Show the version and exit.")
def cli():
    """ChimeraStack CLI entry point."""
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
    create_project(project_name=project_name, language=language,
                  framework=framework, webserver=webserver,
                  database=database, env=env)

@cli.command()
@click.argument('project_name')
def start(project_name: str):
    """Start an existing development environment."""
    try:
        project_path = Path.cwd() / project_name
        if not project_path.exists():
            raise click.ClickException(f"Project {project_name} not found")

        click.echo(f"Starting {project_name} environment...")
        docker_manager = DockerManager(project_name, project_path)
        if docker_manager.start_environment():
            click.echo(f"✨ Environment {project_name} started successfully!")
        else:
            raise click.ClickException("Failed to start environment")

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
        docker_manager = DockerManager(project_name, project_path)
        if docker_manager.stop_environment():
            click.echo(f"✨ Environment {project_name} stopped successfully!")
        else:
            raise click.ClickException("Failed to stop environment")

    except Exception as e:
        raise click.ClickException(str(e))

@cli.command()
def info():
    """Display information about ChimeraStack."""
    click.echo("\nChimeraStack - Docker Development Environment Tool")
    click.echo("=" * 50)
    click.echo(f"Version: {VERSION}")
    click.echo(f"Author: {AUTHOR}")
    click.echo(f"Repository: {REPOSITORY}")
    click.echo("\nSupported Languages:")
    click.echo("  - PHP (Laravel, Symfony, Vanilla)")
    click.echo("  - Python (Django, Flask, Vanilla)")
    click.echo("\nSupported Services:")
    click.echo("  - Web Servers: Nginx, Apache")
    click.echo("  - Databases: MySQL, PostgreSQL, MariaDB")
    click.echo("  - Additional: Redis, Logging, Monitoring")
    click.echo("\nFor more information, visit the repository.")

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

        # Create Docker volume for persistent data
        try:
            docker_manager.create_volume()
            click.echo("Docker volume created successfully")
        except Exception as e:
            click.echo(f"Warning: {str(e)}")
            click.echo("Using existing volume...")

        # Clean up empty directories
        empty_dirs = [
            project_path / 'docker' / 'database',
            project_path / 'docker' / 'webserver'
        ]
        for dir_path in empty_dirs:
            if dir_path.exists() and not any(dir_path.iterdir()):
                try:
                    dir_path.rmdir()
                except Exception as e:
                    print(f"Warning: Could not remove empty directory {dir_path}: {e}")

        click.echo(f"\n✨ Project {project_name} created successfully!")
        
        # Generate dynamic project guide based on configuration
        click.echo("\nProject Structure Overview:")
        click.echo("------------------------")
        click.echo("Root Directory:")
        click.echo("  • .env - Environment variables and sensitive configuration")
        click.echo("  • docker-compose.yml - Docker services orchestration")
        
        click.echo("\nApplication:")
        click.echo("  • public/ - Web root directory (index.php)")
        click.echo("  • src/ - Application source code and business logic")
        
        if language == 'php':
            if framework == 'none':
                click.echo("    ◦ bootstrap.php - Autoloading and initialization")
                click.echo("    ◦ pages/ - Application pages and endpoints")

        click.echo("\nDocker Configuration:")
        if webserver == 'nginx':
            click.echo("  • docker/nginx/ - Nginx web server configuration")
            click.echo("    ◦ conf.d/default.conf - Server blocks and PHP processing")
        elif webserver == 'apache':
            click.echo("  • docker/apache/ - Apache web server configuration")
            click.echo("    ◦ conf.d/default.conf - VirtualHost and mod_php settings")

        if database == 'mysql':
            click.echo("  • docker/mysql/ - MySQL database configuration")
            click.echo("    ◦ my.cnf - Database server optimization settings")
        elif database == 'postgresql':
            click.echo("  • docker/postgresql/ - PostgreSQL database configuration")
            click.echo("    ◦ postgresql.conf - Database server settings")
        elif database == 'mariadb':
            click.echo("  • docker/mariadb/ - MariaDB database configuration")
            click.echo("    ◦ my.cnf - Database server optimization settings")

        if language == 'php':
            click.echo("  • docker/php/ - PHP runtime configuration")
            click.echo("    ◦ Dockerfile - PHP extensions and dependencies")
            click.echo("    ◦ php.ini - PHP runtime settings")
            click.echo("    ◦ www.conf - PHP-FPM process management")

        click.echo("\nNext Steps:")
        click.echo(f"  1. cd {project_name}")
        click.echo("  2. docker-compose up -d")
        click.echo("\nUseful Commands:")
        click.echo("  • docker-compose ps - List running services")
        click.echo("  • docker-compose logs - View service logs")
        if database == 'mysql':
            click.echo("  • docker-compose exec mysql mysql -u root -p - Access MySQL CLI")
        elif database == 'postgresql':
            click.echo("  • docker-compose exec postgresql psql -U postgres - Access PostgreSQL CLI")
        elif database == 'mariadb':
            click.echo("  • docker-compose exec mariadb mysql -u root -p - Access MariaDB CLI")

    except Exception as e:
        if 'environment' in locals():
            environment.cleanup()
        raise click.ClickException(str(e))


if __name__ == '__main__':
    cli()