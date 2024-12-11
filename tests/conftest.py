"""Provide common pytest fixtures."""

import json

import pytest
from aioresponses import aioresponses


@pytest.fixture
def mock_aioclient():
    """Fixture to mock aioclient calls."""
    with aioresponses() as m:
        yield m
