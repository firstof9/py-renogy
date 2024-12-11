"""Authentication handling."""

import base64
import hashlib
import hmac


def calc_sign(url, param_str, ts, secret_key) -> str:
    """Return hashed authorization token."""
    str_to_sign = f"{ts}.{url}.{param_str}".encode("utf-8")
    hmac_obj = hmac.new(secret_key.encode("utf-8"), str_to_sign, hashlib.sha256)
    return base64.b64encode(hmac_obj.digest()).decode("utf-8")
