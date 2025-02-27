from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, validator
from typing import Optional, Dict, Any
from enum import Enum

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
    # API Keys - using SecretStr for better security
    tavily_api_key: SecretStr
    google_api_key: SecretStr
    
    # Search Configuration
    max_results_per_query: int = 10
    search_depth: SearchDepth = SearchDepth.BASIC
    max_retries: int = 3
    request_timeout: int = 30
    
    # Agent Configuration
    research_agent_model: str = "gemini-1.5-flash"
    synthesis_agent_model: str = "gemini-1.5-flash"
    
    # Storage Configuration
    cache_dir: str = "./cache"
    results_dir: str = "./results"
    
    @validator('tavily_api_key', 'google_api_key')
    def validate_api_keys(cls, v):
        """Validate that API keys are non-empty strings"""
        if not v:
            raise ValueError("API key cannot be empty")
        return v
    
    model_config = SettingsConfigDict(env_file='.env')

settings = Settings()