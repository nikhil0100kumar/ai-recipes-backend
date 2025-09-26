"""
Configuration management for AI Recipes Backend
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # Gemini API Configuration
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")  # Render will provide this
    debug: bool = Field(default=False, env="DEBUG")
    
    # CORS Configuration
    allowed_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000", 
        env="ALLOWED_ORIGINS"
    )
    
    # Upload Configuration
    max_file_size_mb: int = Field(default=10, env="MAX_FILE_SIZE_MB")
    allowed_file_types: str = Field(
        default="image/jpeg,image/jpg,image/png,image/webp",
        env="ALLOWED_FILE_TYPES"
    )
    
    # API Configuration
    gemini_model: str = "gemini-2.0-flash-exp"
    request_timeout: int = 30
    max_retries: int = 3
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert comma-separated origins to list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        """Convert comma-separated file types to list."""
        return [file_type.strip() for file_type in self.allowed_file_types.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Convert MB to bytes."""
        return self.max_file_size_mb * 1024 * 1024


# Global settings instance
settings = Settings()
