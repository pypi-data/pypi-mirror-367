"""
Build and deployment utilities for Maweng applications.

This module provides functionality for packaging and deploying
Maweng applications.
"""

import shutil
import zipfile
from pathlib import Path
from typing import Optional


def package_app(app: Optional[str], output: Optional[str]):
    """
    Package application for deployment.
    
    Args:
        app: App name (default: current directory)
        output: Output directory
    """
    # Determine app directory
    app_dir = get_app_directory(app)
    
    # Determine output directory
    if output:
        output_dir = Path(output)
    else:
        output_dir = app_dir / "dist"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create package
    package_name = app_dir.name
    package_file = output_dir / f"{package_name}.zip"
    
    with zipfile.ZipFile(package_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add application files
        for file_path in app_dir.rglob("*"):
            if file_path.is_file() and not should_exclude(file_path):
                arcname = file_path.relative_to(app_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Application packaged: {package_file}")


def deploy_app(app: Optional[str], env: str):
    """
    Deploy application.
    
    Args:
        app: App name (default: current directory)
        env: Environment
    """
    # Determine app directory
    app_dir = get_app_directory(app)
    
    print(f"🚀 Deploying application to {env} environment...")
    
    # This is a placeholder for deployment logic
    # In a real implementation, this would handle different deployment targets
    # such as cloud platforms, containers, etc.
    
    if env == "production":
        print("📦 Production deployment not implemented yet")
        print("   Please configure your deployment settings")
    elif env == "staging":
        print("📦 Staging deployment not implemented yet")
        print("   Please configure your deployment settings")
    else:
        print(f"📦 {env} deployment not implemented yet")
        print("   Please configure your deployment settings")


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


def should_exclude(file_path: Path) -> bool:
    """
    Check if a file should be excluded from packaging.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file should be excluded
    """
    # Exclude common files and directories
    exclude_patterns = [
        "__pycache__",
        ".pyc",
        ".pyo",
        ".pyd",
        ".git",
        ".gitignore",
        ".env",
        ".venv",
        "venv",
        "env",
        "node_modules",
        "dist",
        "build",
        "*.egg-info",
        ".pytest_cache",
        ".coverage",
        "htmlcov",
        ".DS_Store",
        "Thumbs.db"
    ]
    
    file_str = str(file_path)
    for pattern in exclude_patterns:
        if pattern in file_str:
            return True
    
    return False
