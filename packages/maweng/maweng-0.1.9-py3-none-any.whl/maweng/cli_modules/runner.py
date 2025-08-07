"""
Development server runner for Maweng applications.

This module provides functionality to run Maweng applications in development mode
with auto-reload and debugging capabilities.
"""

import os
import sys
from pathlib import Path
from typing import Optional

import uvicorn
from click import echo


def run_server(host: str = "127.0.0.1", port: int = 8000, 
               reload: bool = True, debug: bool = True):
    """
    Run the development server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload
        debug: Enable debug mode
    """
    # Find the main application file
    main_file = find_main_file()
    if not main_file:
        echo("❌ Could not find main.py or app.py file", err=True)
        sys.exit(1)
    
    # Set environment variables
    os.environ.setdefault("MAWENG_ENV", "development")
    if debug:
        os.environ.setdefault("MAWENG_DEBUG", "true")
    
    echo(f"🚀 Starting development server at http://{host}:{port}")
    echo(f"📁 Application: {main_file}")
    echo(f"🔄 Auto-reload: {'enabled' if reload else 'disabled'}")
    echo(f"🐛 Debug mode: {'enabled' if debug else 'disabled'}")
    echo("Press Ctrl+C to stop the server")
    echo()
    
    # Run the server
    uvicorn.run(
        f"{main_file.stem}:app",
        host=host,
        port=port,
        reload=reload,
        log_level="debug" if debug else "info",
        access_log=True
    )


def find_main_file() -> Optional[Path]:
    """
    Find the main application file (main.py or app.py).
    
    Returns:
        Path to the main file or None if not found
    """
    current_dir = Path.cwd()
    
    # Look for main.py or app.py in current directory
    for filename in ["main.py", "app.py"]:
        file_path = current_dir / filename
        if file_path.exists():
            return file_path
    
    # Look in subdirectories
    for subdir in ["app", "src", "."]:
        subdir_path = current_dir / subdir
        if subdir_path.exists() and subdir_path.is_dir():
            for filename in ["main.py", "app.py"]:
                file_path = subdir_path / filename
                if file_path.exists():
                    return file_path
    
    return None


def create_app_from_file(file_path: Path):
    """
    Create an application instance from a file.
    
    Args:
        file_path: Path to the application file
        
    Returns:
        Application instance
    """
    import importlib.util
    
    # Load the module
    spec = importlib.util.spec_from_file_location("app", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Look for app instance or create_app function
    if hasattr(module, 'app'):
        return module.app
    elif hasattr(module, 'create_app'):
        return module.create_app()
    else:
        raise ValueError(f"No app instance or create_app function found in {file_path}")
