"""IAM JSON Lint - A tool for linting and validating IAM policies."""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .linter import IAMLinter
from .validator import IAMValidator

__all__ = ["IAMLinter", "IAMValidator"]
