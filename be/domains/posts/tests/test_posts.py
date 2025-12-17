"""
Tests for posts domain.
"""

import pytest


def test_example():
    """Basic test to verify pytest is working."""
    assert True


def test_posts_domain_exists():
    """Test that posts domain can be imported."""
    from domains.posts import __init__
    assert __init__.__doc__ == "Posts domain package."
