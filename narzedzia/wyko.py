"""Uruchamia wyko: sesję Claude Code w tle na jeden wątek podróży.

Użycie (Archi, z folderu projektu albo z dowolnego miejsca):
  python -X utf8 C:/Users/PC/cyberiada/narzedzia/wyko.py <plik wątku> [--model sonnet] [--pokaz]
  python -X utf8 C:/Users/PC/cyberiada/narzedzia/wyko.py --wznow <id albo nazwa sesji> [--pokaz]

Plik wątku: <projekt>/dokumentacja/podroze/NN-temat/watek-<nazwa>.md, zatwierdzony commitem.
Sesja: wyko-<projekt>-<NN>-<nazwa>, worktree .claude/worktrees/podroz-NN-<nazwa>,
gałąź worktree-podroz-NN-<nazwa>.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wspolne import CYBERIADA, agenci_w_tle, claude_exe, projekt_dla  # noqa: E402

ROLA = CYBERIADA / "role" / "wyko.md"
USTAWIENIA = CYBERIADA / "narzedzia" / "wyko" / "ustawienia.json"


def wspolne_flagi(model: str) -> list[str]:
    return ["--model", model, "--effort", "medium", "--autocompact", "100k", "--no-chrome",
            "--permission-mode", "auto", "--settings", str(USTAWIENIA),
            "--append-system-prompt-file", str(ROLA)]


def git(*args: str, cwd: Path) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8").stdout.strip()


def uruchom(polecenie: list[str], cwd: Path, pokaz: bool) -> int:
    print("Polecenie:", " ".join(f'"{a}"' if " " in a else a for a in polecenie))
    if pokaz:
        return 0
    wynik = subprocess.run(polecenie, cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True,
                           text=True, encoding="utf-8")
    print((wynik.stdout + wynik.stderr).strip())
    return wynik.returncode


def nowy(plik: Path, model: str, pokaz: bool) -> int:
    plik = plik.resolve()
    if not plik.is_file():
        raise SystemExit(f"Brak pliku wątku: {plik}")
    m = re.search(r"podroze[\\/](\d+)-[^\\/]+[\\/]watek-([a-z0-9-]+)\.md$", str(plik))
    if not m:
        raise SystemExit("Plik wątku musi leżeć w dokumentacja/podroze/NN-temat/watek-<nazwa>.md "
                         "(nazwa: małe litery, cyfry, myślniki).")
    nn, watek = m.group(1), m.group(2)
    korzen = Path(git("rev-parse", "--show-toplevel", cwd=plik.parent))
    znaleziony = projekt_dla(korzen)
    projekt = znaleziony[0] if znaleziony else korzen.name.lower()
    wzgl = plik.relative_to(korzen).as_posix()
    if git("status", "--porcelain", "--", wzgl, cwd=korzen) or not git("ls-files", wzgl, cwd=korzen):
        raise SystemExit(f"Najpierw zatwierdź plik wątku commitem: {wzgl}")
    nazwa = f"wyko-{projekt}-{nn}-{watek}"
    if any(a.get("name") == nazwa and a.get("status") not in ("stopped", "done")
           for a in agenci_w_tle()):
        raise SystemExit(f"Sesja {nazwa} już działa (claude agents).")
    prompt = (f"Jesteś wyko. Twój plik wątku: {wzgl} (w Twoim worktree, ścieżka względna). "
              f"Przeczytaj brief na górze pliku i wykonaj go według swojej roli. "
              f"Archi to sesja archi-{projekt}.")
    polecenie = [claude_exe(), "--bg", "--name", nazwa, *wspolne_flagi(model),
                 "-w", f"podroz-{nn}-{watek}", prompt]
    return uruchom(polecenie, korzen, pokaz)


def wznow(cel: str, model: str, pokaz: bool) -> int:
    sesje = [a for a in agenci_w_tle() if cel in (a.get("name"), a.get("sessionId"), a.get("id"))]
    if not sesje:
        raise SystemExit(f"Nie znaleziono sesji {cel} w `claude agents --json --all`.")
    s = sesje[0]
    sid = s.get("sessionId") or s.get("id")
    polecenie = [claude_exe(), "--bg", "--resume", sid, *wspolne_flagi(model),
                 "Wznowienie po przerwie. Sprawdź `git log` i raport w pliku wątku, dokończ brief."]
    return uruchom(polecenie, Path(s.get("cwd") or "."), pokaz)


def main() -> int:
    p = argparse.ArgumentParser(description="Uruchamia wyko (sesję w tle) dla wątku podróży.")
    p.add_argument("plik", nargs="?", type=Path, help="plik wątku")
    p.add_argument("--wznow", metavar="SESJA", help="wznów zatrzymaną sesję wyko (id albo nazwa)")
    p.add_argument("--model", default="sonnet")
    p.add_argument("--pokaz", action="store_true", help="tylko wypisz polecenie")
    a = p.parse_args()
    if a.wznow:
        return wznow(a.wznow, a.model, a.pokaz)
    if not a.plik:
        p.error("podaj plik wątku albo --wznow")
    return nowy(a.plik, a.model, a.pokaz)


if __name__ == "__main__":
    sys.exit(main())
