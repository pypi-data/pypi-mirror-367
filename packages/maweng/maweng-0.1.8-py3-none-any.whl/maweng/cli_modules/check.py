"""
Project validation utilities for Maweng applications.

This module provides functionality to check projects for common issues
and validate configuration.
"""

from pathlib import Path
from typing import List, Optional


def check_project(app: Optional[str]) -> List[str]:
    """
    Check project for issues.
    
    Args:
        app: App name (default: current directory)
        
    Returns:
        List of issues found
    """
    issues = []
    
    # Determine app directory
    app_dir = get_app_directory(app)
    
    # Check project structure
    issues.extend(check_project_structure(app_dir))
    
    # Check configuration
    issues.extend(check_configuration(app_dir))
    
    # Check dependencies
    issues.extend(check_dependencies(app_dir))
    
    # Check for common issues
    issues.extend(check_common_issues(app_dir))
    
    return issues


def get_app_directory(app: Optional[str]) -> Path:
    """
    Get the app directory.
    
    Args:
        app: App name or None for current directory
        
    Returns:
        Path to the app directory
    """
    if app:
        return Path(app)
    else:
        # Look for app directory in current directory
        current_dir = Path.cwd()
        app_dir = current_dir / "app"
        if app_dir.exists():
            return app_dir
        else:
            return current_dir


def check_project_structure(app_dir: Path) -> List[str]:
    """
    Check project structure for issues.
    
    Args:
        app_dir: App directory
        
    Returns:
        List of issues found
    """
    issues = []
    
    # Check for main application file
    main_files = ["main.py", "app.py"]
    main_file_found = False
    
    for main_file in main_files:
        if (app_dir / main_file).exists():
            main_file_found = True
            break
    
    if not main_file_found:
        issues.append("No main application file found (main.py or app.py)")
    
    # Check for app directory structure
    app_subdir = app_dir / "app"
    if app_subdir.exists():
        # Check for views
        views_dir = app_subdir / "views"
        if not views_dir.exists():
            issues.append("No views directory found in app/")
        elif not (views_dir / "__init__.py").exists():
            issues.append("No __init__.py file in app/views/")
        
        # Check for models
        models_dir = app_subdir / "models"
        if not models_dir.exists():
            issues.append("No models directory found in app/")
        elif not (models_dir / "__init__.py").exists():
            issues.append("No __init__.py file in app/models/")
    
    # Check for tests
    tests_dir = app_dir / "tests"
    if not tests_dir.exists():
        issues.append("No tests directory found")
    elif not (tests_dir / "__init__.py").exists():
        issues.append("No __init__.py file in tests/")
    
    return issues


def check_configuration(app_dir: Path) -> List[str]:
    """
    Check configuration for issues.
    
    Args:
        app_dir: App directory
        
    Returns:
        List of issues found
    """
    issues = []
    
    # Check for config file
    config_file = app_dir / "config.py"
    if not config_file.exists():
        issues.append("No config.py file found")
    
    # Check for environment variables
    import os
    
    # Check for required environment variables
    required_env_vars = ["SECRET_KEY"]
    for var in required_env_vars:
        if not os.environ.get(var):
            issues.append(f"Required environment variable {var} not set")
    
    return issues


def check_dependencies(app_dir: Path) -> List[str]:
    """
    Check dependencies for issues.
    
    Args:
        app_dir: App directory
        
    Returns:
        List of issues found
    """
    issues = []
    
    # Check for requirements.txt
    requirements_file = app_dir / "requirements.txt"
    if not requirements_file.exists():
        issues.append("No requirements.txt file found")
    else:
        # Check if maweng is in requirements
        try:
            with open(requirements_file, 'r') as f:
                content = f.read()
                if 'maweng' not in content.lower():
                    issues.append("Maweng not found in requirements.txt")
        except Exception:
            issues.append("Could not read requirements.txt")
    
    # Check for pyproject.toml
    pyproject_file = app_dir / "pyproject.toml"
    if not pyproject_file.exists():
        issues.append("No pyproject.toml file found")
    
    return issues


def check_common_issues(app_dir: Path) -> List[str]:
    """
    Check for common issues.
    
    Args:
        app_dir: App directory
        
    Returns:
        List of issues found
    """
    issues = []
    
    # Check for .env file
    env_file = app_dir / ".env"
    if env_file.exists():
        # Check if .env is in .gitignore
        gitignore_file = app_dir / ".gitignore"
        if gitignore_file.exists():
            try:
                with open(gitignore_file, 'r') as f:
                    content = f.read()
                    if '.env' not in content:
                        issues.append(".env file found but not in .gitignore")
            except Exception:
                issues.append("Could not read .gitignore file")
        else:
            issues.append(".env file found but no .gitignore file")
    
    # Check for __pycache__ directories
    pycache_dirs = list(app_dir.rglob("__pycache__"))
    if pycache_dirs:
        issues.append(f"Found {len(pycache_dirs)} __pycache__ directories (should be in .gitignore)")
    
    # Check for .pyc files
    pyc_files = list(app_dir.rglob("*.pyc"))
    if pyc_files:
        issues.append(f"Found {len(pyc_files)} .pyc files (should be in .gitignore)")
    
    return issues
