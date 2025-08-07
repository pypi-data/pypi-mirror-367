"""
CLI package for Maweng framework.

This package contains all CLI-related functionality including:
- Project templates and generators
- Development server runner
- Database management
- Testing utilities
- Build and deployment tools
"""

# Import main functions from modules
from .templates import create_project
from .generators import create_model, create_view
from .runner import run_server
from .database import init_database, create_migration, apply_migrations, seed_database
from .testing import run_tests
from .build import package_app, deploy_app
from .info import show_info
from .check import check_project

__all__ = [
    # Templates
    'create_project',
    # Generators
    'create_model',
    'create_view',
    # Runner
    'run_server',
    # Database
    'init_database',
    'create_migration',
    'apply_migrations',
    'seed_database',
    # Testing
    'run_tests',
    # Build
    'package_app',
    'deploy_app',
    # Info
    'show_info',
    # Check
    'check_project'
]
