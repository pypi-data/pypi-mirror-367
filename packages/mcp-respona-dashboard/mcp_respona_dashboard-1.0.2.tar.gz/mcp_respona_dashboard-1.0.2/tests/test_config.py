"""Tests for configuration module."""

import os
import pytest
from respona_mcp_server.config import ResponaConfig


def test_default_config():
    """Test default configuration values."""
    config = ResponaConfig()
    
    assert config.api_base_url == "http://10.250.201.107:3001"
    assert config.api_key is None
    assert config.request_timeout == 30
    assert config.max_retries == 3
    assert config.default_page_size == 20
    assert config.max_page_size == 100


def test_env_override(monkeypatch):
    """Test configuration override via environment variables."""
    monkeypatch.setenv("RESPONA_API_BASE_URL", "http://localhost:3000")
    monkeypatch.setenv("RESPONA_REQUEST_TIMEOUT", "60")
    monkeypatch.setenv("RESPONA_API_KEY", "test-key")
    
    config = ResponaConfig()
    
    assert config.api_base_url == "http://localhost:3000"
    assert config.request_timeout == 60
    assert config.api_key == "test-key" 