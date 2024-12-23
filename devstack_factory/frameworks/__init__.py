# src/frameworks/__init__.py
"""
Framework Implementations

Provides framework-specific implementations for PHP and Python projects.
"""

from .php import LaravelFramework, SymfonyFramework, VanillaPHPFramework
from .python import DjangoFramework, FlaskFramework, VanillaPythonFramework

__all__ = [
    'LaravelFramework',
    'SymfonyFramework',
    'VanillaPHPFramework',
    'DjangoFramework',
    'FlaskFramework',
    'VanillaPythonFramework'
]