"""
Unit tests for agent configuration.
"""
import pytest
import os
from agent.agent import create_agent


def test_agent_missing_api_key():
    """Test agent creation fails without API key."""
    # Temporarily remove API key
    original_key = os.environ.get("OPENAI_API_KEY")
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    
    try:
        with pytest.raises(ValueError, match="OPENAI_API_KEY not found"):
            create_agent()
    finally:
        # Restore original key if it existed
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key


def test_agent_with_test_key():
    """Test agent creation structure with test key."""
    # Set a test key
    original_key = os.environ.get("OPENAI_API_KEY")
    os.environ["OPENAI_API_KEY"] = "test-key-123"
    
    try:
        # Should create agent (will fail on actual API call, but structure is correct)
        agent = create_agent()
        assert agent is not None
        assert agent.name == "DocumentQA"
    finally:
        # Restore original key
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key
        elif "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]

