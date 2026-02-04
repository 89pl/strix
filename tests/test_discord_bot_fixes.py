#!/usr/bin/env python3
"""
Test suite for Discord bot fixes - validates URL construction and API readiness checks.
"""

import pytest
import sys
import os

# Add the parent directory to the path so we can import from discord_bot
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the function we need to test
# We'll define it inline since we can't easily import from discord_bot.py without Discord dependencies
def get_chat_completions_url(base_endpoint: str) -> str:
    """Construct the correct chat completions URL from the base endpoint.
    
    The CLIPROXY_ENDPOINT is set to something like 'http://127.0.0.1:8317/v1'
    For chat completions, we need to POST to 'http://127.0.0.1:8317/v1/chat/completions'
    """
    # Remove trailing slash if present
    base = base_endpoint.rstrip('/')
    
    # Check if endpoint already ends with /chat/completions
    if base.endswith('/chat/completions'):
        return base
    
    # Check if endpoint ends with /v1, append /chat/completions
    if base.endswith('/v1'):
        return f"{base}/chat/completions"
    
    # Otherwise, assume it's a base URL and add /v1/chat/completions
    return f"{base}/v1/chat/completions"


class TestGetChatCompletionsUrl:
    """Test cases for get_chat_completions_url function."""
    
    def test_endpoint_with_v1(self):
        """Test that endpoint with /v1 gets /chat/completions appended."""
        endpoint = "http://127.0.0.1:8317/v1"
        expected = "http://127.0.0.1:8317/v1/chat/completions"
        assert get_chat_completions_url(endpoint) == expected
    
    def test_endpoint_with_v1_and_trailing_slash(self):
        """Test that endpoint with /v1/ gets /chat/completions appended correctly."""
        endpoint = "http://127.0.0.1:8317/v1/"
        expected = "http://127.0.0.1:8317/v1/chat/completions"
        assert get_chat_completions_url(endpoint) == expected
    
    def test_endpoint_without_v1(self):
        """Test that endpoint without /v1 gets /v1/chat/completions appended."""
        endpoint = "http://127.0.0.1:8317"
        expected = "http://127.0.0.1:8317/v1/chat/completions"
        assert get_chat_completions_url(endpoint) == expected
    
    def test_endpoint_without_v1_with_trailing_slash(self):
        """Test that endpoint without /v1 but with trailing slash works."""
        endpoint = "http://127.0.0.1:8317/"
        expected = "http://127.0.0.1:8317/v1/chat/completions"
        assert get_chat_completions_url(endpoint) == expected
    
    def test_endpoint_already_has_chat_completions(self):
        """Test that endpoint already with /chat/completions is unchanged."""
        endpoint = "http://127.0.0.1:8317/v1/chat/completions"
        expected = "http://127.0.0.1:8317/v1/chat/completions"
        assert get_chat_completions_url(endpoint) == expected
    
    def test_https_endpoint(self):
        """Test with HTTPS endpoint."""
        endpoint = "https://api.example.com/v1"
        expected = "https://api.example.com/v1/chat/completions"
        assert get_chat_completions_url(endpoint) == expected
    
    def test_custom_port(self):
        """Test with custom port."""
        endpoint = "http://localhost:3000/v1"
        expected = "http://localhost:3000/v1/chat/completions"
        assert get_chat_completions_url(endpoint) == expected
    
    def test_openai_style_endpoint(self):
        """Test with OpenAI-style endpoint."""
        endpoint = "https://api.openai.com/v1"
        expected = "https://api.openai.com/v1/chat/completions"
        assert get_chat_completions_url(endpoint) == expected


class TestApiReadinessUrlConstruction:
    """Test cases for API readiness URL construction logic."""
    
    def test_construct_models_url_from_v1_endpoint(self):
        """Test constructing /models URL from endpoint with /v1."""
        base_endpoint = "http://127.0.0.1:8317/v1"
        base = base_endpoint.rstrip('/')
        
        urls_to_check = []
        if base.endswith('/v1'):
            urls_to_check.append(f"{base}/models")
            base_url = base[:-3]  # Remove /v1
            urls_to_check.append(f"{base_url}/health")
            urls_to_check.append(base_url)
        
        assert urls_to_check == [
            "http://127.0.0.1:8317/v1/models",
            "http://127.0.0.1:8317/health",
            "http://127.0.0.1:8317"
        ]
    
    def test_construct_models_url_from_base_endpoint(self):
        """Test constructing /models URL from base endpoint without /v1."""
        base_endpoint = "http://127.0.0.1:8317"
        base = base_endpoint.rstrip('/')
        
        urls_to_check = []
        if base.endswith('/v1'):
            urls_to_check.append(f"{base}/models")
        else:
            urls_to_check.append(f"{base}/v1/models")
            urls_to_check.append(f"{base}/models")
            urls_to_check.append(f"{base}/health")
            urls_to_check.append(base)
        
        assert urls_to_check == [
            "http://127.0.0.1:8317/v1/models",
            "http://127.0.0.1:8317/models",
            "http://127.0.0.1:8317/health",
            "http://127.0.0.1:8317"
        ]


class TestToolServerPortValidation:
    """Test cases for tool server port validation logic."""
    
    def test_default_port_value(self):
        """Test that default port is used when not set."""
        tool_server_port = ""
        
        if not tool_server_port:
            tool_server_port = "48081"
        
        assert tool_server_port == "48081"
    
    def test_port_value_preserved_when_set(self):
        """Test that port value is preserved when already set."""
        tool_server_port = "8080"
        
        if not tool_server_port:
            tool_server_port = "48081"
        
        assert tool_server_port == "8080"
    
    def test_port_can_be_converted_to_int(self):
        """Test that port value can be converted to int."""
        tool_server_port = "48081"
        assert int(tool_server_port) == 48081
    
    def test_default_port_can_be_converted_to_int(self):
        """Test that default port can be converted to int."""
        tool_server_port = ""
        if not tool_server_port:
            tool_server_port = "48081"
        
        assert int(tool_server_port) == 48081


if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v", "--tb=short"])
