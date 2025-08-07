"""
Testing utilities for Maweng applications.

This module provides functionality for running tests and generating
test coverage reports.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional


def run_tests(app: Optional[str], coverage: bool, verbose: bool):
    """
    Run tests.
    
    Args:
        app: App name (default: current directory)
        coverage: Run with coverage
        verbose: Verbose output
    """
    # Determine app directory
    app_dir = get_app_directory(app)
    
    # Find tests directory
    tests_dir = app_dir / "tests"
    if not tests_dir.exists():
        print(f"Tests directory not found: {tests_dir}")
        return
    
    # Build pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    
    # Add tests directory
    cmd.append(str(tests_dir))
    
    # Run tests
    try:
        subprocess.run(cmd, check=True)
        print("✅ Tests completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with exit code {e.returncode}")
        sys.exit(e.returncode)


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
