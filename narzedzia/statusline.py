"""Statusline Claude Code: jedna krótka linia + zapis limitu do ~/.claude/cyberiada-limit.json.

Claude Code podaje JSON na stdin (https://code.claude.com/docs/en/statusline). Używane pola:
model.display_name, context_window.used_percentage, rate_limits.five_hour / seven_day
(used_percentage, resets_at = epoch s). Gdy pól limitu brak, plik limitu zostaje bez zmian.
Błędy są ciche: statusline nie może przeszkadzać w pracy.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

PLIK_LIMITU = Path.home() / ".claude" / "cyberiada-limit.json"


def okno(d: dict | None) -> dict | None:
    if not isinstance(d, dict) or d.get("used_percentage") is None:
        return None
    return {"used": d["used_percentage"], "resets_at": d.get("resets_at")}


def limity(dane: dict) -> dict | None:
    """Zawartość pliku limitu albo None, gdy w danych nie ma limitu."""
    rl = dane.get("rate_limits") or {}
    wynik = {k: w for k, w in (("five_hour", okno(rl.get("five_hour"))),
                               ("seven_day", okno(rl.get("seven_day")))) if w}
    if not wynik:
        return None
    return {**wynik, "czas": datetime.now().astimezone().isoformat(timespec="seconds")}


def zapisz(wynik: dict, plik: Path = PLIK_LIMITU) -> None:
    tmp = plik.with_name(plik.name + ".tmp")
    tmp.write_text(json.dumps(wynik, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, plik)


def linia(dane: dict) -> str:
    czesci = [(dane.get("model") or {}).get("display_name") or "?"]
    ctx = (dane.get("context_window") or {}).get("used_percentage")
    if ctx is not None:
        czesci.append(f"kontekst {ctx:.0f}%")
    f = okno((dane.get("rate_limits") or {}).get("five_hour"))
    if f:
        czesci.append(f"limit 5h {f['used']:.0f}%")
        if f["resets_at"]:
            reszta = max(0, int(f["resets_at"] - datetime.now().timestamp())) // 60
            czesci.append(f"do resetu {reszta // 60}:{reszta % 60:02d}")
    return " · ".join(czesci)


def main() -> int:
    try:
        dane = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        dane = {}
    try:
        print(linia(dane))
    except Exception:  # noqa: BLE001
        print("")
    try:
        w = limity(dane)
        if w:
            zapisz(w)
    except Exception:  # noqa: BLE001
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
