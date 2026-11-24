"""Tempo pracy: gdzie jesteśmy w oknie 5 h i jaka rada dla wybranego tempa.

  python -X utf8 narzedzia/tempo.py [--tempo zolw|zwykly|krolik] [--json] [--plik <limit.json>]

Dane: ~/.claude/cyberiada-limit.json (zapisuje statusline.py). Tempo domyślnie z linii `Tempo: ...`
w dokumentacja/Stan.md bieżącego folderu (też z folderu nadrzędnego). Żółw nigdy nie każe czekać:
reguluje oszczędnością (effort, model, liczba wyko), nie przerwami.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path

PLIK_LIMITU = Path.home() / ".claude" / "cyberiada-limit.json"
OKNO = timedelta(hours=5)
MARGINES = 10  # punkty procentowe
STARE_MIN = 15
TEMPA = ("zolw", "zwykly", "krolik")


def tempo_nazwa(tekst: str | None) -> str | None:
    """żółw/Żółw/zolw → 'zolw' itd.; nieznane → None."""
    if not tekst:
        return None
    t = unicodedata.normalize("NFKD", tekst.strip().lower().replace("ł", "l"))
    t = "".join(c for c in t if not unicodedata.combining(c))
    return t if t in TEMPA else None


def tempo_ze_stanu(folder: Path) -> str | None:
    """Wartość linii `Tempo: ...` z dokumentacja/Stan.md folderu albo jego rodziców."""
    for f in [folder.resolve(), *folder.resolve().parents]:
        stan = f / "dokumentacja" / "Stan.md"
        if stan.is_file():
            m = re.search(r"^\s*(?:[-*]\s*)?\**Tempo:\**\s*([^\s,;.]+)", stan.read_text(encoding="utf-8"),
                          re.MULTILINE | re.IGNORECASE)
            return tempo_nazwa(m.group(1)) if m else None
    return None


def godz(t: datetime) -> str:
    return f"{t:%H:%M}"


def licz(limit: dict, teraz: datetime, tempo: str | None) -> dict:
    wynik: dict = {"tempo": tempo, "ostrzezenia": []}
    czas_pliku = limit.get("czas")
    if czas_pliku:
        try:
            wiek = (teraz - datetime.fromisoformat(czas_pliku)).total_seconds() / 60
            if wiek > STARE_MIN:
                wynik["ostrzezenia"].append(f"dane limitu sprzed {wiek:.0f} min (statusline nie odświeża pliku)")
        except ValueError:
            pass
    f = limit.get("five_hour") or {}
    if f.get("used") is None or not f.get("resets_at"):
        wynik["ostrzezenia"].append("brak danych o limicie 5 h")
        return wynik
    koniec = datetime.fromtimestamp(f["resets_at"]).astimezone()
    start = koniec - OKNO
    uplynelo = teraz - start
    if uplynelo > OKNO:
        wynik["ostrzezenia"].append("okno 5 h z pliku już się skończyło: dane nieaktualne")
        return wynik
    czas_proc = max(0.0, uplynelo / OKNO * 100)
    uzyte = float(f["used"])
    wynik |= {"czas_proc": round(czas_proc, 1), "limit_proc": round(uzyte, 1),
              "roznica_pp": round(uzyte - czas_proc, 1), "reset": godz(koniec), "start_okna": godz(start)}
    if uzyte > 0 and uplynelo.total_seconds() > 60:
        sto = start + uplynelo * (100 / uzyte)
        wynik["prognoza_100"] = godz(sto)
        wynik["przed_resetem"] = sto < koniec
    if tempo == "zolw":
        r = wynik["roznica_pp"]
        wynik["rada"] = ("oszczędniej: effort low, bez nowego wyko równolegle, Haiku do drobnych"
                         if r > MARGINES else "dodaj wyko / wyższy effort" if r < -MARGINES else "tempo dobre")
    return wynik


def tekst(w: dict) -> str:
    L = [f"Tempo: {w['tempo'] or 'nieustalone'}"] if w.get("tempo") else []
    if "limit_proc" in w:
        L.append(f"Okno 5 h: minęło {w['czas_proc']:.0f}% czasu (start {w['start_okna']}, reset {w['reset']}), "
                 f"zużyto {w['limit_proc']:.0f}% limitu, różnica {round(w["roznica_pp"]):+d} pp.")
        if "prognoza_100" in w:
            L.append(f"Prognoza: 100% limitu około {w['prognoza_100']}"
                     + (" (przed resetem)." if w["przed_resetem"] else " (po resecie: limit starczy)."))
        if "rada" in w:
            L.append(f"Rada (żółw): {w['rada']}.")
    L += [f"Uwaga: {o}." for o in w["ostrzezenia"]]
    return "\n".join(L)


def main() -> int:
    p = argparse.ArgumentParser(description="Tempo pracy względem limitu 5 h.")
    p.add_argument("--tempo", help="zolw|zwykly|krolik (domyślnie z Stan.md)")
    p.add_argument("--plik", type=Path, default=PLIK_LIMITU)
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    tempo = tempo_nazwa(a.tempo) if a.tempo else tempo_ze_stanu(Path.cwd())
    if a.tempo and not tempo:
        p.error("tempo: zolw, zwykly albo krolik")
    try:
        limit = json.loads(a.plik.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        limit = {}
        print("Brak pliku limitu (uruchom Claude Code ze statusline z cyberiady: instaluj.py).", file=sys.stderr)
    w = licz(limit, datetime.now().astimezone(), tempo)
    print(json.dumps(w, ensure_ascii=False, indent=1) if a.json else tekst(w))
    return 0


if __name__ == "__main__":
    sys.exit(main())
