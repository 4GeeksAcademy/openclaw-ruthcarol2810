#!/usr/bin/env python3
"""Check a 4Geeks student token without printing it or user data."""
from __future__ import annotations

import json
import os
import stat
import sys
import urllib.error
import urllib.request
from pathlib import Path

TOKEN_ENV = "TOKEN_4GEEKS"
API_URL = "https://breathecode.herokuapp.com/v1/admissions/user/me"
TIMEOUT_SECONDS = 15
MAX_RESPONSE_BYTES = 1024 * 1024


def emit(status: str, reason: str | None = None) -> None:
    result = {"status": status}
    if reason:
        result["reason"] = reason
    print(json.dumps(result, ensure_ascii=False))


def _workspace_env_path() -> Path:
    # This skill lives at <OpenClaw-root>/workspace/skills/<skill>/scripts/.
    return Path(__file__).resolve().parents[4] / ".env"


def _read_token_from_private_env(path: Path) -> str | None:
    """Read only TOKEN_4GEEKS from a private regular file; never source the file."""
    try:
        if path.is_symlink() or not path.is_file():
            return None
        info = path.stat()
        if stat.S_IMODE(info.st_mode) & 0o077:
            return None
        for line in path.read_text(encoding="utf-8").splitlines():
            candidate = line.strip()
            if candidate.startswith("export "):
                candidate = candidate[7:].lstrip()
            key, separator, value = candidate.partition("=")
            if separator and key.strip() == TOKEN_ENV:
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '\"'):
                    value = value[1:-1]
                return value if value.strip() else None
    except (OSError, UnicodeError):
        return None
    return None


def _token() -> str | None:
    value = os.environ.get(TOKEN_ENV)
    if value and value.strip():
        return value
    return _read_token_from_private_env(_workspace_env_path())


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Reject redirects so the authorization header is never forwarded."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def check_auth(token: str) -> tuple[str, str | None]:
    request = urllib.request.Request(
        API_URL,
        headers={"Authorization": "Token " + token, "Accept": "application/json"},
        method="GET",
    )
    opener = urllib.request.build_opener(_NoRedirectHandler())
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            status_code = response.status
            content_type = response.headers.get("Content-Type", "")
            body = response.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as error:
        status_code = error.code
        content_type = error.headers.get("Content-Type", "") if error.headers else ""
        body = b""
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, UnicodeError):
        return "inconclusive", "network_or_timeout"

    if status_code in (401, 403):
        return "rejected", "unauthorized"
    if status_code < 200 or status_code >= 300:
        return "inconclusive", "redirect_or_http_" + str(status_code)
    if len(body) > MAX_RESPONSE_BYTES:
        return "inconclusive", "response_too_large"
    if "json" not in content_type.lower():
        return "inconclusive", "unexpected_content_type"
    try:
        payload = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        return "inconclusive", "invalid_json"
    if not isinstance(payload, dict):
        return "inconclusive", "unexpected_response_shape"
    return "authenticated", None


def main() -> int:
    token = _token()
    if not token:
        emit("inconclusive", "missing_or_insecure_TOKEN_4GEEKS")
        return 2
    if "\r" in token or "\n" in token:
        emit("inconclusive", "invalid_token_format")
        return 2

    status, reason = check_auth(token)
    emit(status, reason)
    return {"authenticated": 0, "rejected": 1, "inconclusive": 2}[status]


if __name__ == "__main__":
    sys.exit(main())
