#!/usr/bin/env python3
"""Summarize the authenticated student's assigned 4Geeks tasks."""
from __future__ import annotations

import importlib.util
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

API_BASE = "https://breathecode.herokuapp.com"
TASKS_PATH = "/v1/assignment/user/me/task"
PAGE_SIZE = 100
MAX_PAGES = 30
MAX_RESPONSE_BYTES = 4 * 1024 * 1024
TIMEOUT_SECONDS = 20
AUTH_HELPER = (
    Path(__file__).resolve().parents[2]
    / "autentication-4geeks-academy"
    / "scripts"
    / "check_auth.py"
)


def load_auth_helper():
    spec = importlib.util.spec_from_file_location("fourgeeks_auth_helper", AUTH_HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError("auth_helper_unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Do not forward Authorization across redirects."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _get_json(offset: int, token: str) -> object:
    query = urllib.parse.urlencode({"limit": PAGE_SIZE, "offset": offset})
    request = urllib.request.Request(
        f"{API_BASE}{TASKS_PATH}?{query}",
        headers={"Authorization": "Token " + token, "Accept": "application/json"},
        method="GET",
    )
    opener = urllib.request.build_opener(_NoRedirectHandler())
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            if response.status != 200 or "json" not in response.headers.get("Content-Type", "").lower():
                raise RuntimeError("unexpected_http_response")
            body = response.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise RuntimeError("token_rejected") from None
        raise RuntimeError(f"http_{exc.code}") from None
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        raise RuntimeError("network_or_timeout") from None
    if len(body) > MAX_RESPONSE_BYTES:
        raise RuntimeError("response_too_large")
    try:
        return json.loads(body)
    except (ValueError, UnicodeDecodeError):
        raise RuntimeError("invalid_json") from None


def _next_offset(value: str, current: int, row_count: int) -> int:
    if not isinstance(value, str) or not value:
        raise RuntimeError("invalid_pagination")
    parsed = urllib.parse.urlsplit(urllib.parse.urljoin(API_BASE, value))
    if (
        parsed.scheme != "https"
        or parsed.netloc != "breathecode.herokuapp.com"
        or parsed.path != TASKS_PATH
        or parsed.fragment
    ):
        raise RuntimeError("invalid_pagination")
    try:
        query = urllib.parse.parse_qs(parsed.query, strict_parsing=True)
    except ValueError:
        raise RuntimeError("invalid_pagination") from None
    if set(query) != {"limit", "offset"}:
        raise RuntimeError("invalid_pagination")
    try:
        if any(len(query[key]) != 1 for key in ("limit", "offset")):
            raise RuntimeError("invalid_pagination")
        limit, next_offset = int(query["limit"][0]), int(query["offset"][0])
    except (KeyError, IndexError, TypeError, ValueError):
        raise RuntimeError("invalid_pagination") from None
    if limit != PAGE_SIZE or next_offset != current + row_count or next_offset <= current:
        raise RuntimeError("invalid_pagination")
    return next_offset


def _label(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, dict):
        for key in ("name", "slug"):
            label = value.get(key)
            if isinstance(label, str) and label.strip():
                return label.strip()
    return None


def _tally(rows: list[dict], key: str) -> dict[str, int]:
    counts = Counter()
    for row in rows:
        value = row.get(key)
        counts[value if isinstance(value, str) and value.strip() else "UNKNOWN"] += 1
    return dict(sorted(counts.items()))


def summarize(rows: list[dict]) -> dict:
    by_cohort: dict[str, Counter] = {}
    for row in rows:
        cohort = _label(row.get("cohort")) or "Sin cohorte informada"
        status = row.get("task_status")
        by_cohort.setdefault(cohort, Counter())[
            status if isinstance(status, str) and status.strip() else "UNKNOWN"
        ] += 1
    return {
        "total_assignments": len(rows),
        "counts_by_task_status": _tally(rows, "task_status"),
        "counts_by_revision_status": _tally(rows, "revision_status"),
        "counts_by_type": _tally(rows, "task_type"),
        "counts_by_cohort": {
            cohort: dict(sorted(counts.items()))
            for cohort, counts in sorted(by_cohort.items())
        },
    }


def _fetch_tasks(token: str) -> list[dict]:
    rows: list[dict] = []
    total = None
    offset = 0
    for _ in range(MAX_PAGES):
        payload = _get_json(offset, token)
        if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
            raise RuntimeError("unexpected_task_response")
        page = payload["results"]
        if any(not isinstance(row, dict) for row in page):
            raise RuntimeError("unexpected_task_record")
        rows.extend(page)
        count = payload.get("count")
        if count is not None:
            if not isinstance(count, int) or isinstance(count, bool) or count < 0:
                raise RuntimeError("invalid_pagination_count")
            if total is not None and total != count:
                raise RuntimeError("inconsistent_pagination_count")
            total = count
        if "next" in payload:
            next_page = payload["next"]
            if next_page is None:
                if total is not None and len(rows) != total:
                    raise RuntimeError("incomplete_pagination")
                return rows
            offset = _next_offset(next_page, offset, len(page))
            if total is not None and len(rows) >= total:
                raise RuntimeError("inconsistent_pagination")
            continue
        if not page or (total is not None and len(rows) >= total):
            if total is not None and len(rows) != total:
                raise RuntimeError("incomplete_pagination")
            return rows
        offset += len(page)
    raise RuntimeError("pagination_limit_exceeded")


def run() -> dict:
    auth = load_auth_helper()
    token = auth._token()
    if not token or "\r" in token or "\n" in token:
        raise RuntimeError("authentication_inconclusive")
    auth_status, _ = auth.check_auth(token)
    if auth_status != "authenticated":
        raise RuntimeError("authentication_" + auth_status)

    rows = _fetch_tasks(token)
    return {
        "status": "ok",
        "as_of_venezuela": datetime.now(ZoneInfo("America/Caracas")).isoformat(timespec="minutes"),
        "metric_note": (
            "Este es un conteo de asignaciones visibles para el estudiante; no es el porcentaje "
            "oficial de avance del curso. La referencia no define el total curricular ni una fórmula oficial."
        ),
        **summarize(rows),
    }


def main() -> int:
    try:
        result = run()
    except RuntimeError as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
