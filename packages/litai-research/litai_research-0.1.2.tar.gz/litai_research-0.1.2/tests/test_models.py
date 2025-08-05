"""Tests for data models."""

import pytest
from litai.models import LLMConfig


class TestLLMConfig:
    """Test the LLMConfig model."""
    
    def test_default_values(self):
        """Test default LLMConfig values."""
        config = LLMConfig()
        assert config.provider == "auto"
        assert config.model is None
        assert config.api_key_env is None
        assert config.is_auto is True
    
    def test_custom_values(self):
        """Test LLMConfig with custom values."""
        config = LLMConfig(
            provider="openai",
            model="gpt-4",
            api_key_env="MY_API_KEY"
        )
        assert config.provider == "openai"
        assert config.model == "gpt-4"
        assert config.api_key_env == "MY_API_KEY"
        assert config.is_auto is False
    
    def test_to_dict(self):
        """Test converting LLMConfig to dict."""
        config = LLMConfig(provider="anthropic", model="claude-3")
        d = config.to_dict()
        
        assert d == {
            "provider": "anthropic",
            "model": "claude-3",
            "api_key_env": None
        }
    
    def test_from_dict(self):
        """Test creating LLMConfig from dict."""
        data = {
            "provider": "openai",
            "model": "gpt-4",
            "api_key_env": "CUSTOM_KEY"
        }
        config = LLMConfig.from_dict(data)
        
        assert config.provider == "openai"
        assert config.model == "gpt-4"
        assert config.api_key_env == "CUSTOM_KEY"
    
    def test_from_dict_with_defaults(self):
        """Test creating LLMConfig from partial dict."""
        config = LLMConfig.from_dict({})
        assert config.provider == "auto"
        assert config.model is None
        assert config.api_key_env is None
        
        config = LLMConfig.from_dict({"provider": "anthropic"})
        assert config.provider == "anthropic"
        assert config.model is None
        assert config.api_key_env is None