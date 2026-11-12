#!/usr/bin/env python3
"""Fetch only assigned 4Geeks projects after validating the existing student token."""
from __future__ import annotations

import importlib.util
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_BASE = "https://breathecode.herokuapp.com"
TASKS_PATH = "/v1/assignment/user/me/task"
PAGE_SIZE = 100
MAX_PAGES = 20
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


def fetch_page(token: str, offset: int) -> dict:
    query = urllib.parse.urlencode(
        {"task_type": "PROJECT", "limit": PAGE_SIZE, "offset": offset}
    )
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
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        raise RuntimeError("network_or_timeout") from None
    if len(body) > MAX_RESPONSE_BYTES:
        raise RuntimeError("response_too_large")
    try:
        payload = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        raise RuntimeError("invalid_json") from None
    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise RuntimeError("unexpected_response_shape")
    return payload


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Never forward an Authorization header across a redirect."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _cohort_name(value) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("name", "slug", "title"):
            if isinstance(value.get(key), str):
                return value[key]
    return None


def _status(task_status, revision_status) -> str:
    task = task_status if isinstance(task_status, str) else "UNKNOWN"
    revision = revision_status if isinstance(revision_status, str) else ""
    if task == "PENDING":
        return "Pendiente"
    if task == "DONE":
        if revision == "APPROVED":
            return "Calificado: aprobado"
        if revision == "REJECTED":
            return "Calificado: requiere correcciones"
        return "Entregado"
    if task == "APPROVED":
        return "Calificado: aprobado"
    if task == "REJECTED":
        return "Calificado: requiere correcciones"
    return task


def _project(item: dict) -> dict:
    task_status = item.get("task_status")
    revision_status = item.get("revision_status")
    result = {
        "title": item.get("title") if isinstance(item.get("title"), str) else "(sin título)",
        "status": _status(task_status, revision_status),
        "task_status": task_status,
    }
    if revision_status is not None:
        result["revision_status"] = revision_status
    cohort = _cohort_name(item.get("cohort"))
    if cohort:
        result["cohort"] = cohort
    for key in ("created_at", "updated_at", "delivered_at", "reviewed_at"):
        value = item.get(key)
        if isinstance(value, str):
            result[key] = value
    return result


def _next_page_offset(value: str, current_offset: int, row_count: int) -> int:
    """Validate a server-provided next URL and return its offset only."""
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
    query = urllib.parse.parse_qs(parsed.query, strict_parsing=True)
    if set(query) != {"task_type", "limit", "offset"}:
        raise RuntimeError("invalid_pagination")
    try:
        if any(len(query[key]) != 1 for key in ("task_type", "limit", "offset")):
            raise RuntimeError("invalid_pagination")
        task_type = query["task_type"]
        limit, next_offset = int(query["limit"][0]), int(query["offset"][0])
    except (KeyError, IndexError, TypeError, ValueError):
        raise RuntimeError("invalid_pagination") from None
    if (
        task_type != ["PROJECT"]
        or limit != PAGE_SIZE
        or next_offset != current_offset + row_count
        or next_offset <= current_offset
    ):
        raise RuntimeError("invalid_pagination")
    return next_offset


def run() -> tuple[int, list[dict]]:
    auth = load_auth_helper()
    token = auth._token()
    if not token or "\r" in token or "\n" in token:
        raise RuntimeError("authentication_inconclusive")
    auth_status, _ = auth.check_auth(token)
    if auth_status != "authenticated":
        raise RuntimeError("authentication_" + auth_status)

    projects: list[dict] = []
    total = None
    offset = 0
    for _ in range(MAX_PAGES):
        payload = fetch_page(token, offset)
        rows = payload["results"]
        if any(not isinstance(row, dict) or row.get("task_type") != "PROJECT" for row in rows):
            raise RuntimeError("unexpected_project_record")
        projects.extend(_project(row) for row in rows)
        count = payload.get("count")
        if isinstance(count, int) and count >= 0:
            if total is not None and total != count:
                raise RuntimeError("inconsistent_pagination_count")
            total = count
        if "next" in payload:
            next_page = payload["next"]
            if next_page is None:
                if total is not None and len(projects) != total:
                    raise RuntimeError("incomplete_pagination")
                return (total if total is not None else len(projects)), projects
            offset = _next_page_offset(next_page, offset, len(rows))
            if total is not None and len(projects) >= total:
                raise RuntimeError("inconsistent_pagination")
            continue
        if not rows or (total is not None and len(projects) >= total):
            if total is not None and len(projects) != total:
                raise RuntimeError("incomplete_pagination")
            return (total if total is not None else len(projects)), projects
        offset += len(rows)
    raise RuntimeError("pagination_limit_exceeded")


def main() -> int:
    try:
        count, projects = run()
    except RuntimeError as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}))
        return 1
    print(json.dumps({"status": "ok", "count": count, "projects": projects}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
