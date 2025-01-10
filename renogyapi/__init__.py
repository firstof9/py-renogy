"""Main librbary functions for py_renogy."""

from __future__ import annotations

import time
import json
import logging
from typing import Any
from urllib.parse import urlencode

import aiohttp  # type: ignore
from aiohttp.client_exceptions import ContentTypeError, ServerTimeoutError

from .auth import calc_sign
from .exceptions import NoDevices, NotAuthorized, RateLimit, UrlNotFound

CONNECTION_TYPE = {
    "zigbee": "Zigbee",
    "bt": "Bluetooth",
    "rvc": "RVC",
    "rs485": "RS485",
    "rs232": "RS232",
    "ethernet": "Ethernet",
    "wifi": "Wifi",
    "can": "CANBUS",
    "mesh": "Mesh",
    "": "Hub",
}

SUBDEVICE_CONNECTION_TYPE = {
    "zigbee": "Zigbee",
    "bt": "Bluetooth",
    "rvc": "RVC",
    "rs485": "RS485",
    "rs232": "RS232",
    "ethernet": "Ethernet",
    "wifi": "Wifi",
    "can": "CANBUS",
    "mesh": "Mesh",
    "": "Unknown",
}

BASE_URL = "https://openapi.renogy.com"
DEVICE_LIST = "/device/list"

_LOGGER = logging.getLogger(__name__)
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
}
ERROR_TIMEOUT = "Timeout while updating"


class Renogy:
    """Represent a Renogy Hub."""

    def __init__(
        self,
        secret_key: str,
        access_key: str,
    ) -> None:
        """Initialize."""
        self._key = secret_key
        self._access_key = access_key
        self._device_list: dict[Any, Any] = {}

    async def process_request(
        self,
        url: str,
        headers: dict,
    ) -> dict[Any, Any]:
        """Process API requests."""
        async with aiohttp.ClientSession(headers=headers) as session:
            _LOGGER.debug("Request URL: %s", url)
            timeout = aiohttp.ClientTimeout(total=90)
            try:
                async with session.get(url, timeout=timeout) as response:
                    message: Any = {}
                    try:
                        message = await response.text()
                    except UnicodeDecodeError:
                        _LOGGER.debug("Decoding error.")
                        data = await response.read()
                        message = data.decode(errors="replace")

                    try:
                        message = json.loads(message)
                    except ValueError:
                        _LOGGER.warning("Non-JSON response: %s", message)
                        message = {"error": message}

                    if response.status == 404:
                        raise UrlNotFound
                    if response.status == 401:
                        raise NotAuthorized
                    if response.status == 429:
                        raise RateLimit
                    if response.status != 200:
                        _LOGGER.error(  # pylint: disable-next=line-too-long
                            "An error reteiving data from the server, code: %s\nmessage: %s",  # noqa: E501
                            response.status,
                            message,
                        )
                        message = {"error": message}
                    return message

            except (TimeoutError, ServerTimeoutError):
                _LOGGER.error("%s: %s", ERROR_TIMEOUT, url)
                message = {"error": ERROR_TIMEOUT}
            except ContentTypeError as err:
                _LOGGER.error("%s", err)
                message = {"error": err}

            await session.close()
            return message

    async def get_devices(self) -> dict:
        """Provide list of devices associated with account."""
        processed_devices = {}
        timestamp = int(time.time() * 1000)
        params: dict[Any, Any] = {}
        signature = calc_sign(DEVICE_LIST, urlencode(params), timestamp, self._key)
        headers = {
            "Access-Key": self._access_key,
            "Signature": signature,
            "Timestamp": str(timestamp),
        }
        url = BASE_URL + DEVICE_LIST
        response = await self.process_request(url, headers)

        _LOGGER.debug("Response: %s", response)

        if len(response) == 0:
            _LOGGER.info("Renogy API returned no devices.")
            raise NoDevices

        if "deviceId" in response[0].keys():
            # Main 'hub' data
            data = {}
            data["deviceId"] = response[0]["deviceId"]
            data["name"] = response[0]["name"]
            data["mac"] = response[0]["mac"]
            data["firmware"] = response[0]["firmware"]
            data["status"] = response[0]["onlineStatus"]
            data["connection"] = CONNECTION_TYPE[response[0]["connectType"]]
            data["serial"] = response[0]["sn"]
            data["model"] = response[0]["sku"]
            data["data"] = await self.get_realtime_data(data["deviceId"])

            processed_devices[data["deviceId"]] = data

            if "sublist" in response[0].keys():
                # Sub devices
                if len(response[0]["sublist"][0]) > 0:
                    for device in response[0]["sublist"]:
                        _LOGGER.debug("Device: %s", device)
                        data = {}
                        data["deviceId"] = device["deviceId"]
                        data["name"] = device["name"]
                        data["mac"] = device["mac"]
                        data["firmware"] = device["firmware"]
                        data["status"] = device["onlineStatus"]
                        data["connection"] = SUBDEVICE_CONNECTION_TYPE[
                            device["connectType"]
                        ]
                        data["serial"] = device["sn"]
                        data["model"] = device["sku"]
                        data["data"] = await self.get_realtime_data(data["deviceId"])
                        processed_devices[data["deviceId"]] = data

        self._device_list = processed_devices
        return self._device_list

    async def get_realtime_data(self, device_id: str) -> dict:
        """Provide reatime data of specified device_id."""
        timestamp = int(time.time() * 1000)
        path = f"/device/data/latest/{device_id}"
        params: dict[Any, Any] = {}
        signature = calc_sign(path, urlencode(params), timestamp, self._key)
        headers = {
            "Access-Key": self._access_key,
            "Signature": signature,
            "Timestamp": str(timestamp),
        }
        url = BASE_URL + path
        response = await self.process_request(url, headers)
        _LOGGER.debug("Response realtime: %s", response)
        if "data" not in response.keys():
            _LOGGER.warning("No data in API response.")
            return {}
        return response["data"]
