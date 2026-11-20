#!/usr/bin/env python3
"""Resolve a public 4Geeks technology and fetch matching registry assets."""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

API_BASE = "https://breathecode.herokuapp.com"
ASSET_PATH = "/v1/registry/asset"
TECH_PATH = "/v1/registry/technology"
PAGE_SIZE = 100
MAX_PAGES = 50
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
TIMEOUT_SECONDS = 20


def _text(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _technology_terms(value: Any) -> list[dict[str, str]]:
    """Normalize either observed slug strings or detailed technology objects."""
    if not isinstance(value, list):
        return []
    out = []
    for item in value:
        if isinstance(item, str) and item.strip():
            out.append({"slug": item.strip(), "title": item.strip()})
        elif isinstance(item, dict):
            slug, title = _text(item.get("slug")), _text(item.get("title"))
            if slug:
                out.append({"slug": slug, "title": title or slug})
    return out


def _get_json(url: str, opener=None) -> Any:
    request = urllib.request.Request(url, headers={"Accept": "application/json"}, method="GET")
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
        return json.loads(body)
    except (ValueError, UnicodeDecodeError):
        raise RuntimeError("invalid_json") from None


def _validate_page_url(value: Any, path: str, expected_params: dict[str, str], current_offset: int) -> tuple[int, str]:
    if not isinstance(value, str) or not value:
        raise RuntimeError("invalid_pagination")
    parsed = urllib.parse.urlsplit(urllib.parse.urljoin(API_BASE, value))
    if parsed.scheme != "https" or parsed.netloc != "breathecode.herokuapp.com" or parsed.path != path or parsed.fragment:
        raise RuntimeError("invalid_pagination")
    try:
        query = urllib.parse.parse_qs(parsed.query, strict_parsing=True)
    except ValueError:
        raise RuntimeError("invalid_pagination") from None
    if any(len(values) != 1 for values in query.values()):
        raise RuntimeError("invalid_pagination")
    if set(query) != set(expected_params) | {"offset", "limit"}:
        raise RuntimeError("invalid_pagination")
    for key, expected in expected_params.items():
        if query.get(key) != [expected]:
            raise RuntimeError("invalid_pagination")
    try:
        offset = int(query["offset"][0])
        limit = int(query["limit"][0])
    except (KeyError, IndexError, TypeError, ValueError):
        raise RuntimeError("invalid_pagination") from None
    if limit != PAGE_SIZE or offset <= current_offset:
        raise RuntimeError("invalid_pagination")
    return offset, urllib.parse.urlunsplit(parsed)


def _fetch_collection(path: str, filters: dict[str, str], opener=None) -> list[dict[str, Any]]:
    params = {**filters, "limit": str(PAGE_SIZE), "offset": "0"}
    url = f"{API_BASE}{path}?{urllib.parse.urlencode(params)}"
    total: int | None = None
    rows_all: list[dict[str, Any]] = []
    offset = 0
    for _ in range(MAX_PAGES):
        payload = _get_json(url, opener=opener)
        if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
            raise RuntimeError("unexpected_collection_response")
        rows = payload["results"]
        count = payload.get("count")
        if not isinstance(count, int) or count < 0:
            raise RuntimeError("invalid_collection_count")
        if total is not None and total != count:
            raise RuntimeError("inconsistent_pagination_count")
        total = count
        if any(not isinstance(row, dict) for row in rows):
            raise RuntimeError("unexpected_collection_record")
        rows_all.extend(rows)
        next_url = payload.get("next")
        if next_url is None:
            if len(rows_all) != total:
                raise RuntimeError("incomplete_pagination")
            return rows_all
        next_offset, url = _validate_page_url(next_url, path, filters, offset)
        if next_offset != offset + len(rows) or not rows or len(rows_all) >= total:
            raise RuntimeError("invalid_pagination")
        offset = next_offset
    raise RuntimeError("pagination_limit_exceeded")


def resolve_technology(query: str, opener=None) -> dict[str, Any]:
    query = _text(query) or ""
    if not query or len(query) > 100:
        raise RuntimeError("invalid_technology_query")
    rows = _fetch_collection(TECH_PATH, {"like": query}, opener=opener)
    candidates = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        slug, title = _text(row.get("slug")), _text(row.get("title"))
        if not slug:
            continue
        candidates.append({
            "slug": slug,
            "title": title or slug,
            "visibility": row.get("visibility") if isinstance(row.get("visibility"), str) else None,
            "is_deprecated": row.get("is_deprecated") if isinstance(row.get("is_deprecated"), bool) else None,
        })
    normalized = query.casefold().strip()
    exact = [c for c in candidates if c["slug"].casefold() == normalized or c["title"].casefold() == normalized]
    public = [c for c in candidates if c.get("visibility") == "PUBLIC" and c.get("is_deprecated") is not True]
    if len(exact) == 1:
        chosen = exact[0]
    elif len(exact) > 1:
        return {"status": "needs_selection", "query": query, "candidates": exact}
    elif len(public) == 1:
        chosen = public[0]
    elif not candidates:
        return {"status": "not_found", "query": query, "candidates": []}
    else:
        return {"status": "needs_selection", "query": query, "candidates": public or candidates[:25]}
    if chosen.get("visibility") != "PUBLIC" or chosen.get("is_deprecated") is True:
        return {"status": "not_available", "query": query, "candidates": [chosen]}
    return {"status": "ok", "technology": chosen}


def _project_asset(item: Any, target_slug: str) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise RuntimeError("unexpected_asset_record")
    slug, title = _text(item.get("slug")), _text(item.get("title"))
    if not slug or not title:
        raise RuntimeError("asset_missing_identity")
    technologies = _technology_terms(item.get("technologies"))
    # The endpoint has an observed filter, but verify each result against the
    # exact canonical slug to avoid relying on fuzzy API matching.
    if target_slug.casefold() not in {t["slug"].casefold() for t in technologies}:
        raise RuntimeError("technology_filter_mismatch")
    category = item.get("category") if isinstance(item.get("category"), dict) else {}
    result: dict[str, Any] = {
        "slug": slug,
        "title": title,
        "asset_type": _text(item.get("asset_type")) or "UNKNOWN",
        "lang": _text(item.get("lang")),
        "description": _text(item.get("description")),
        "difficulty": _text(item.get("difficulty")),
        "duration": item.get("duration") if isinstance(item.get("duration"), (int, float)) else None,
        "status": _text(item.get("status")),
        "visibility": _text(item.get("visibility")),
        "technologies": technologies,
        "url": _text(item.get("url")),
        "readme_url": _text(item.get("readme_url")),
        "preview": _text(item.get("preview")),
        "category": {k: _text(category.get(k)) for k in ("title", "slug") if _text(category.get(k))},
        "graded": item.get("graded") if isinstance(item.get("graded"), bool) else None,
        "interactive": item.get("interactive") if isinstance(item.get("interactive"), bool) else None,
        "with_solutions": item.get("with_solutions") if isinstance(item.get("with_solutions"), bool) else None,
        "with_video": item.get("with_video") if isinstance(item.get("with_video"), bool) else None,
    }
    translations = item.get("translations")
    if isinstance(translations, dict):
        result["translations"] = {str(k): v for k, v in translations.items() if isinstance(k, str) and isinstance(v, str)}
    # Strip absent/null values for a concise, safe transport shape.
    return {k: v for k, v in result.items() if v is not None and v != {} and v != []}


def fetch_assets(technology_slug: str, opener=None) -> tuple[int, list[dict[str, Any]]]:
    rows = _fetch_collection(ASSET_PATH, {"technologies": technology_slug}, opener=opener)
    assets = [_project_asset(row, technology_slug) for row in rows]
    return len(assets), assets


def run(query: str, opener=None) -> dict[str, Any]:
    resolved = resolve_technology(query, opener=opener)
    if resolved["status"] != "ok":
        return resolved
    tech = resolved["technology"]
    count, assets = fetch_assets(tech["slug"], opener=opener)
    return {
        "status": "ok",
        "query": query,
        "technology": tech,
        "count": count,
        "assets": assets,
        "asset_types": dict(sorted({key: sum(1 for a in assets if a["asset_type"] == key) for key in {a["asset_type"] for a in assets}}.items())),
    }


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Reject redirects on public API requests."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"status": "error", "reason": "usage: get_assets.py <technology>"}))
        return 2
    try:
        result = run(sys.argv[1])
    except RuntimeError as exc:
        result = {"status": "error", "reason": str(exc)}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] in ("ok", "needs_selection", "not_found", "not_available") else 1


if __name__ == "__main__":
    sys.exit(main())
