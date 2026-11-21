"""Wspólne funkcje narzędzi cyberiady: rejestr projektów, ścieżki Claude Code, sesje."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import yaml

CYBERIADA = Path(__file__).resolve().parent.parent
DOM = Path.home()
CLAUDE_DIR = DOM / ".claude"
SESJE_DIR = CLAUDE_DIR / "projects"


def komputer() -> str:
    return os.environ.get("COMPUTERNAME", "").upper()


def rejestr() -> dict:
    with open(CYBERIADA / "projekty.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def projekty() -> dict[str, Path]:
    """Projekty tego komputera: nazwa -> ścieżka bezwzględna."""
    dane = rejestr()
    baza = (dane.get("komputery") or {}).get(komputer())
    wynik = {}
    for nazwa, p in (dane.get("projekty") or {}).items():
        sciezka = Path(p["sciezka"])
        if not sciezka.is_absolute():
            if not baza:
                continue
            sciezka = Path(baza) / sciezka
        wynik[nazwa] = sciezka.resolve()
    return wynik


def projekt_dla(sciezka: Path) -> tuple[str, Path] | None:
    """Projekt, w którym leży ścieżka (także worktree w .claude/worktrees)."""
    s = sciezka.resolve()
    najlepszy = None
    for nazwa, p in projekty().items():
        if s == p or p in s.parents:
            if najlepszy is None or len(str(p)) > len(str(najlepszy[1])):
                najlepszy = (nazwa, p)
    return najlepszy


def zakoduj(sciezka: Path | str) -> str:
    """Nazwa katalogu sesji w ~/.claude/projects (każdy znak spoza [A-Za-z0-9] -> '-')."""
    return re.sub(r"[^A-Za-z0-9]", "-", str(sciezka))


def claude_exe() -> str:
    exe = shutil.which("claude")
    if not exe:
        raise SystemExit("Nie znaleziono polecenia `claude` w PATH.")
    return exe


def tytul_sesji(plik_jsonl: Path) -> str | None:
    """Ostatnia nazwa sesji (custom-title) z katalogu sesji albo z jej dziennika."""
    meta = plik_jsonl.with_suffix("") / "custom-title.json"
    if meta.exists():
        try:
            return json.loads(meta.read_text(encoding="utf-8")).get("customTitle")
        except (OSError, ValueError):
            pass
    tytul = None
    try:
        with open(plik_jsonl, encoding="utf-8", errors="replace") as f:
            for linia in f:
                if '"custom-title"' in linia:
                    try:
                        tytul = json.loads(linia).get("customTitle") or tytul
                    except ValueError:
                        pass
    except OSError:
        return None
    return tytul


def sesja_o_nazwie(katalog_projektu: Path, nazwa: str) -> str | None:
    """Identyfikator najnowszej sesji o danej nazwie w danym folderze."""
    d = SESJE_DIR / zakoduj(katalog_projektu)
    if not d.is_dir():
        return None
    for plik in sorted(d.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True):
        if tytul_sesji(plik) == nazwa:
            return plik.stem
    return None


def agenci_w_tle() -> list[dict]:
    """Lista sesji z `claude agents --json --all` (pusta, gdy polecenie zawiedzie)."""
    try:
        wynik = subprocess.run([claude_exe(), "agents", "--json", "--all"],
                               capture_output=True, text=True, encoding="utf-8", timeout=60)
        return json.loads(wynik.stdout or "[]")
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return []
