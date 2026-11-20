#!/usr/bin/env python3
"""Private opt-in dream-symbol journal; stores titles and symbols only."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

DEFAULT_DIR = Path.home() / ".local" / "share" / "openclaw" / "dream-journal"
REGISTRO_FILE = Path(os.environ.get("OPENCLAW_DREAM_LOG", DEFAULT_DIR / "historial_suenos.json")).expanduser()
UMBRAL_TENDENCIAS = 2
VALID_TYPES = {"propio", "tercero", "parcial"}


def cargar_historial() -> list[dict]:
    if not REGISTRO_FILE.exists():
        return []
    try:
        data = json.loads(REGISTRO_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RuntimeError("journal_unreadable_or_invalid_json") from exc
    if not isinstance(data, list) or any(not isinstance(row, dict) for row in data):
        raise RuntimeError("journal_invalid_structure")
    return data


def guardar_historial(historial: list[dict]) -> None:
    REGISTRO_FILE.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        os.chmod(REGISTRO_FILE.parent, 0o700)
    except OSError:
        pass
    tmp = REGISTRO_FILE.with_name(REGISTRO_FILE.name + ".tmp")
    try:
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(historial, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, REGISTRO_FILE)
        os.chmod(REGISTRO_FILE, 0o600)
    except OSError as exc:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        raise RuntimeError("journal_write_failed") from exc


def _symbol_list(raw: str) -> list[str]:
    return list(dict.fromkeys(s.strip().casefold() for s in raw.split(",") if s.strip()))


def add_entry(title: str, symbols_raw: str, kind: str, confirmed: bool) -> dict:
    if not confirmed:
        raise ValueError("explicit_consent_required_use_--confirmar")
    if kind not in VALID_TYPES:
        raise ValueError("invalid_entry_type")
    symbols = _symbol_list(symbols_raw)
    if not symbols:
        raise ValueError("at_least_one_symbol_required")
    # Record no dream narrative, identity or names: only a short title, symbols, type, timestamp.
    entry = {
        "fecha": datetime.now(ZoneInfo("America/Caracas")).isoformat(timespec="seconds"),
        "titulo": " ".join(title.split())[:120] or "Sueño sin título",
        "simbolos": symbols,
        "tipo": kind,
    }
    history = cargar_historial()
    history.append(entry)
    guardar_historial(history)
    return {"status": "success", "mensaje": "Registro simbólico guardado en el diario local privado.", "simbolos_guardados": len(symbols)}


def trends() -> dict:
    history = cargar_historial()
    own = [row for row in history if row.get("tipo", "propio") in ("propio", "parcial")]
    counts: dict[str, int] = {}
    # A symbol counts at most once per record; recurrence means distinct dream entries.
    for row in own:
        symbols = row.get("simbolos", [])
        if not isinstance(symbols, list):
            continue
        for symbol in set(s.casefold() for s in symbols if isinstance(s, str) and s.strip()):
            counts[symbol] = counts.get(symbol, 0) + 1
    recurring = {symbol: count for symbol, count in sorted(counts.items()) if count >= UMBRAL_TENDENCIAS}
    return {
        "umbral_cumplido": bool(recurring),
        "total_suenos_registrados": len(own),
        "simbolos_recurrentes": recurring,
        "hilos_detectados": [f"El símbolo '{symbol}' aparece en {count} relatos distintos." for symbol, count in recurring.items()],
        "criterio": "Cada símbolo cuenta como máximo una vez por relato propio o parcial; relatos de terceros se excluyen.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("agregar")
    add.add_argument("--titulo", default="Sueño sin título")
    add.add_argument("--simbolos", required=True, help="Lista separada por comas")
    add.add_argument("--tipo", choices=sorted(VALID_TYPES), default="propio")
    add.add_argument("--confirmar", action="store_true", help="Confirma que el usuario autorizó guardar símbolos/título localmente")
    sub.add_parser("tendencias")
    args = parser.parse_args()
    try:
        if args.command == "agregar":
            result = add_entry(args.titulo, args.simbolos, args.tipo, args.confirmar)
        else:
            result = trends()
    except (ValueError, RuntimeError) as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
