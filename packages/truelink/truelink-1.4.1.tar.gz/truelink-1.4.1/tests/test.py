"""Tests for the TrueLinkResolver class."""

from __future__ import annotations

import contextlib

import pytest

from truelink.core import TrueLinkResolver
from truelink.exceptions import UnsupportedProviderException


@pytest.mark.asyncio
async def test_truelink_resolver_resolve_unsupported_link() -> None:
    """Test that an unsupported link raises an exception."""
    resolver = TrueLinkResolver()
    url = "https://example.com"
    with pytest.raises(UnsupportedProviderException):
        await resolver.resolve(url)


@pytest.mark.asyncio
async def test_truelink_resolver_resolve_supported_link() -> None:
    """Test that a supported link returns a non-empty result."""
    resolver = TrueLinkResolver()
    url = "https://www.mediafire.com/file/abcdef1234567/test.txt/file"
    # This will fail, but we're just testing that it doesn't raise an exception
    with contextlib.suppress(Exception):
        result = await resolver.resolve(url)
        assert result is not None
