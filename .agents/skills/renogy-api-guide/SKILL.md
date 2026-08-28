---
name: renogy-api-guide
description: >-
  Use this skill when developing, refactoring, or integrating with the py-renogy
  library and Renogy OpenAPI, including authentication signatures, device hierarchy,
  realtime telemetry, datamap parsing, and error handling.
---

# Renogy API & Architecture Guide

This skill provides architectural guidelines, endpoint conventions, authentication flows, and error handling patterns for `py-renogy`.

## Architecture Overview

The library wraps the Renogy OpenAPI (`https://openapi.renogy.com`):

- **`renogyapi/__init__.py`**: Contains the main `Renogy` client class and constants (`CONNECTION_TYPE`, `SUBDEVICE_CONNECTION_TYPE`, `BASE_URL`, `DEVICE_LIST`).
- **`renogyapi/auth.py`**: Authentication helper (`calc_sign`) calculating HMAC-SHA256 request signatures.
- **`renogyapi/exceptions.py`**: Exception hierarchy (`UrlNotFound`, `NotAuthorized`, `RateLimit`, `InvalidCall`, `NoDevices`).

## Client Initialization

The `Renogy` class supports both internal session management and external `aiohttp.ClientSession` dependency injection:

```python
from renogyapi import Renogy

# Managed internal session:
client = Renogy(secret_key="...", access_key="...")

# Injected external session:
async with aiohttp.ClientSession() as session:
    client = Renogy(secret_key="...", access_key="...", session=session)
```

## Authentication & Request Signing

Renogy OpenAPI requires HMAC-SHA256 signing for all requests:

1. **Signature Calculation (`calc_sign`)**:
   - String to sign: `"{timestamp}.{path}.{urlencode(params)}"`
   - Algorithm: `hmac.new(secret_key.encode("utf-8"), str_to_sign.encode(), hashlib.sha256)`
   - Output: Base64-encoded digest string.
2. **Required HTTP Headers**:
   ```python
   headers = {
       "Access-Key": access_key,
       "Signature": signature,
       "Timestamp": str(timestamp_ms),
       "Content-Type": "application/json",
   }
   ```

## OpenAPI Endpoints Reference

| Endpoint Path | Purpose | Method | Notes |
| :--- | :--- | :--- | :--- |
| `/device/list` | Retrieve list of hub devices and child subdevices | GET | Requires empty params signature |
| `/device/data/latest/{device_id}` | Retrieve latest telemetry values for a device | GET | Returns dictionary of raw telemetry keys/values |
| `/device/datamap/{device_id}` | Retrieve telemetry metadata (units, names) | GET | Maps telemetry keys to unit tuples `(value, unit)` |

## Device & Subdevice Processing

Renogy structures devices in a hierarchy of top-level hubs and child subdevices:

1. **Hub / Parent Devices**:
   - Identified by `deviceId`, `name`, `mac`, `firmware`, `onlineStatus`, `connectType`, `sn`, `sku`.
   - Connection type resolved via `CONNECTION_TYPE`.
2. **Subdevices (`sublist`)**:
   - Nested inside parent hub record under `sublist`.
   - Identified with `parent` set to the hub's `deviceId`.
   - Connection type resolved via `SUBDEVICE_CONNECTION_TYPE`.
3. **Telemetry & Unit Mapping (`get_realtime_data`)**:
   - Fetches `/device/data/latest/{device_id}`.
   - If data exists, queries `/device/datamap/{device_id}` to resolve units.
   - Values in `data` dictionary are stored as tuples: `(value, unit)` (e.g. `(54.78, "%")` or `(-3, "°C")`).

## Exception Handling Conventions

| Exception | HTTP Status / Condition | Description |
| :--- | :--- | :--- |
| `UrlNotFound` | `404` | Requested endpoint not found |
| `NotAuthorized` | `401` | Invalid access key or signature verification failed |
| `RateLimit` | `429` | OpenAPI rate limit reached |
| `NoDevices` | Empty list (`[]`) | Account has no devices associated |
| `InvalidCall` | Client-side error | Missing or invalid required parameters |
| `TimeoutError` | Timeout | Handled gracefully in `process_request`, returns `{"error": ERROR_TIMEOUT}` |
