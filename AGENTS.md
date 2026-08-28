# AGENTS.md

A short orientation for AI coding agents (Claude, Codex, Copilot, Antigravity, etc.) working in this repo.

## What this repo is

`py-renogy` is an asynchronous Python library wrapping the Renogy OpenAPI (`https://openapi.renogy.com`). It is used by [ha-renogy](https://github.com/firstof9/ha-renogy) and standalone consumers to discover and monitor Renogy smart solar hubs, batteries, inverters, and subdevices.

```
py-renogy/
├── renogyapi/
│   ├── __init__.py      # Renogy client class, session handling, device processing
│   ├── auth.py          # HMAC-SHA256 signature calculation (calc_sign)
│   └── exceptions.py    # UrlNotFound, NotAuthorized, RateLimit, InvalidCall, NoDevices
├── tests/
│   ├── fixtures/        # Mock OpenAPI JSON payloads (device_list, realtime_data, datamap)
│   ├── common.py        # Fixture loader helper (load_fixture)
│   ├── conftest.py      # mock_aioclient fixture for intercepting aiohttp requests
│   └── test_main.py     # Unit test suite
└── .agents/
    └── skills/          # Domain skills (renogy-api-guide, renogy-testing-guide)
```

## Environment & Toolchain

- **Python**: `>=3.10` (tested across 3.10, 3.11, 3.12, 3.13, 3.14).
- **Package Manager & Test Runner**: `uv` and `tox` with `tox-uv`.
- **Linting & Formatting**: `ruff` configured in `pyproject.toml`.
- **Type Checking**: `mypy` running with `tox -e mypy`.
- **Testing**: `pytest` + `pytest-asyncio` + `mock_aioclient`.

```bash
# Run test suite across all environments
uv run --with tox-uv tox

# Run linting and type checking
uv run --with tox-uv tox -e lint
uv run --with tox-uv tox -e mypy

# Run ruff check and format directly
uv run ruff check .
uv run ruff format .
```

## Architecture & Important Conventions

### 1. Authentication & Signature Generation

Every OpenAPI request requires an HMAC-SHA256 signature generated with `calc_sign(path, param_str, timestamp, secret_key)`:

- **Signed message format**: `"{timestamp}.{path}.{param_str}"`
- **Output**: Base64-encoded HMAC-SHA256 digest.
- **Required Headers**: `Access-Key`, `Signature`, `Timestamp`, `Content-Type: application/json`.

### 2. Session Management

The `Renogy` class supports both standalone mode and external `aiohttp.ClientSession` dependency injection:

```python
# Standalone internal session per request
client = Renogy(secret_key="...", access_key="...")

# Reused external session (preferred for Home Assistant integrations)
client = Renogy(secret_key="...", access_key="...", session=session)
```

### 3. Device Hierarchy & Telemetry

- **Top-Level Hubs**: Returned directly from `/device/list`. Connection type is resolved from `CONNECTION_TYPE`.
- **Child Subdevices**: Located in `response["sublist"]`. Child entries have `parent` set to the hub's `deviceId`, with connection type resolved from `SUBDEVICE_CONNECTION_TYPE`.
- **Unit Pairing**: Realtime metrics fetched from `/device/data/latest/{device_id}` are correlated with units from `/device/datamap/{device_id}` and returned as tuples: `(value, unit)` (e.g. `(54.78, "%")`).

### 4. Error Handling

- **HTTP Status Codes**:
  - `404` -> raises `UrlNotFound`
  - `401` -> raises `NotAuthorized`
  - `429` -> raises `RateLimit`
  - Non-200 with JSON/text -> returns `{"error": ...}` envelope
- **Network / Timeout**:
  - `TimeoutError` / `ServerTimeoutError` -> returns `{"error": "Timeout while updating"}`
- **Device Discovery**:
  - Empty device response -> raises `NoDevices`

## Specialized Agent Skills

Check `.agents/skills/` for detailed procedural guides:
- [renogy-api-guide](.agents/skills/renogy-api-guide/SKILL.md): Comprehensive API architecture, signing, and data processing.
- [renogy-testing-guide](.agents/skills/renogy-testing-guide/SKILL.md): Test patterns, `mock_aioclient` recipes, and fixture usage.
