"""
Command-line interface for the Maweng framework.

This module provides CLI tools for project management, development,
and deployment of Maweng applications.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from click import Context, Group


@click.group()
@click.version_option(version="0.1.0", prog_name="maweng")
def cli():
    """
    Maweng Framework CLI
    
    A lightweight, modern Python web framework with ORM and auto-generated API docs.
    """
    pass


@cli.group()
def new():
    """Create new projects and components."""
    pass


@new.command()
@click.argument("project_name")
@click.option("--template", "-t", default="basic", help="Project template to use")
@click.option("--directory", "-d", help="Directory to create project in")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing directory")
def project(project_name: str, template: str, directory: Optional[str], force: bool):
    """Create a new Maweng project."""
    from .cli.templates import create_project
    
    try:
        create_project(project_name, template, directory, force)
        click.echo(f"✅ Created new Maweng project: {project_name}")
        click.echo(f"📁 Project directory: {Path(directory or project_name).absolute()}")
        click.echo("\n🚀 Next steps:")
        click.echo(f"  cd {project_name}")
        click.echo("  maweng run")
    except Exception as e:
        click.echo(f"❌ Error creating project: {e}", err=True)
        sys.exit(1)


@new.command()
@click.argument("model_name")
@click.option("--app", "-a", help="App name (default: current directory)")
@click.option("--fields", "-f", help="Model fields (format: name:type,name:type)")
def model(model_name: str, app: Optional[str], fields: Optional[str]):
    """Create a new model."""
    from .cli.generators import create_model
    
    try:
        create_model(model_name, app, fields)
        click.echo(f"✅ Created new model: {model_name}")
    except Exception as e:
        click.echo(f"❌ Error creating model: {e}", err=True)
        sys.exit(1)


@new.command()
@click.argument("view_name")
@click.option("--app", "-a", help="App name (default: current directory)")
@click.option("--methods", "-m", help="HTTP methods (default: get,post,put,delete)")
def view(view_name: str, app: Optional[str], methods: Optional[str]):
    """Create a new view."""
    from .cli.generators import create_view
    
    try:
        create_view(view_name, app, methods)
        click.echo(f"✅ Created new view: {view_name}")
    except Exception as e:
        click.echo(f"❌ Error creating view: {e}", err=True)
        sys.exit(1)


@cli.group()
def run():
    """Run development server and other commands."""
    pass


@run.command()
@click.option("--host", "-h", default="127.0.0.1", help="Host to bind to")
@click.option("--port", "-p", default=8000, help="Port to bind to")
@click.option("--reload", "-r", is_flag=True, help="Enable auto-reload")
@click.option("--debug", "-d", is_flag=True, help="Enable debug mode")
def server(host: str, port: int, reload: bool, debug: bool):
    """Run the development server."""
    from .cli.runner import run_server
    
    try:
        run_server(host, port, reload, debug)
    except KeyboardInterrupt:
        click.echo("\n👋 Server stopped")
    except Exception as e:
        click.echo(f"❌ Error starting server: {e}", err=True)
        sys.exit(1)


@cli.group()
def db():
    """Database management commands."""
    pass


@db.command()
@click.option("--app", "-a", help="App name (default: current directory)")
def init(app: Optional[str]):
    """Initialize database."""
    from .cli.database import init_database
    
    try:
        init_database(app)
        click.echo("✅ Database initialized")
    except Exception as e:
        click.echo(f"❌ Error initializing database: {e}", err=True)
        sys.exit(1)


@db.command()
@click.option("--app", "-a", help="App name (default: current directory)")
@click.option("--message", "-m", help="Migration message")
def migrate(app: Optional[str], message: Optional[str]):
    """Create and apply database migrations."""
    from .cli.database import create_migration, apply_migrations
    
    try:
        if message:
            create_migration(app, message)
            click.echo("✅ Migration created")
        else:
            apply_migrations(app)
            click.echo("✅ Migrations applied")
    except Exception as e:
        click.echo(f"❌ Error with migrations: {e}", err=True)
        sys.exit(1)


@db.command()
@click.option("--app", "-a", help="App name (default: current directory)")
def seed(app: Optional[str]):
    """Seed database with sample data."""
    from .cli.database import seed_database
    
    try:
        seed_database(app)
        click.echo("✅ Database seeded")
    except Exception as e:
        click.echo(f"❌ Error seeding database: {e}", err=True)
        sys.exit(1)


@cli.group()
def test():
    """Testing commands."""
    pass


@test.command()
@click.option("--app", "-a", help="App name (default: current directory)")
@click.option("--coverage", "-c", is_flag=True, help="Run with coverage")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def run_tests(app: Optional[str], coverage: bool, verbose: bool):
    """Run tests."""
    from .cli.testing import run_tests
    
    try:
        run_tests(app, coverage, verbose)
    except Exception as e:
        click.echo(f"❌ Error running tests: {e}", err=True)
        sys.exit(1)


@cli.group()
def build():
    """Build and deployment commands."""
    pass


@build.command()
@click.option("--app", "-a", help="App name (default: current directory)")
@click.option("--output", "-o", help="Output directory")
def package(app: Optional[str], output: Optional[str]):
    """Package application for deployment."""
    from .cli.build import package_app
    
    try:
        package_app(app, output)
        click.echo("✅ Application packaged")
    except Exception as e:
        click.echo(f"❌ Error packaging application: {e}", err=True)
        sys.exit(1)


@build.command()
@click.option("--app", "-a", help="App name (default: current directory)")
@click.option("--env", "-e", default="production", help="Environment")
def deploy(app: Optional[str], env: str):
    """Deploy application."""
    from .cli.build import deploy_app
    
    try:
        deploy_app(app, env)
        click.echo("✅ Application deployed")
    except Exception as e:
        click.echo(f"❌ Error deploying application: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--app", "-a", help="App name (default: current directory)")
def info(app: Optional[str]):
    """Show project information."""
    from .cli.info import show_info
    
    try:
        show_info(app)
    except Exception as e:
        click.echo(f"❌ Error showing info: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--app", "-a", help="App name (default: current directory)")
def check(app: Optional[str]):
    """Check project for issues."""
    from .cli.check import check_project
    
    try:
        issues = check_project(app)
        if issues:
            click.echo("⚠️  Found issues:")
            for issue in issues:
                click.echo(f"  - {issue}")
        else:
            click.echo("✅ No issues found")
    except Exception as e:
        click.echo(f"❌ Error checking project: {e}", err=True)
        sys.exit(1)


# CLI submodules
class CLIModules:
    """CLI module implementations."""
    
    @staticmethod
    def templates():
        """Template management."""
        pass
    
    @staticmethod
    def generators():
        """Code generators."""
        pass
    
    @staticmethod
    def runner():
        """Development server runner."""
        pass
    
    @staticmethod
    def database():
        """Database management."""
        pass
    
    @staticmethod
    def testing():
        """Testing utilities."""
        pass
    
    @staticmethod
    def build():
        """Build and deployment."""
        pass
    
    @staticmethod
    def info():
        """Project information."""
        pass
    
    @staticmethod
    def check():
        """Project validation."""
        pass


# Template creation
def create_project(project_name: str, template: str, directory: Optional[str], force: bool):
    """Create a new project from template."""
    import shutil
    from pathlib import Path
    
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
    template_dir = Path(__file__).parent / "templates" / template
    if template_dir.exists():
        shutil.copytree(template_dir, project_dir, dirs_exist_ok=True)
    else:
        # Create basic project structure
        create_basic_project_structure(project_dir, project_name)
    
    # Update project files
    update_project_files(project_dir, project_name)


def create_basic_project_structure(project_dir: Path, project_name: str):
    """Create basic project structure."""
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
    """Update project files with project name."""
    # Update main.py
    main_file = project_dir / "main.py"
    if main_file.exists():
        content = main_file.read_text()
        content = content.replace("project_name", project_name)
        main_file.write_text(content)


# Main CLI entry point
def main():
    """Main CLI entry point."""
    cli()


if __name__ == "__main__":
    main() 