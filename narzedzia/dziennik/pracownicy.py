"""Lista pracowników (sesji Claude Code) dla dziennika: aktywni i zakończeni dziś.

Użycie: python -X utf8 pracownicy.py [--wyjscie plik.json]
Domyślnie zapisuje _robocze/dziennik/pracownicy.json. Źródła: `claude agents --json --all`, logi sesji, git.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wspolne import CYBERIADA, SESJE_DIR, agenci_w_tle, projekt_dla, zakoduj  # noqa: E402
from zuzycie import czytaj, wazone  # noqa: E402

STANY = {"busy": "pracuje", "working": "pracuje", "idle": "czeka", "stopped": "zakończony", "done": "zakończony"}
MODELE = ("fable", "opus", "sonnet", "haiku")


def rola(nazwa: str) -> str:
    if nazwa.startswith("archi-"):
        return "Archi"
    if nazwa.startswith("wyko-"):
        return "wyko"
    return "pomo"


def git(cwd: Path, *a: str) -> str:
    try:
        w = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, encoding="utf-8", timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return w.stdout.strip() if w.returncode == 0 else ""


def log_sesji(cwd: str, sesja_id: str) -> Path | None:
    for kandydat in (SESJE_DIR / zakoduj(cwd) / f"{sesja_id}.jsonl", *SESJE_DIR.glob(f"*/{sesja_id}.jsonl")):
        if kandydat.is_file():
            return kandydat
    return None


def zuzycie(plik: Path | None) -> tuple[int, str | None, str | None]:
    """(tokeny ważone z podagentami, główny model, czas ostatniego wpisu)."""
    if not plik:
        return 0, None, None
    wpisy = czytaj(plik, lambda c, t: True)
    for s in plik.with_suffix("").glob("subagents/*.jsonl"):
        wpisy += czytaj(s, lambda c, t: True)
    licz: dict[str, float] = {}
    for w in wpisy:
        m = next((x for x in MODELE if x in w["model"].lower()), None)
        if m:
            licz[m] = licz.get(m, 0) + wazone(w)
    ostatni = max((w["czas"] for w in wpisy), default=None)
    return round(sum(wazone(w) for w in wpisy)), max(licz, key=licz.get) if licz else None, ostatni


def zbuduj(teraz: datetime | None = None) -> dict:
    teraz = (teraz or datetime.now()).astimezone()
    dzis = teraz.date()
    lista = []
    for a in agenci_w_tle():
        nazwa = a.get("name") or (a.get("sessionId") or "?")[:8]
        stan = STANY.get(a.get("status") or a.get("state") or "", "zakończony")
        cwd = a.get("cwd") or ""
        tokeny, model, ostatni = zuzycie(log_sesji(cwd, a.get("sessionId") or ""))
        start = datetime.fromtimestamp(a["startedAt"] / 1000).astimezone() if a.get("startedAt") else None
        koniec_dnia = datetime.fromisoformat(ostatni.replace("Z", "+00:00")).astimezone() if ostatni else start
        if stan == "zakończony" and (not koniec_dnia or koniec_dnia.date() != dzis):
            continue
        znaleziony = projekt_dla(Path(cwd)) if cwd else None
        projekt = znaleziony[0] if znaleziony else (Path(cwd).name.lower() if cwd else None)
        m = re.fullmatch(r"wyko-[a-z0-9]+-(\d+)-(.+)", nazwa)
        aktywny = stan != "zakończony" and cwd and Path(cwd).is_dir()
        krok = git(Path(cwd), "log", "-1", "--format=%s%x1f%cI") if aktywny else ""
        temat, _, czas_kroku = krok.partition("\x1f")
        lista.append({"nazwa": nazwa, "rola": rola(nazwa), "projekt": projekt,
                      "watek": f"{m.group(1)}/{m.group(2)}" if m else None, "stan": stan,
                      "w_tle": a.get("kind") == "background", "start": start.isoformat(timespec="seconds") if start else None,
                      "ostatnio": koniec_dnia.isoformat(timespec="seconds") if koniec_dnia else None,
                      "krok": temat[:160] or None, "krok_czas": czas_kroku or None,
                      "tokeny": tokeny, "model": model})
    kolej = {"pracuje": 0, "czeka": 1, "zakończony": 2}
    lista.sort(key=lambda p: (kolej[p["stan"]], p["projekt"] or "", p["nazwa"]))
    return {"wygenerowano": teraz.isoformat(timespec="seconds"), "lista": lista}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--wyjscie", type=Path, default=CYBERIADA / "_robocze" / "dziennik" / "pracownicy.json")
    a = p.parse_args()
    dane = zbuduj()
    a.wyjscie.parent.mkdir(parents=True, exist_ok=True)
    a.wyjscie.write_text(json.dumps(dane, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"zapisano {a.wyjscie} · pracowników {len(dane['lista'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
