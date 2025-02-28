from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, validator, Field
from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class SearchDepth(str, Enum):
    BASIC = "basic"
    ADVANCED = "advanced"

    @classmethod
    def from_user_input(cls, value: str) -> "SearchDepth":
        """Convert user-friendly input to valid search depth"""
        value = value.lower()
        if value in ["shallow", "medium"]:
            return cls.BASIC
        elif value in ["deep"]:
            return cls.ADVANCED
        return cls.BASIC  # default to basic

class Settings(BaseSettings):
    # System Information
    current_timestamp: datetime = Field(
        default_factory=lambda: datetime.strptime("2025-02-28 12:35:06", "%Y-%m-%d %H:%M:%S")
    )
    current_user: str = Field(default="srikrishnavansi")
    
    # API Keys - using SecretStr for better security
    tavily_api_key: SecretStr = Field(
        default=SecretStr(os.getenv("TAVILY_API_KEY", "default-tavily-key")),
        description="Tavily API Key"
    )
    google_api_key: SecretStr = Field(
        default=SecretStr(os.getenv("GOOGLE_API_KEY", "default-google-key")),
        description="Google API Key"
    )
    
    # Search Configuration
    max_results_per_query: int = 10
    search_depth: SearchDepth = SearchDepth.BASIC
    max_retries: int = 3
    request_timeout: int = 30
    
    # Agent Configuration
    research_agent_model: str = "gemini-1.5-flash"
    synthesis_agent_model: str = "gemini-1.5-flash"
    
    # Base Directories
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent)
    
    # Storage Configuration
    @property
    def cache_dir(self) -> Path:
        cache_path = self.base_dir / "cache"
        cache_path.mkdir(parents=True, exist_ok=True)
        return cache_path
    
    @property
    def results_dir(self) -> Path:
        results_path = self.base_dir / "results"
        results_path.mkdir(parents=True, exist_ok=True)
        return results_path
    
    @validator('tavily_api_key', 'google_api_key')
    def validate_api_keys(cls, v):
        """Validate that API keys are non-empty strings"""
        if not v or v.get_secret_value() in ["default-tavily-key", "default-google-key"]:
            raise ValueError("API key cannot be empty or default value")
        return v
    
    def get_formatted_timestamp(self) -> str:
        """Get current timestamp in YYYY-MM-DD HH:MM:SS format"""
        return self.current_timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    def get_file_timestamp(self) -> str:
        """Get current timestamp in YYYYMMDD_HHMMSS format for filenames"""
        return self.current_timestamp.strftime("%Y%m%d_%H%M%S")
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        use_enum_values=True,
        extra='ignore'
    )
try:
    settings = Settings()
except Exception as e:
    print("Error loading settings. Please check your .env file and ensure API keys are set.")
    print(f"Error details: {str(e)}")
    print("\nMake sure your .env file contains:")
    print("TAVILY_API_KEY=your-tavily-api-key-here")
    print("GOOGLE_API_KEY=your-google-api-key-here")
    raise
