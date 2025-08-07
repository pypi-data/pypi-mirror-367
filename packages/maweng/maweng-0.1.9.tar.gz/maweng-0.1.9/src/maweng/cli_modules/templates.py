"""
Project templates for Maweng applications.

This module provides functionality to create new projects from templates
and manage project structure.
"""

import shutil
from pathlib import Path
from typing import Optional


def create_project(project_name: str, template: str, directory: Optional[str], force: bool):
    """
    Create a new project from template.
    
    Args:
        project_name: Name of the project
        template: Template to use
        directory: Directory to create project in
        force: Overwrite existing directory
    """
    # Determine project directory
    if directory:
        project_dir = Path(directory)
    else:
        project_dir = Path(project_name)
    
    # Check if directory exists
    if project_dir.exists() and not force:
        raise FileExistsError(f"Directory {project_dir} already exists. Use --force to overwrite.")
    
    # Create project structure
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy template files
    template_dir = Path(__file__).parent.parent / "templates" / template
    if template_dir.exists():
        shutil.copytree(template_dir, project_dir, dirs_exist_ok=True)
    else:
        # Create basic project structure
        create_basic_project_structure(project_dir, project_name)
    
    # Update project files
    update_project_files(project_dir, project_name)


def create_basic_project_structure(project_dir: Path, project_name: str):
    """
    Create basic project structure.
    
    Args:
        project_dir: Project directory
        project_name: Name of the project
    """
    # Create directories
    (project_dir / "app").mkdir(exist_ok=True)
    (project_dir / "tests").mkdir(exist_ok=True)
    (project_dir / "static").mkdir(exist_ok=True)
    (project_dir / "templates").mkdir(exist_ok=True)
    (project_dir / "migrations").mkdir(exist_ok=True)
    
    # Create __init__.py files
    (project_dir / "app" / "__init__.py").touch()
    (project_dir / "tests" / "__init__.py").touch()
    
    # Create main.py
    main_content = f'''"""
Main application entry point for {project_name}.
"""

from maweng import App
from app.views import register_views

def create_app():
    """Create and configure the application."""
    app = App("{project_name}")
    
    # Register views
    register_views(app)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
'''
    
    with open(project_dir / "main.py", "w") as f:
        f.write(main_content)
    
    # Create config.py
    config_content = '''"""
Configuration for the application.
"""

from maweng.config import DevelopmentConfig

class Config(DevelopmentConfig):
    """Application configuration."""
    pass
'''
    
    with open(project_dir / "config.py", "w") as f:
        f.write(config_content)
    
    # Create requirements.txt
    requirements_content = '''maweng>=0.1.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
'''
    
    with open(project_dir / "requirements.txt", "w") as f:
        f.write(requirements_content)
    
    # Create README.md
    readme_content = f'''# {project_name}

A Maweng web application.

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   maweng run
   ```

3. Visit http://localhost:8000

## Development

- Run tests: `maweng test`
- Create migrations: `maweng db migrate -m "description"`
- Apply migrations: `maweng db migrate`
'''
    
    with open(project_dir / "README.md", "w") as f:
        f.write(readme_content)


def update_project_files(project_dir: Path, project_name: str):
    """
    Update project files with project name.
    
    Args:
        project_dir: Project directory
        project_name: Name of the project
    """
    # Update main.py
    main_file = project_dir / "main.py"
    if main_file.exists():
        content = main_file.read_text()
        content = content.replace("project_name", project_name)
        main_file.write_text(content)
