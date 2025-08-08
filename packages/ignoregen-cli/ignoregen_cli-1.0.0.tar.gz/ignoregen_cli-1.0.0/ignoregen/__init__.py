"""
IgnoreGen - Smart .gitignore Generator
A CLI tool and Python package for generating .gitignore files.
"""

__version__ = "1.0.0"
__author__ = "Victor Abimbola"
__email__ = "abimbolaolawale41@gmail.com"

from .core import IgnoreGen, generate_gitignore
from .detector import ProjectDetector

__all__ = ["IgnoreGen", "generate_gitignore", "ProjectDetector"]