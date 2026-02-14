"""Library tests."""

import json
import logging

import pytest
import aiohttp
from aiohttp.client_exceptions import ServerTimeoutError, ContentTypeError
from unittest.mock import MagicMock

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


async def test_get_devices_no_sublist(mock_aioclient, caplog):
    """Test get_devices function."""
    mock_aioclient.get(
        BASE_URL + DEVICE_LIST,
        status=200,
        body=load_fixture("device_list_error.json"),
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
    with caplog.at_level(logging.DEBUG):
        await handler.get_devices()
    assert "No subdevices found." in caplog.text


async def test_get_devices_with_session(mock_aioclient):
    """Test get_devices function with external session."""
    mock_aioclient.get(
        BASE_URL + DEVICE_LIST,
        status=200,
        body="[]",
    )
    async with aiohttp.ClientSession() as session:
        handler = renogyapi.Renogy(
            secret_key="fakeSecretKey", access_key="FakeAccessKey", session=session
        )
        with pytest.raises(NoDevices):
            await handler.get_devices()


async def test_process_request_errors(mock_aioclient):
    """Test process_request error statuses."""
    handler = renogyapi.Renogy(secret_key="fakeSecretKey", access_key="FakeAccessKey")

    mock_aioclient.get(BASE_URL + "/404", status=404)
    with pytest.raises(UrlNotFound):
        await handler.process_request(BASE_URL + "/404", {})

    mock_aioclient.get(BASE_URL + "/401", status=401)
    with pytest.raises(NotAuthorized):
        await handler.process_request(BASE_URL + "/401", {})

    mock_aioclient.get(BASE_URL + "/429", status=429)
    with pytest.raises(RateLimit):
        await handler.process_request(BASE_URL + "/429", {})

    mock_aioclient.get(BASE_URL + "/500", status=500, body="Error")
    resp = await handler.process_request(BASE_URL + "/500", {})
    assert resp == {"error": "Error"}

    mock_aioclient.get(BASE_URL + "/500json", status=500, body='{"msg": "failure"}')
    resp = await handler.process_request(BASE_URL + "/500json", {})
    assert resp == {"error": {"msg": "failure"}}


async def test_process_request_exceptions(mock_aioclient):
    """Test process_request exceptions."""
    handler = renogyapi.Renogy(secret_key="fakeSecretKey", access_key="FakeAccessKey")

    # Timeout
    mock_aioclient.get(BASE_URL + "/timeout", exception=ServerTimeoutError())
    resp = await handler.process_request(BASE_URL + "/timeout", {})
    assert resp == {"error": renogyapi.ERROR_TIMEOUT}

    # Non-JSON response
    mock_aioclient.get(BASE_URL + "/nonjson", status=200, body="Not JSON")
    resp = await handler.process_request(BASE_URL + "/nonjson", {})
    assert resp == {"error": "Not JSON"}


async def test_process_request_unicode_error(mock_aioclient):
    """Test process_request UnicodeDecodeError handling."""
    handler = renogyapi.Renogy(secret_key="fakeSecretKey", access_key="FakeAccessKey")

    # body=b"\xff" triggers UnicodeDecodeError on text()
    mock_aioclient.get(BASE_URL + "/unicode", status=200, body=b"\xff")
    resp = await handler.process_request(BASE_URL + "/unicode", {})
    assert "error" in resp
    assert resp["error"] == "\ufffd"


async def test_process_request_content_type_error(mock_aioclient):
    """Test process_request ContentTypeError handling."""
    handler = renogyapi.Renogy(secret_key="fakeSecretKey", access_key="FakeAccessKey")

    mock_aioclient.get(
        BASE_URL + "/contenttype", exception=ContentTypeError(MagicMock(), ())
    )
    resp = await handler.process_request(BASE_URL + "/contenttype", {})
    assert "error" in resp
