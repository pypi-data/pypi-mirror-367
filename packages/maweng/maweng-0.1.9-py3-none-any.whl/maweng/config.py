"""
Configuration system for the Maweng framework.

This module provides the configuration classes and utilities for managing
application settings with environment variable support and type validation.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Config(BaseSettings):
    """
    Main configuration class for Maweng applications.
    
    This class provides a centralized way to manage application settings
    with support for environment variables, type validation, and sensible defaults.
    """
    
    # Application settings
    APP_NAME: str = Field(default="maweng", description="Application name")
    DEBUG: bool = Field(default=False, description="Debug mode")
    SECRET_KEY: str = Field(default="your-secret-key-change-this", description="Secret key for sessions")
    
    # Server settings
    HOST: str = Field(default="127.0.0.1", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    WORKERS: int = Field(default=1, description="Number of worker processes")
    
    # Database settings
    DATABASE_URL: str = Field(
        default="sqlite:///./app.db",
        description="Database connection URL"
    )
    DATABASE_ECHO: bool = Field(default=False, description="Echo SQL queries")
    DATABASE_POOL_SIZE: int = Field(default=5, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, description="Database max overflow")
    
    # CORS settings
    CORS_ENABLED: bool = Field(default=True, description="Enable CORS")
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, description="Allow CORS credentials")
    CORS_ALLOW_METHODS: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="Allowed CORS methods"
    )
    CORS_ALLOW_HEADERS: List[str] = Field(
        default=["*"],
        description="Allowed CORS headers"
    )
    
    # Static files and templates
    STATIC_DIR: str = Field(default="static", description="Static files directory")
    TEMPLATE_DIR: str = Field(default="templates", description="Templates directory")
    
    # Logging settings
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    
    # Security settings
    JWT_SECRET_KEY: str = Field(
        default="your-jwt-secret-key-change-this",
        description="JWT secret key"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="JWT access token expiration time in minutes"
    )
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="JWT refresh token expiration time in days"
    )
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Requests per minute")
    RATE_LIMIT_WINDOW: int = Field(default=60, description="Rate limit window in seconds")
    
    # Cache settings
    CACHE_ENABLED: bool = Field(default=False, description="Enable caching")
    CACHE_URL: str = Field(default="redis://localhost:6379/0", description="Cache URL")
    CACHE_TTL: int = Field(default=300, description="Cache TTL in seconds")
    
    # File upload settings
    UPLOAD_DIR: str = Field(default="uploads", description="Upload directory")
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, description="Max file size in bytes")
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=["jpg", "jpeg", "png", "gif", "pdf", "txt"],
        description="Allowed file extensions"
    )
    
    # Email settings
    EMAIL_ENABLED: bool = Field(default=False, description="Enable email functionality")
    EMAIL_HOST: str = Field(default="localhost", description="SMTP host")
    EMAIL_PORT: int = Field(default=587, description="SMTP port")
    EMAIL_USERNAME: str = Field(default="", description="SMTP username")
    EMAIL_PASSWORD: str = Field(default="", description="SMTP password")
    EMAIL_USE_TLS: bool = Field(default=True, description="Use TLS for SMTP")
    EMAIL_FROM: str = Field(default="noreply@example.com", description="Default from email")
    
    # API documentation
    API_DOCS_ENABLED: bool = Field(default=True, description="Enable API documentation")
    API_DOCS_URL: str = Field(default="/docs", description="API docs URL")
    API_REDOC_URL: str = Field(default="/redoc", description="ReDoc URL")
    
    # Testing settings
    TESTING: bool = Field(default=False, description="Testing mode")
    TEST_DATABASE_URL: str = Field(
        default="sqlite:///./test.db",
        description="Test database URL"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @field_validator("SECRET_KEY", "JWT_SECRET_KEY")
    @classmethod
    def validate_secret_keys(cls, v: str) -> str:
        """Validate that secret keys are not using default values in production."""
        if not cls.DEBUG and v in ["your-secret-key-change-this", "your-jwt-secret-key-change-this"]:
            raise ValueError("Secret keys must be changed in production")
        return v
    
    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        if not v.startswith(("sqlite://", "postgresql://", "mysql://", "oracle://")):
            raise ValueError("Invalid database URL format")
        return v
    
    @field_validator("CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, v: List[str]) -> List[str]:
        """Validate CORS origins."""
        if "*" in v and len(v) > 1:
            raise ValueError("Cannot use '*' with other origins")
        return v
    
    def get_database_url(self) -> str:
        """Get the appropriate database URL based on environment."""
        if self.TESTING:
            return self.TEST_DATABASE_URL
        return self.DATABASE_URL
    
    def get_static_dir(self) -> Path:
        """Get the static directory path."""
        return Path(self.STATIC_DIR)
    
    def get_template_dir(self) -> Path:
        """Get the template directory path."""
        return Path(self.TEMPLATE_DIR)
    
    def get_upload_dir(self) -> Path:
        """Get the upload directory path."""
        return Path(self.UPLOAD_DIR)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.model_dump()
    
    def update(self, **kwargs: Any) -> None:
        """Update configuration with new values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class DevelopmentConfig(Config):
    """Development configuration with debug enabled."""
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./dev.db"
    LOG_LEVEL: str = "DEBUG"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]


class ProductionConfig(Config):
    """Production configuration with security settings."""
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"
    CORS_ORIGINS: List[str] = []
    RATE_LIMIT_ENABLED: bool = True
    CACHE_ENABLED: bool = True
    
    @field_validator("SECRET_KEY", "JWT_SECRET_KEY")
    @classmethod
    def validate_production_secrets(cls, v: str) -> str:
        """Ensure production secrets are properly set."""
        if v in ["your-secret-key-change-this", "your-jwt-secret-key-change-this"]:
            raise ValueError("Production secret keys must be set")
        return v


class TestingConfig(Config):
    """Testing configuration."""
    TESTING: bool = True
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./test.db"
    LOG_LEVEL: str = "DEBUG"
    CORS_ENABLED: bool = False
    RATE_LIMIT_ENABLED: bool = False
    CACHE_ENABLED: bool = False


def load_config(config_class: Optional[str] = None) -> Config:
    """
    Load configuration based on environment.
    
    Args:
        config_class: Configuration class name to use
        
    Returns:
        Configuration instance
    """
    env = os.getenv("MAWENG_ENV", "development").lower()
    
    if config_class:
        # Import and return specified config class
        config_map = {
            "development": DevelopmentConfig,
            "production": ProductionConfig,
            "testing": TestingConfig,
        }
        return config_map.get(config_class, DevelopmentConfig)()
    
    # Auto-detect based on environment
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig() 