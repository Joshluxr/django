import pytest
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from verifier import verify_url


@pytest.mark.asyncio
async def test_verify_url_invalid_url():
    """Test verification of invalid URL."""
    result = await verify_url(
        url="not-a-url",
        allowed_domains=["*.popmart.com"],
        proxy=None,
        timeout=5,
        user_agent="TestBot",
        retries=1,
        backoff=1.0
    )
    
    assert result.ok is False
    assert result.status == "rejected"
    assert result.reason == "Invalid URL"


@pytest.mark.asyncio
async def test_verify_url_domain_not_allowed():
    """Test verification of URL with non-allowed domain."""
    result = await verify_url(
        url="https://evil-site.com/product",
        allowed_domains=["*.popmart.com"],
        proxy=None,
        timeout=5,
        user_agent="TestBot",
        retries=1,
        backoff=1.0
    )
    
    assert result.ok is False
    assert result.status == "rejected"
    assert result.reason == "Domain not allowed"
    assert result.domain_allowed is False


@pytest.mark.asyncio
async def test_verify_url_allowed_domain():
    """Test that popmart.com matches *.popmart.com pattern."""
    # This will fail at connection, but should pass domain check
    result = await verify_url(
        url="https://www.popmart.com/product",
        allowed_domains=["*.popmart.com"],
        proxy=None,
        timeout=2,
        user_agent="TestBot",
        retries=1,
        backoff=1.0
    )
    
    # Should not fail on domain check
    assert result.domain_allowed is True
    # May fail on connection, which is expected in test environment
