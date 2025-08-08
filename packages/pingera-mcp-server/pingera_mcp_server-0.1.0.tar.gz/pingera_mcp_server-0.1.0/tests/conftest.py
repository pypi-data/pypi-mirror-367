
"""
Pytest configuration and shared fixtures.
"""
import pytest
import os
from unittest.mock import Mock, patch

from config import Config, OperationMode
from pingera import PingeraClient, Page, PageList


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    config = Config()
    config.api_key = "test_api_key"
    config.base_url = "https://api.test.com/v1"
    config.mode = OperationMode.READ_ONLY
    config.timeout = 30
    config.max_retries = 3
    config.debug = False
    config.server_name = "Test MCP Server"
    return config


@pytest.fixture
def mock_page():
    """Create a mock page object for testing."""
    return Page(
        id="123",
        name="Test Page",
        url="https://example.com",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
        organization_id="org123"
    )


@pytest.fixture
def mock_page_list(mock_page):
    """Create a mock page list for testing."""
    return PageList(
        pages=[mock_page],
        total=1,
        page=1,
        per_page=10
    )


@pytest.fixture
def mock_pingera_client():
    """Create a mock Pingera client for testing."""
    client = Mock(spec=PingeraClient)
    client.test_connection.return_value = True
    client.get_api_info.return_value = {
        "connected": True,
        "version": "v1",
        "status": "ok"
    }
    return client
