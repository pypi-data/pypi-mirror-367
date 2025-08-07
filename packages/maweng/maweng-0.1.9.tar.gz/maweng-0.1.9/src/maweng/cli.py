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
    from maweng.cli_modules.templates import create_project
    
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
    from maweng.cli_modules.generators import create_model
    
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
    from maweng.cli_modules.generators import create_view
    
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
    from maweng.cli_modules.runner import run_server
    
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
    from maweng.cli_modules.database import init_database
    
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
    from maweng.cli_modules.database import create_migration, apply_migrations
    
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
    from maweng.cli_modules.database import seed_database
    
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
    from maweng.cli_modules.testing import run_tests
    
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
    from maweng.cli_modules.build import package_app
    
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
    from maweng.cli_modules.build import deploy_app
    
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
    from maweng.cli_modules.info import show_info
    
    try:
        show_info(app)
    except Exception as e:
        click.echo(f"❌ Error showing info: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--app", "-a", help="App name (default: current directory)")
def check(app: Optional[str]):
    """Check project for issues."""
    from maweng.cli_modules.check import check_project
    
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


# CLI functionality is organized in separate modules under cli_modules/


# Main CLI entry point
def main():
    """Main CLI entry point."""
    cli()


if __name__ == "__main__":
    main() 