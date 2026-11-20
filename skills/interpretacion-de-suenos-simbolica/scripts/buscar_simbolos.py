#!/usr/bin/env python3
"""Fetch short, attributed dream-symbol excerpts from the configured public sites."""
from __future__ import annotations

import argparse
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

SKILL_DIR = Path(__file__).resolve().parents[1]
CACHE_FILE = Path.home() / ".cache" / "openclaw" / "dream-symbols" / "cache.json"
CACHE_SECONDS = 7 * 24 * 60 * 60
TIMEOUT_SECONDS = 18
MAX_BYTES = 1_000_000
MAX_EXCERPT = 500
USER_AGENT = "Mozilla/5.0 (compatible; NucitaDreamSymbols/1.0)"


class _SameHostRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        old, new = urllib.parse.urlsplit(req.full_url), urllib.parse.urlsplit(newurl)
        if new.scheme != "https" or new.hostname != old.hostname:
            return None
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class _TextBlocks(HTMLParser):
    """Small stdlib-only extractor for headings, paragraphs and bold labels."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks: list[dict[str, Any]] = []
        self.current: dict[str, Any] | None = None
        self.in_bold = False

    def handle_starttag(self, tag, attrs):
        if tag in ("p", "h1", "h2", "h3", "h4", "li"):
            self._finish()
            self.current = {"tag": tag, "text": [], "bold": []}
        elif tag in ("b", "strong") and self.current is not None:
            self.in_bold = True
        elif tag == "br" and self.current is not None:
            self.current["text"].append(" ")

    def handle_endtag(self, tag):
        if tag in ("b", "strong"):
            self.in_bold = False
        if tag in ("p", "h1", "h2", "h3", "h4", "li"):
            self._finish()

    def handle_data(self, data):
        if self.current is None:
            return
        self.current["text"].append(data)
        if self.in_bold:
            self.current["bold"].append(data)

    def _finish(self):
        if self.current is not None:
            text = " ".join(" ".join(self.current["text"]).split())
            bold = " ".join(" ".join(self.current["bold"]).split())
            if text:
                self.blocks.append({"tag": self.current["tag"], "text": text, "bold": bold})
        self.current = None
        self.in_bold = False

    def close(self):
        super().close()
        self._finish()


def _normal(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def _fetch(url: str) -> tuple[int, str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"})
    opener = urllib.request.build_opener(_SameHostRedirect())
    try:
        with opener.open(req, timeout=TIMEOUT_SECONDS) as response:
            content_type = response.headers.get("Content-Type", "").lower()
            if response.status != 200 or "html" not in content_type:
                raise RuntimeError("unexpected_http_response")
            body = response.read(MAX_BYTES + 1)
            final_url = response.geturl()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"http_{exc.code}") from None
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        raise RuntimeError("network_or_timeout") from None
    if len(body) > MAX_BYTES:
        raise RuntimeError("page_too_large")
    parsed = urllib.parse.urlsplit(final_url)
    if parsed.scheme != "https" or parsed.hostname != urllib.parse.urlsplit(url).hostname:
        raise RuntimeError("unexpected_final_host")
    return response.status, body.decode("utf-8", "replace"), final_url


def _dreambible_url(symbol: str) -> str:
    return "https://www.dreambible.com/search.php?" + urllib.parse.urlencode({"q": symbol})


def _auntyflo_url(symbol: str) -> str:
    slug = "-".join(_normal(symbol).split())
    return f"https://www.auntyflo.com/dream-dictionary/{urllib.parse.quote(slug, safe='-')}"


def _extract_dreambible(symbol: str, source: str) -> dict[str, Any]:
    parser = _TextBlocks()
    parser.feed(source)
    query = _normal(symbol)
    blocks = parser.blocks
    matches = []
    for index, block in enumerate(blocks):
        if block["tag"] != "p" or not block["bold"]:
            continue
        label = _normal(block["bold"])
        # Dream Bible uses separate paragraphs for the bold entry heading and its definition.
        same_entry = label == query or label == query + "s" or (query.endswith("s") and label == query[:-1])
        if same_entry:
            next_block = blocks[index + 1] if index + 1 < len(blocks) else None
            if next_block and next_block["tag"] == "p" and not next_block["bold"]:
                matches.append(next_block)
    if not matches:
        return {"status": "not_found", "url": _dreambible_url(symbol), "reason": "exact_symbol_entry_not_found"}
    excerpt = html.unescape(matches[0]["text"]).strip()
    return {"status": "ok", "url": _dreambible_url(symbol), "excerpt": excerpt[:MAX_EXCERPT]}


def _extract_auntyflo(symbol: str, source: str, final_url: str) -> dict[str, Any]:
    parser = _TextBlocks()
    parser.feed(source)
    query = _normal(symbol)
    # Only accept the actual article h1, not a loose mention in navigation or body text.
    headings = [_normal(b["text"]) for b in parser.blocks if b["tag"] == "h1"]
    if not any(query in heading for heading in headings):
        return {"status": "not_found", "url": final_url, "reason": "exact_symbol_entry_not_found"}
    candidates = []
    for block in parser.blocks:
        if block["tag"] == "p" and len(block["text"]) >= 80:
            text = block["text"]
            if any(phrase in text.casefold() for phrase in ("auntyflo", "legal disclaimer", "copyright", "about the author")):
                continue
            candidates.append(text)
        if len(candidates) == 3:
            break
    if not candidates:
        return {"status": "not_found", "url": final_url, "reason": "no_article_excerpt"}
    excerpt = " ".join(candidates)
    return {"status": "ok", "url": final_url, "excerpt": html.unescape(excerpt)[:MAX_EXCERPT]}


def _load_cache() -> dict[str, Any]:
    try:
        data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError, TypeError):
        return {}


def _save_cache(cache: dict[str, Any]) -> None:
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        try:
            os.chmod(CACHE_FILE.parent, 0o700)
        except OSError:
            pass
        tmp = CACHE_FILE.with_suffix(CACHE_FILE.suffix + ".tmp")
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, separators=(",", ":"))
        os.replace(tmp, CACHE_FILE)
        os.chmod(CACHE_FILE, 0o600)
    except OSError as exc:
        sys.stderr.write(f"cache_write_failed:{type(exc).__name__}\n")


def _cached(cache: dict[str, Any], key: str, now: float) -> dict[str, Any] | None:
    item = cache.get(key)
    if not isinstance(item, dict) or not isinstance(item.get("timestamp"), (int, float)):
        return None
    if now - item["timestamp"] >= CACHE_SECONDS or not isinstance(item.get("data"), dict):
        return None
    data = item["data"]
    if data.get("status") != "ok" or not isinstance(data.get("excerpt"), str) or not data["excerpt"].strip():
        return None
    return data


def _lookup(portal: str, symbol: str, cache: dict[str, Any], now: float) -> dict[str, Any]:
    key = f"{portal}:{_normal(symbol)}"
    cached = _cached(cache, key, now)
    if cached is not None:
        return {**cached, "cached": True}
    if portal == "Dream Bible":
        url = _dreambible_url(symbol)
        extract = lambda source, final: _extract_dreambible(symbol, source)
    else:
        url = _auntyflo_url(symbol)
        extract = lambda source, final: _extract_auntyflo(symbol, source, final)
    try:
        _, source, final_url = _fetch(url)
        result = extract(source, final_url)
    except RuntimeError as exc:
        result = {"status": "unavailable", "url": url, "reason": str(exc)}
    if result.get("status") == "ok" and isinstance(result.get("excerpt"), str) and result["excerpt"].strip():
        cache[key] = {"timestamp": now, "data": result}
    return result


def run(symbols: list[str], compare: bool = False, now: float | None = None) -> dict[str, Any]:
    cleaned = []
    for symbol in symbols:
        symbol = " ".join(symbol.split())
        if symbol and len(symbol) <= 80 and symbol not in cleaned:
            cleaned.append(symbol)
    if not cleaned:
        raise ValueError("No se proporcionaron símbolos válidos")
    if len(cleaned) > 5:
        raise ValueError("Se permiten como máximo 5 símbolos por consulta")
    cache = _load_cache()
    current = time.time() if now is None else now
    output: dict[str, Any] = {}
    for symbol in cleaned:
        output[symbol] = {
            "Dream Bible": _lookup("Dream Bible", symbol, cache, current),
            "AuntyFlo": _lookup("AuntyFlo", symbol, cache, current),
            # dreambook.es is intentionally not fetched: DNS for the supplied domain
            # failed during live checks, and no replacement URL has been confirmed.
            "Dream Book": {"status": "unavailable", "url": "https://www.dreambook.es/", "reason": "domain_dns_unavailable_confirm_replacement"},
        }
    _save_cache(cache)
    result: dict[str, Any] = {"status": "ok", "simbolos": output}
    if compare:
        result["comparacion"] = "Contrasta creativamente los extractos disponibles; no se afirma que las fuentes coincidan ni se asigna un significado objetivo."
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("simbolos", nargs="+", help="Hasta cinco símbolos o expresiones breves")
    parser.add_argument("--comparar", action="store_true", help="Solicita una comparación creativa, no factual, entre extractos")
    args = parser.parse_args()
    try:
        result = run(args.simbolos, compare=args.comparar)
    except ValueError as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
