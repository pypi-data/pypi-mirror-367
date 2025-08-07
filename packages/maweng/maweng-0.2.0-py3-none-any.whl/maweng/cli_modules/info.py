"""
Project information utilities for Maweng applications.

This module provides functionality to display project information
and configuration details.
"""

import os
import platform
import sys
from pathlib import Path
from typing import Optional


def show_info(app: Optional[str]):
    """
    Show project information.
    
    Args:
        app: App name (default: current directory)
    """
    # Determine app directory
    app_dir = get_app_directory(app)
    
    print("📊 Project Information")
    print("=" * 50)
    
    # Project details
    print(f"📁 Project Directory: {app_dir.absolute()}")
    print(f"🐍 Python Version: {sys.version}")
    print(f"💻 Platform: {platform.platform()}")
    print(f"🏗️  Maweng Version: {get_maweng_version()}")
    
    # Project structure
    print("\n📂 Project Structure:")
    show_project_structure(app_dir)
    
    # Configuration
    print("\n⚙️  Configuration:")
    show_configuration(app_dir)
    
    # Dependencies
    print("\n📦 Dependencies:")
    show_dependencies(app_dir)


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


def get_maweng_version() -> str:
    """
    Get Maweng version.
    
    Returns:
        Maweng version string
    """
    try:
        import maweng
        return getattr(maweng, '__version__', 'unknown')
    except ImportError:
        return 'not installed'


def show_project_structure(app_dir: Path):
    """
    Show project structure.
    
    Args:
        app_dir: App directory
    """
    # Common directories to check
    directories = [
        "app",
        "tests",
        "static",
        "templates",
        "migrations",
        "models",
        "views",
        "config"
    ]
    
    for directory in directories:
        dir_path = app_dir / directory
        if dir_path.exists():
            print(f"  ✅ {directory}/")
        else:
            print(f"  ❌ {directory}/ (not found)")
    
    # Check for main files
    main_files = ["main.py", "app.py", "config.py", "requirements.txt"]
    for file in main_files:
        file_path = app_dir / file
        if file_path.exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (not found)")


def show_configuration(app_dir: Path):
    """
    Show configuration details.
    
    Args:
        app_dir: App directory
    """
    # Environment variables
    env_vars = [
        "MAWENG_ENV",
        "MAWENG_DEBUG",
        "DATABASE_URL",
        "SECRET_KEY"
    ]
    
    for var in env_vars:
        value = os.environ.get(var, "not set")
        print(f"  {var}: {value}")
    
    # Configuration file
    config_file = app_dir / "config.py"
    if config_file.exists():
        print(f"  📄 Config file: {config_file}")
    else:
        print("  📄 Config file: not found")


def show_dependencies(app_dir: Path):
    """
    Show project dependencies.
    
    Args:
        app_dir: App directory
    """
    # Check requirements.txt
    requirements_file = app_dir / "requirements.txt"
    if requirements_file.exists():
        print(f"  📄 Requirements: {requirements_file}")
        try:
            with open(requirements_file, 'r') as f:
                requirements = f.read().strip().split('\n')
                for req in requirements:
                    if req.strip() and not req.startswith('#'):
                        print(f"    - {req.strip()}")
        except Exception as e:
            print(f"    Error reading requirements: {e}")
    else:
        print("  📄 Requirements: not found")
    
    # Check pyproject.toml
    pyproject_file = app_dir / "pyproject.toml"
    if pyproject_file.exists():
        print(f"  📄 PyProject: {pyproject_file}")
    else:
        print("  📄 PyProject: not found")
