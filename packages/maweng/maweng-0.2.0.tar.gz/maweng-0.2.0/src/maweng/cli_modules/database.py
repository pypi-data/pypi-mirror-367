"""
Database management for Maweng applications.

This module provides functionality for database initialization,
migrations, and seeding.
"""

from pathlib import Path
from typing import Optional


def init_database(app: Optional[str]):
    """
    Initialize database.
    
    Args:
        app: App name (default: current directory)
    """
    # Determine app directory
    app_dir = get_app_directory(app)
    
    # Create migrations directory if it doesn't exist
    migrations_dir = app_dir / "migrations"
    migrations_dir.mkdir(exist_ok=True)
    
    # Create __init__.py if it doesn't exist
    init_file = migrations_dir / "__init__.py"
    if not init_file.exists():
        init_file.touch()
    
    # Create initial migration
    create_initial_migration(migrations_dir)


def create_migration(app: Optional[str], message: str):
    """
    Create a new migration.
    
    Args:
        app: App name (default: current directory)
        message: Migration message
    """
    # Determine app directory
    app_dir = get_app_directory(app)
    
    # Create migrations directory if it doesn't exist
    migrations_dir = app_dir / "migrations"
    migrations_dir.mkdir(exist_ok=True)
    
    # Generate migration filename
    migration_name = message.lower().replace(" ", "_").replace("-", "_")
    migration_file = migrations_dir / f"{migration_name}.py"
    
    # Create migration content
    migration_content = generate_migration_content(message)
    
    # Write migration file
    with open(migration_file, "w") as f:
        f.write(migration_content)


def apply_migrations(app: Optional[str]):
    """
    Apply database migrations.
    
    Args:
        app: App name (default: current directory)
    """
    # Determine app directory
    app_dir = get_app_directory(app)
    
    # Find migrations directory
    migrations_dir = app_dir / "migrations"
    if not migrations_dir.exists():
        raise FileNotFoundError(f"Migrations directory not found: {migrations_dir}")
    
    # Find all migration files
    migration_files = sorted(migrations_dir.glob("*.py"))
    migration_files = [f for f in migration_files if f.name != "__init__.py"]
    
    if not migration_files:
        print("No migrations to apply")
        return
    
    # Apply each migration
    for migration_file in migration_files:
        print(f"Applying migration: {migration_file.name}")
        apply_migration(migration_file)


def seed_database(app: Optional[str]):
    """
    Seed database with sample data.
    
    Args:
        app: App name (default: current directory)
    """
    # Determine app directory
    app_dir = get_app_directory(app)
    
    # Look for seed file
    seed_file = app_dir / "seed.py"
    if not seed_file.exists():
        # Create basic seed file
        create_basic_seed_file(seed_file)
    
    # Run seed file
    import subprocess
    import sys
    
    try:
        subprocess.run([sys.executable, str(seed_file)], check=True)
        print("Database seeded successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error seeding database: {e}")


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


def create_initial_migration(migrations_dir: Path):
    """
    Create initial migration.
    
    Args:
        migrations_dir: Migrations directory
    """
    migration_content = '''"""
Initial migration.

This migration creates the initial database schema.
"""

from maweng.orm.database import Database

def up(db: Database):
    """Apply migration."""
    # Create tables
    db.create_all()

def down(db: Database):
    """Rollback migration."""
    # Drop all tables
    db.drop_all()
'''
    
    migration_file = migrations_dir / "001_initial.py"
    with open(migration_file, "w") as f:
        f.write(migration_content)


def generate_migration_content(message: str) -> str:
    """
    Generate migration content.
    
    Args:
        message: Migration message
        
    Returns:
        Generated migration content
    """
    content = f'''"""
{message}

This migration {message.lower()}.
"""

from maweng.orm.database import Database

def up(db: Database):
    """Apply migration."""
    # TODO: Add migration logic here
    pass

def down(db: Database):
    """Rollback migration."""
    # TODO: Add rollback logic here
    pass
'''
    
    return content


def apply_migration(migration_file: Path):
    """
    Apply a single migration.
    
    Args:
        migration_file: Path to migration file
    """
    import importlib.util
    
    # Load the migration module
    spec = importlib.util.spec_from_file_location("migration", migration_file)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    
    # Get database instance
    from maweng.orm.database import Database
    db = Database()
    
    # Apply migration
    if hasattr(migration, 'up'):
        migration.up(db)
    else:
        print(f"Warning: No 'up' function found in {migration_file.name}")


def create_basic_seed_file(seed_file: Path):
    """
    Create a basic seed file.
    
    Args:
        seed_file: Path to seed file
    """
    seed_content = '''"""
Database seeder.

This file contains sample data for the application.
"""

from maweng.orm.database import Database

def seed():
    """Seed the database with sample data."""
    db = Database()
    
    # TODO: Add sample data here
    print("Seeding database...")
    
    # Example:
    # from app.models.user import User
    # user = User(name="John Doe", email="john@example.com")
    # db.add(user)
    # db.commit()

if __name__ == "__main__":
    seed()
'''
    
    with open(seed_file, "w") as f:
        f.write(seed_content)
