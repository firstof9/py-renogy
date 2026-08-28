---
name: renogy-testing-guide
description: >-
  Use this skill when writing, debugging, or running tests for py-renogy, including
  aiohttp mocking with mock_aioclient, test fixtures, tox environments, ruff linting,
  and mypy type checking.
---

# Renogy Testing & Quality Assurance Guide

This skill provides guidelines and patterns for testing and maintaining code quality in `py-renogy`.

## Test Execution with `uv` and `tox`

Run the full test and lint suite across Python environments using `uv` and `tox`:

```bash
# Run all configured tox environments
uv run --with tox-uv tox

# Run tests for a specific Python version (e.g. Python 3.13 or 3.14)
uv run --with tox-uv tox -e py313
uv run --with tox-uv tox -e py314

# Run linting and formatting checks
uv run --with tox-uv tox -e lint

# Run type checking with mypy
uv run --with tox-uv tox -e mypy
```

## Mocking HTTP Requests (`mock_aioclient`)

The test suite uses the `mock_aioclient` fixture to intercept `aiohttp.ClientSession` HTTP requests without making actual network calls.

### Mocking Successful Responses

```python
from tests.common import load_fixture


async def test_endpoint(mock_aioclient):
    # Queue a mocked GET response
    mock_aioclient.get(
        "https://openapi.renogy.com/device/list",
        status=200,
        body=load_fixture("device_list.json"),
        repeat=True,  # Set repeat=True if called multiple times in one test
    )

    client = renogyapi.Renogy(secret_key="fakeSecret", access_key="fakeAccess")
    devices = await client.get_devices()
    assert len(devices) > 0
```

### Mocking Errors and Exceptions

```python
from aiohttp.client_exceptions import ServerTimeoutError
from renogyapi.exceptions import NotAuthorized, UrlNotFound


async def test_errors(mock_aioclient):
    # Status error
    mock_aioclient.get("https://openapi.renogy.com/401", status=401)

    # Exception simulation (timeout)
    mock_aioclient.get(
        "https://openapi.renogy.com/timeout",
        exception=ServerTimeoutError(),
    )
```

## Test Fixtures (`tests/fixtures/`)

JSON payload fixtures represent actual Renogy OpenAPI response structures:

- **`device_list.json`**: Sample hub devices and nested subdevices.
- **`device_list_error.json`**: Hub device with empty/missing subdevices list.
- **`realtime_data.json`**: Telemetry payload containing sensor keys (e.g. `batteryLevel`, `heatingModeStatus`, `averageTemperature`).
- **`datamap.json`**: Measurement unit definitions mapped to telemetry metric keys.

Load fixtures in tests using `load_fixture(filename)`.

## Code Style & Formatting (`ruff`)

The codebase adheres to Ruff formatting and linting rules:

```bash
# Check code style and lint rules
uv run ruff check .

# Automatically apply safe fixes
uv run ruff check --fix .

# Verify code formatting
uv run ruff format --check .

# Format code
uv run ruff format .
```
