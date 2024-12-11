"""Library tests."""

import json
import logging

import pytest
from aiohttp.client_exceptions import ServerTimeoutError

import renogyapi
from renogyapi.exceptions import NotAuthorized, RateLimit, UrlNotFound
from tests.common import load_fixture

pytestmark = pytest.mark.asyncio

BASE_URL = "https://openapi.renogy.com"
DEVICE_LIST = "/device/list"


async def test_get_devices(mock_aioclient, caplog):
    """Test get_devices function."""
    mock_aioclient.get(
        BASE_URL + DEVICE_LIST,
        status=200,
        body=load_fixture("device_list.json"),
        repeat=True,
    )
    mock_aioclient.get(
        f"{BASE_URL}/device/data/latest/1234567890",
        status=200,
        body="",
        repeat=True,
    )
    mock_aioclient.get(
        f"{BASE_URL}/device/data/latest/12345678901",
        status=200,
        body="",
        repeat=True,
    )
    mock_aioclient.get(
        f"{BASE_URL}/device/data/latest/12345678902",
        status=200,
        body="",
        repeat=True,
    )
    mock_aioclient.get(
        f"{BASE_URL}/device/data/latest/12345678903",
        status=200,
        body=load_fixture("realtime_data.json"),
        repeat=True,
    )
    handler = renogyapi.Renogy(secret_key="fakeSecretKey", access_key="FakeAccessKey")
    data = await handler.get_devices()
    assert data["12345678903"]["data"]["batteryLevel"] == 54.784637
