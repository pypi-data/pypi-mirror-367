"""Configuration management for Respona MCP Server."""

import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class ResponaConfig(BaseSettings):
    """Configuration for Respona API connection."""
    
    # API Configuration
    api_base_url: str = Field(
        default="http://10.250.201.107:3001",
        description="Base URL for the Respona Dashboard API"
    )
    
    # Optional API authentication (if needed in the future)
    api_key: Optional[str] = Field(
        default=None,
        description="API key for authentication (if required)"
    )
    
    # Request configuration
    request_timeout: int = Field(
        default=30,
        description="Request timeout in seconds"
    )
    
    max_retries: int = Field(
        default=3,
        description="Maximum number of request retries"
    )
    
    # Pagination defaults
    default_page_size: int = Field(
        default=20,
        description="Default number of items per page"
    )
    
    max_page_size: int = Field(
        default=100,
        description="Maximum allowed page size"
    )

    model_config = {
        "env_prefix": "RESPONA_",
        "case_sensitive": False
    }


# Global configuration instance
config = ResponaConfig() 