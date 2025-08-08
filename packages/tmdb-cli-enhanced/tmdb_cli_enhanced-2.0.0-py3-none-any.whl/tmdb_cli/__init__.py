"""
TMDB CLI - A beautiful command-line interface for The Movie Database API

This package provides an interactive CLI tool for searching movies, managing watchlists,
and getting personalized recommendations from The Movie Database (TMDB) API.
"""

__version__ = "2.0.0"
__author__ = "Hamza Danjaji"
__email__ = "bhantsi@gmail.com"

from .main import cli

__all__ = ["cli"]
