"""
Python Framework Implementations

Provides framework-specific implementations for Python projects including Django,
Flask, and vanilla Python configurations.
"""

from .django import DjangoFramework
from .flask import FlaskFramework
from .vanilla import VanillaPythonFramework

__all__ = [
    'DjangoFramework',
    'FlaskFramework',
    'VanillaPythonFramework'
]