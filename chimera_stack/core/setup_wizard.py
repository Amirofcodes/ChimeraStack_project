"""
Setup Wizard Module

Provides an interactive, user-friendly interface for configuring development environments.
Guides users through each choice with clear explanations and confirmations.
"""

import click
from typing import Dict, Any, Optional

class SetupWizard:
    """Interactive setup wizard for development environment configuration."""
    
    def __init__(self):
        self.config = {}
        self.options = {
            'language': {
                'php': 'PHP - A popular general-purpose scripting language',
                'python': 'Python - A versatile programming language'
            },
            'framework': {
                'php': {
                    'none': 'Vanilla PHP - No framework, just pure PHP',
                    'laravel': 'Laravel - The PHP Framework for Web Artisans',
                    'symfony': 'Symfony - Professional PHP Framework'
                },
                'python': {
                    'none': 'Vanilla Python - No framework, just pure Python',
                    'django': 'Django - The Web framework for perfectionists',
                    'flask': 'Flask - Lightweight WSGI web application framework'
                }
            },
            'webserver': {
                'nginx': 'Nginx - High-performance HTTP server',
                'apache': 'Apache - The most widely used web server'
            },
            'database': {
                'mysql': 'MySQL - The most popular open-source database',
                'postgresql': 'PostgreSQL - The world\'s most advanced open source database',
                'mariadb': 'MariaDB - Community-developed fork of MySQL'
            },
            'environment': {
                'development': 'Development - Optimized for local development',
                'testing': 'Testing - Configured for testing and staging',
                'production': 'Production - Optimized for production deployment'
            }
        }

    def run_setup(self) -> Optional[Dict[str, str]]:
        """Run the interactive setup process.
        
        Returns:
            Dict containing all configuration options or None if setup was cancelled
        """
        try:
            # Get project name
            project_name = self._get_project_name()
            if not self._confirm_step("project name", project_name):
                return None
            
            # Get environment type
            environment = self._get_environment()
            if not self._confirm_step("environment", self.options['environment'][environment]):
                return None
            
            # Get programming language
            language = self._get_language()
            if not self._confirm_step("programming language", self.options['language'][language]):
                return None
            
            # Get framework
            framework = self._get_framework(language)
            framework_desc = self.options['framework'][language][framework]
            if not self._confirm_step("framework", framework_desc):
                return None
            
            # Get web server
            webserver = self._get_webserver()
            if not self._confirm_step("web server", self.options['webserver'][webserver]):
                return None
            
            # Get database
            database = self._get_database()
            if not self._confirm_step("database", self.options['database'][database]):
                return None
            
            # Show final summary
            self._show_summary({
                'Project Name': project_name,
                'Environment': environment,
                'Language': language,
                'Framework': framework,
                'Web Server': webserver,
                'Database': database
            })
            
            if not click.confirm('\nWould you like to create this project?'):
                click.echo("\nSetup cancelled. No changes were made.")
                return None
            
            return {
                'project_name': project_name,
                'environment': environment,
                'language': language,
                'framework': framework,
                'webserver': webserver,
                'database': database
            }
            
        except click.Abort:
            click.echo("\nSetup cancelled. No changes were made.")
            return None

    def _get_project_name(self) -> str:
        """Get project name from user with validation."""
        while True:
            name = click.prompt("\nEnter your project name", type=str)
            if name.isalnum() or (name.replace('_', '').replace('-', '').isalnum()):
                return name
            click.echo("Project name must contain only letters, numbers, underscores, or hyphens.")

    def _get_environment(self) -> str:
        """Get environment type from user."""
        click.echo("\nAvailable environments:")
        for env, desc in self.options['environment'].items():
            click.echo(f"  {env}: {desc}")
        
        return click.prompt(
            "\nWhich environment would you like to use?",
            type=click.Choice(self.options['environment'].keys()),
            default='development'
        )

    def _get_language(self) -> str:
        """Get programming language choice from user."""
        click.echo("\nAvailable programming languages:")
        for lang, desc in self.options['language'].items():
            click.echo(f"  {lang}: {desc}")
        
        return click.prompt(
            "\nWhich programming language would you like to use?",
            type=click.Choice(self.options['language'].keys())
        )

    def _get_framework(self, language: str) -> str:
        """Get framework choice from user based on selected language."""
        click.echo(f"\nAvailable frameworks for {language}:")
        for fw, desc in self.options['framework'][language].items():
            click.echo(f"  {fw}: {desc}")
        
        return click.prompt(
            "\nWhich framework would you like to use?",
            type=click.Choice(self.options['framework'][language].keys()),
            default='none'
        )

    def _get_webserver(self) -> str:
        """Get web server choice from user."""
        click.echo("\nAvailable web servers:")
        for ws, desc in self.options['webserver'].items():
            click.echo(f"  {ws}: {desc}")
        
        return click.prompt(
            "\nWhich web server would you like to use?",
            type=click.Choice(self.options['webserver'].keys()),
            default='nginx'
        )

    def _get_database(self) -> str:
        """Get database choice from user."""
        click.echo("\nAvailable databases:")
        for db, desc in self.options['database'].items():
            click.echo(f"  {db}: {desc}")
        
        return click.prompt(
            "\nWhich database would you like to use?",
            type=click.Choice(self.options['database'].keys()),
            default='mysql'
        )

    def _confirm_step(self, step_name: str, value: str) -> bool:
        """Confirm user's choice for a setup step."""
        click.echo(f"\nYou selected: {value}")
        if not click.confirm(f"Would you like to proceed with this {step_name}?"):
            click.echo(f"\nLet's choose a different {step_name}.")
            return False
        return True

    def _show_summary(self, config: Dict[str, str]) -> None:
        """Show summary of all selected options."""
        click.echo("\nConfiguration Summary:")
        click.echo("=====================")
        for key, value in config.items():
            # Get description for the value if available
            if key.lower() in self.options:
                desc = self.options[key.lower()].get(value, value)
            elif key == 'Framework':
                desc = self.options['framework'][config['Language']][value]
            else:
                desc = value
            click.echo(f"{key}: {desc}")
        click.echo("=====================")