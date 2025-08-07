"""
Code generators for Maweng applications.

This module provides functionality to generate models, views, and other
application components.
"""

from pathlib import Path
from typing import Optional


def create_model(model_name: str, app: Optional[str], fields: Optional[str]):
    """
    Create a new model.
    
    Args:
        model_name: Name of the model
        app: App name (default: current directory)
        fields: Model fields (format: name:type,name:type)
    """
    # Determine app directory
    app_dir = get_app_directory(app)
    
    # Create models directory if it doesn't exist
    models_dir = app_dir / "models"
    models_dir.mkdir(exist_ok=True)
    
    # Create __init__.py if it doesn't exist
    init_file = models_dir / "__init__.py"
    if not init_file.exists():
        init_file.touch()
    
    # Generate model content
    model_content = generate_model_content(model_name, fields)
    
    # Write model file
    model_file = models_dir / f"{model_name.lower()}.py"
    with open(model_file, "w") as f:
        f.write(model_content)
    
    # Update __init__.py to import the model
    update_models_init(models_dir, model_name)


def create_view(view_name: str, app: Optional[str], methods: Optional[str]):
    """
    Create a new view.
    
    Args:
        view_name: Name of the view
        app: App name (default: current directory)
        methods: HTTP methods (default: get,post,put,delete)
    """
    # Determine app directory
    app_dir = get_app_directory(app)
    
    # Create views directory if it doesn't exist
    views_dir = app_dir / "views"
    views_dir.mkdir(exist_ok=True)
    
    # Create __init__.py if it doesn't exist
    init_file = views_dir / "__init__.py"
    if not init_file.exists():
        init_file.touch()
    
    # Generate view content
    view_content = generate_view_content(view_name, methods)
    
    # Write view file
    view_file = views_dir / f"{view_name.lower()}.py"
    with open(view_file, "w") as f:
        f.write(view_content)
    
    # Update __init__.py to import the view
    update_views_init(views_dir, view_name)


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


def generate_model_content(model_name: str, fields: Optional[str]) -> str:
    """
    Generate model content.
    
    Args:
        model_name: Name of the model
        fields: Model fields
        
    Returns:
        Generated model content
    """
    # Parse fields
    field_definitions = []
    if fields:
        for field in fields.split(","):
            if ":" in field:
                name, field_type = field.split(":", 1)
                field_definitions.append(f"    {name.strip()} = {field_type.strip()}")
    
    # Default fields if none provided
    if not field_definitions:
        field_definitions = [
            "    id = Integer(primary_key=True)",
            "    created_at = DateTime(auto_now_add=True)",
            "    updated_at = DateTime(auto_now=True)"
        ]
    
    content = f'''"""
{model_name} model.
"""

from maweng.orm import Model
from maweng.orm.field import Integer, String, DateTime, Text, Boolean, Float

class {model_name}(Model):
    """{model_name} model."""
    
    __tablename__ = "{model_name.lower()}s"
    
{chr(10).join(field_definitions)}
    
    def __repr__(self):
        return f"<{model_name}(id={{self.id}})>"
'''
    
    return content


def generate_view_content(view_name: str, methods: Optional[str]) -> str:
    """
    Generate view content.
    
    Args:
        view_name: Name of the view
        methods: HTTP methods
        
    Returns:
        Generated view content
    """
    # Parse methods
    if methods:
        method_list = [method.strip().upper() for method in methods.split(",")]
    else:
        method_list = ["GET", "POST", "PUT", "DELETE"]
    
    # Generate method handlers
    method_handlers = []
    for method in method_list:
        method_handlers.append(f'''    async def {method.lower()}(self, request):
        """Handle {method} request."""
        return {{"message": "{method} {view_name}"}}''')
    
    content = f'''"""
{view_name} view.
"""

from maweng.view import View

class {view_name}View(View):
    """{view_name} view."""
    
    methods = {method_list}
    
{chr(10).join(method_handlers)}
    
    def register(self, app):
        """Register the view with the app."""
        app.add_view(f"/{view_name.lower()}", self)
'''
    
    return content


def update_models_init(models_dir: Path, model_name: str):
    """
    Update models __init__.py to import the new model.
    
    Args:
        models_dir: Models directory
        model_name: Name of the model
    """
    init_file = models_dir / "__init__.py"
    
    # Read existing content
    if init_file.exists():
        content = init_file.read_text()
    else:
        content = ""
    
    # Add import if not already present
    import_line = f"from .{model_name.lower()} import {model_name}\n"
    if import_line not in content:
        content += import_line
    
    # Write back
    with open(init_file, "w") as f:
        f.write(content)


def update_views_init(views_dir: Path, view_name: str):
    """
    Update views __init__.py to import the new view.
    
    Args:
        views_dir: Views directory
        view_name: Name of the view
    """
    init_file = views_dir / "__init__.py"
    
    # Read existing content
    if init_file.exists():
        content = init_file.read_text()
    else:
        content = ""
    
    # Add import if not already present
    import_line = f"from .{view_name.lower()} import {view_name}View\n"
    if import_line not in content:
        content += import_line
    
    # Add to register_views function if it exists
    if "def register_views" in content:
        # Find the register_views function and add registration
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "def register_views" in line:
                # Find the end of the function and add registration
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() == "" and j + 1 < len(lines) and lines[j + 1].startswith("def"):
                        lines.insert(j, f"    {view_name}View().register(app)")
                        break
                break
        content = "\n".join(lines)
    else:
        # Create register_views function
        content += f'''

def register_views(app):
    """Register all views with the app."""
    {view_name}View().register(app)
'''
    
    # Write back
    with open(init_file, "w") as f:
        f.write(content)
