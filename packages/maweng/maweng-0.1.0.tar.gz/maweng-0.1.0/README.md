# Maweng Framework

A lightweight, modern Python web framework designed for building scalable backend systems with ease. Maweng combines the simplicity of Flask with the power of FastAPI, featuring an intuitive ORM, auto-generated API documentation, and developer-friendly tooling.

## 🚀 Features

- **Lightning Fast**: Built on top of FastAPI and Uvicorn for exceptional performance
- **Intuitive ORM**: SQLAlchemy-based ORM with automatic migrations
- **Auto-Generated API Docs**: OpenAPI/Swagger documentation out of the box
- **Type Safety**: Full type hints and Pydantic integration
- **Dependency Injection**: Clean architecture with built-in DI container
- **CLI Tools**: Project scaffolding and management utilities
- **Testing Framework**: Built-in testing utilities and fixtures
- **Modern Python**: Python 3.8+ with async/await support

## 📦 Installation

```bash
# Install from PyPI (when available)
pip install maweng

# Or install from source
git clone https://github.com/maweng/framework.git
cd framework
pip install -e .
```

## 🎯 Quick Start

### 1. Create a New Project

```bash
maweng new myapp
cd myapp
```

### 2. Define Your Models

```python
# models.py
from maweng.orm import Model, Field
from datetime import datetime

class User(Model):
    __tablename__ = "users"
    
    id = Field.Integer(primary_key=True)
    email = Field.String(unique=True, max_length=255)
    name = Field.String(max_length=100)
    created_at = Field.DateTime(default=datetime.utcnow)
    is_active = Field.Boolean(default=True)
```

### 3. Create Your Views

```python
# views.py
from maweng import View, Response
from maweng.orm import query
from .models import User

class UserView(View):
    @query.get("/users")
    async def list_users(self):
        users = await User.all()
        return Response.json(users)
    
    @query.post("/users")
    async def create_user(self, user_data: dict):
        user = await User.create(**user_data)
        return Response.json(user, status=201)
    
    @query.get("/users/{user_id}")
    async def get_user(self, user_id: int):
        user = await User.get(user_id)
        if not user:
            return Response.json({"error": "User not found"}, status=404)
        return Response.json(user)
```

### 4. Run Your Application

```bash
maweng run
```

Visit `http://localhost:8000/docs` to see your auto-generated API documentation!

## 🏗️ Project Structure

```
myapp/
├── app/
│   ├── __init__.py
│   ├── models.py          # Database models
│   ├── views.py           # API endpoints
│   ├── services.py        # Business logic
│   └── middleware.py      # Custom middleware
├── migrations/            # Database migrations
├── tests/                 # Test files
├── static/               # Static files
├── templates/            # HTML templates
├── config.py             # Configuration
└── main.py              # Application entry point
```

## 🔧 Configuration

```python
# config.py
from maweng.config import Config

class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URL = "sqlite:///./dev.db"
    SECRET_KEY = "your-secret-key"
    
class ProductionConfig(Config):
    DEBUG = False
    DATABASE_URL = "postgresql://user:pass@localhost/db"
    SECRET_KEY = "your-production-secret"
```

## 🗄️ ORM Usage

### Basic CRUD Operations

```python
# Create
user = await User.create(name="John Doe", email="john@example.com")

# Read
user = await User.get(1)
users = await User.filter(is_active=True)
all_users = await User.all()

# Update
await user.update(name="Jane Doe")
# or
await User.filter(id=1).update(name="Jane Doe")

# Delete
await user.delete()
# or
await User.filter(id=1).delete()
```

### Relationships

```python
class Post(Model):
    __tablename__ = "posts"
    
    id = Field.Integer(primary_key=True)
    title = Field.String(max_length=200)
    content = Field.Text()
    author_id = Field.Integer(foreign_key="users.id")
    
    # Define relationship
    author = Relationship("User", back_populates="posts")

class User(Model):
    # ... existing fields ...
    posts = Relationship("Post", back_populates="author")
```

## 🧪 Testing

```python
# tests/test_users.py
import pytest
from maweng.testing import TestClient
from app.models import User

@pytest.mark.asyncio
async def test_create_user():
    client = TestClient()
    
    response = await client.post("/users", json={
        "name": "Test User",
        "email": "test@example.com"
    })
    
    assert response.status_code == 201
    assert response.json()["name"] == "Test User"
```

## 📚 Documentation

- [Getting Started Guide](https://maweng.dev/getting-started)
- [API Reference](https://maweng.dev/api)
- [ORM Documentation](https://maweng.dev/orm)
- [Testing Guide](https://maweng.dev/testing)
- [Deployment Guide](https://maweng.dev/deployment)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆚 Comparison with Other Frameworks

| Feature | Maweng | FastAPI | Django | Flask |
|---------|--------|---------|--------|-------|
| Performance | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Ease of Use | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| ORM | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Auto Docs | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ |
| Type Safety | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Learning Curve | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |

## 🚀 Roadmap

- [ ] GraphQL support
- [ ] WebSocket support
- [ ] Background task queue
- [ ] Admin interface
- [ ] Plugin system
- [ ] Microservices support
- [ ] Kubernetes deployment tools

---

Built with ❤️ by the Maweng Framework Team 