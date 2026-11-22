"""Hook PostToolUse (Bash) dla sesji wyko i Archiego: po udanym `git commit` każe zapisać postęp do dziennika.

Podpięty przez `--settings` w `wyko.py` (narzedzia/wyko/ustawienia.json) i `archi.py` (narzedzia/archi/ustawienia.json).
Czyta JSON hooka ze stdin, sam liczy dane z gita i wypisuje gotową instrukcję (additionalContext).
Wyko zapisuje dokument `postep/<sesja>`; Archi dodatkowo generuje i zapisuje dokument projektu.
Każdy błąd: cisza (hook nigdy nie przeszkadza w pracy).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wspolne import CYBERIADA, projekt_dla, rejestr, tytul_sesji  # noqa: E402

DOMYSLNY_URL = "https://claude.ai/artifact/5c5LeHX3ohn5qRanw6XyoT"


def git(cwd: Path, *a: str) -> str:
    w = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    return w.stdout.strip() if w.returncode == 0 else ""


def instrukcja(wejscie: dict) -> str | None:
    polecenie = str((wejscie.get("tool_input") or {}).get("command") or "")
    if not re.search(r"\bgit\b[^\n|;&]*\bcommit\b", polecenie):
        return None
    cwd = Path(wejscie.get("cwd") or ".")
    sesja = tytul_sesji(Path(wejscie["transcript_path"])) if wejscie.get("transcript_path") else None
    if not sesja or not sesja.startswith(("wyko-", "archi-")):
        return None
    znaleziony = projekt_dla(cwd)
    projekt = znaleziony[0] if znaleziony else cwd.name.lower()
    galaz = git(cwd, "rev-parse", "--abbrev-ref", "HEAD")
    krok = git(cwd, "log", "-1", "--format=%s")
    if not krok:
        return None
    rola, watek, commity = "Archi", None, None
    m = re.fullmatch(rf"wyko-{re.escape(projekt)}-(\d+)-(.+)", sesja)
    if sesja.startswith("wyko-"):
        rola = "wyko"
        watek = f"{m.group(1)}/{m.group(2)}" if m else None
        licz = git(cwd, "rev-list", "--count", "main..HEAD") or git(cwd, "rev-list", "--count", "master..HEAD")
        commity = int(licz) if licz.isdigit() else None
    dane = {"projekt": projekt, "watek": watek, "rola": rola, "krok": krok[:160], "commity": commity,
            "galaz": galaz or None, "czas": datetime.now().astimezone().isoformat(timespec="seconds")}
    url = rejestr().get("dziennik") or DOMYSLNY_URL
    tekst = (f"Dziennik (hook po commicie): zapisz postęp jednym wywołaniem narzędzia ArtifactData "
             f"(odroczone: najpierw ToolSearch select:ArtifactData, jeśli go nie masz): action set, url {url}, "
             f"collection postep, doc_id {sesja}, data {json.dumps(dane, ensure_ascii=False)}. "
             f"if_version: wersja z Twojego poprzedniego zapisu tego dokumentu (pierwszy raz bez; gdy zapis "
             f"odmówi z powodu wersji, ponów z wersją podaną w odmowie). Nie czytaj dokumentu.")
    if rola == "Archi":
        tekst += (f" Potem ruchy zadań z dziennika: ArtifactData get, collection uklad, doc_id {projekt}; jeśli jest i ma "
                  f"`ruchy` ({{\"Z9\": \"nastepnie\", ...}}), uruchom `python -X utf8 {CYBERIADA.as_posix()}/narzedzia/dziennik/"
                  f"przenies.py --projekt {projekt} Z9=nastepnie ...`, zacommituj `Zadania.md` i po zapisie projektu "
                  f"usuń dokument (ArtifactData delete, collection uklad, doc_id {projekt}).")
        tekst += (f" Potem odśwież dokument projektu: `python -X utf8 {CYBERIADA.as_posix()}/narzedzia/dziennik/"
                  f"generuj.py --projekt {projekt}` i ArtifactData set, collection projekty, doc_id {projekt}, "
                  f"file_path {CYBERIADA.as_posix()}/_robocze/dziennik/{projekt}.json, z if_version jak wyżej.")
    return tekst + " Nie komentuj tego w odpowiedzi."


def main() -> int:
    try:
        tekst = instrukcja(json.load(sys.stdin))
    except Exception:  # noqa: BLE001 - hook nie może przerwać pracy
        return 0
    if tekst:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                                 "additionalContext": tekst}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
