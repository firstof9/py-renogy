"""Library tests."""

import json
import logging

import pytest
from aiohttp.client_exceptions import ServerTimeoutError

import renogyapi
from renogyapi.exceptions import NoDevices, NotAuthorized, RateLimit, UrlNotFound
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
    mock_aioclient.get(
        f"{BASE_URL}/device/data/latest/12345678904",
        status=200,
        body="",
        repeat=True,
    )
    mock_aioclient.get(
        f"{BASE_URL}/device/datamap/12345678903",
        status=200,
        body=load_fixture("datamap.json"),
        repeat=True,
    )
    mock_aioclient.get(
        f"{BASE_URL}/device/data/latest/12345678905",
        status=200,
        body="",
        repeat=True,
    )
    mock_aioclient.get(
        f"{BASE_URL}/device/data/latest/12345678906",
        status=200,
        body="",
        repeat=True,
    )
    mock_aioclient.get(
        f"{BASE_URL}/device/data/latest/12345678907",
        status=200,
        body="",
        repeat=True,
    )
    mock_aioclient.get(
        f"{BASE_URL}/device/data/latest/12345678908",
        status=200,
        body=load_fixture("realtime_data.json"),
        repeat=True,
    )
    mock_aioclient.get(
        f"{BASE_URL}/device/data/latest/12345678909",
        status=200,
        body="",
        repeat=True,
    )
    mock_aioclient.get(
        f"{BASE_URL}/device/datamap/12345678908",
        status=200,
        body=load_fixture("datamap.json"),
        repeat=True,
    )    
    handler = renogyapi.Renogy(secret_key="fakeSecretKey", access_key="FakeAccessKey")
    data = await handler.get_devices()
    assert data["12345678903"]["data"]["batteryLevel"] == (54.784637, "%")
    assert data["12345678903"]["data"]["heatingModeStatus"] == (0, "")
    assert data["12345678903"]["data"]["averageTemperature"] == (-3, "°C")
    assert data["12345678904"]["connection"] == "Unknown"
    assert data["12345678903"]["parent"] == "1234567890"
    assert data["12345678906"]["parent"] == "12345678905"


async def test_get_devices_exception(mock_aioclient, caplog):
    """Test get_devices function."""
    mock_aioclient.get(
        BASE_URL + DEVICE_LIST,
        status=200,
        body="[]",
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
        body="",
        repeat=True,
    )
    mock_aioclient.get(
        f"{BASE_URL}/device/data/latest/12345678904",
        status=200,
        body="",
        repeat=True,
    )
    handler = renogyapi.Renogy(secret_key="fakeSecretKey", access_key="FakeAccessKey")
    with pytest.raises(NoDevices):
        await handler.get_devices()
