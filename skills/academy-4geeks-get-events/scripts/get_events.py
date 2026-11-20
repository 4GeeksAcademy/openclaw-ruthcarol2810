#!/usr/bin/env python3
"""Fetch and safely project public upcoming events from the 4Geeks API."""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

API_URL = "https://breathecode.herokuapp.com/v1/events/all"
TIMEOUT_SECONDS = 20
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
LIMIT = 100
AI_TERMS = re.compile(
    r"(?<![\w])(?:ai|ia|artificial intelligence|inteligencia artificial|machine[ -]learning|aprendizaje autom[aá]tico)(?![\w])",
    re.IGNORECASE,
)


def _text(value: Any) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


def _timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except (ValueError, OverflowError):
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _event_type(item: dict[str, Any]) -> dict[str, str]:
    value = item.get("event_type")
    if not isinstance(value, dict):
        return {}
    result = {}
    for key in ("name", "slug"):
        text = _text(value.get(key))
        if text:
            result[key] = text
    return result


def _venue(item: dict[str, Any]) -> dict[str, str]:
    value = item.get("venue")
    if not isinstance(value, dict):
        return {}
    result = {}
    for key in ("title", "street_address", "city", "state"):
        text = _text(value.get(key))
        if text:
            result[key] = text
    return result


def _academy(item: dict[str, Any]) -> dict[str, str]:
    value = item.get("academy")
    if not isinstance(value, dict):
        return {}
    result = {}
    for key in ("name", "slug"):
        text = _text(value.get(key))
        if text:
            result[key] = text
    return result


def _searchable_text(value: Any) -> list[str]:
    """Extract meaningful words from string and structured API tag fields."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [
            value[key]
            for key in ("name", "slug", "title", "label")
            if isinstance(value.get(key), str)
        ]
    if isinstance(value, list):
        return [text for entry in value for text in _searchable_text(entry)]
    return []


def is_ai_related(item: dict[str, Any]) -> bool:
    """Heuristically detect explicit AI wording in observed public text fields."""
    event_type = item.get("event_type") if isinstance(item.get("event_type"), dict) else {}
    fields = [item.get(k) for k in ("title", "excerpt", "description", "tags")]
    fields.extend(event_type.get(k) for k in ("name", "slug", "technologies"))
    return any(
        AI_TERMS.search(text)
        for value in fields
        for text in _searchable_text(value)
    )


def project_event(item: dict[str, Any], now: datetime | None = None) -> dict[str, Any]:
    """Return only the public fields needed by the event skill."""
    if not isinstance(item, dict):
        raise ValueError("unexpected_event_record")
    title = _text(item.get("title"))
    if not title:
        raise ValueError("event_missing_title")
    start = _timestamp(item.get("starting_at"))
    end = _timestamp(item.get("ending_at"))
    if start and end and end <= start:
        raise ValueError("invalid_event_time_range")
    current = now or datetime.now(timezone.utc)
    current = current.astimezone(timezone.utc)
    result: dict[str, Any] = {
        "id": item.get("id") if isinstance(item.get("id"), (str, int)) else None,
        "title": title,
        "starting_at": start.isoformat().replace("+00:00", "Z") if start else None,
        "ending_at": end.isoformat().replace("+00:00", "Z") if end else None,
        "upcoming": bool(start and start > current),
        "has_valid_time_range": bool(start and end and end > start),
        "ai_related": is_ai_related(item),
        "online": item.get("online_event") if isinstance(item.get("online_event"), bool) else None,
    }
    for key in ("url", "excerpt"):
        text = _text(item.get(key))
        if text:
            result[key] = text
    description = _text(item.get("description"))
    if description:
        result["description"] = description[:2500]
    status = _text(item.get("status"))
    if status:
        result["status"] = status
    result["active"] = status.strip().upper() == "ACTIVE" if status else None
    event_type = _event_type(item)
    if event_type:
        result["event_type"] = event_type
    venue = _venue(item)
    if venue:
        result["venue"] = venue
    academy = _academy(item)
    if academy:
        result["academy"] = academy
    return result


def fetch_events(opener=None) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode({"upcoming": "true", "limit": LIMIT})
    request = urllib.request.Request(
        f"{API_URL}?{query}", headers={"Accept": "application/json"}, method="GET"
    )
    client = opener or urllib.request.build_opener(_NoRedirectHandler())
    try:
        with client.open(request, timeout=TIMEOUT_SECONDS) as response:
            if response.status != 200 or "json" not in response.headers.get("Content-Type", "").lower():
                raise RuntimeError("unexpected_http_response")
            body = response.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"http_{exc.code}") from None
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        raise RuntimeError("network_or_timeout") from None
    if len(body) > MAX_RESPONSE_BYTES:
        raise RuntimeError("response_too_large")
    try:
        payload = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        raise RuntimeError("invalid_json") from None
    # The live endpoint was observed to return a JSON array; do not guess at
    # pagination or silently interpret an undocumented wrapper.
    if not isinstance(payload, list) or any(not isinstance(row, dict) for row in payload):
        raise RuntimeError("unexpected_response_shape")
    try:
        projected = [project_event(row) for row in payload]
    except ValueError as exc:
        raise RuntimeError(str(exc)) from None
    # Event-specific pagination is not documented locally; fail rather than
    # present a possibly capped page as a complete list.
    if len(payload) >= LIMIT:
        raise RuntimeError("possibly_truncated_at_api_limit")
    # Preserve future items with incomplete metadata for the chat summary.
    # The skill separately blocks auto-scheduling unless active/time are valid.
    projected = [row for row in projected if row["upcoming"]]
    return sorted(
        projected,
        key=lambda row: row["starting_at"] or "9999-12-31T23:59:59Z",
    )


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def main() -> int:
    try:
        events = fetch_events()
    except RuntimeError as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}))
        return 1
    print(json.dumps({"status": "ok", "count": len(events), "events": events}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
