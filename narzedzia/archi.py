"""Polecenie `archi <projekt> [tryb]`: otwiera czat Archiego projektu (wznawia, jeśli już był).

  archi                 lista projektów tego komputera
  archi lukrum              czat archi-lukrum; Archi sam pyta o podróż (prompt `start`)
  archi lukrum komp         to samo i od razu /komp (szef przy komputerze)
  archi lukrum sen          /sen (noc, Archi sam)
  archi lukrum szkola 16:00 /szkola 16:00 (rama czasowa)
  --pokaz                   tylko wypisz polecenie
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wspolne import CYBERIADA, claude_exe, komputer, projekt_dla, projekty, sesja_o_nazwie  # noqa: E402

ROLA = CYBERIADA / "role" / "archi.md"
USTAWIENIA = CYBERIADA / "narzedzia" / "archi" / "ustawienia.json"  # hook dziennika po commicie
TRYBY = {"komp", "sen", "szkola", "hej"}


def main(argv: list[str]) -> int:
    pokaz = "--pokaz" in argv
    argv = [a for a in argv if a != "--pokaz"]
    znane = projekty()
    if not argv:
        tutaj = projekt_dla(Path.cwd())
        if not tutaj:
            print(f"Projekty na komputerze {komputer()}:")
            for nazwa, p in znane.items():
                print(f"  archi {nazwa:<14} {p}")
            print("Użycie: archi <projekt> [komp | sen | szkola 16:00] [--pokaz]")
            return 0
        argv = [tutaj[0]]
    nazwa, reszta = argv[0], argv[1:]
    if nazwa not in znane:
        raise SystemExit(f"Nieznany projekt „{nazwa}”. Znane: {', '.join(znane) or 'brak'}. "
                         "Nowy projekt: /nowy-projekt w dowolnym czacie.")
    katalog = znane[nazwa]
    if not katalog.is_dir():
        raise SystemExit(f"Brak folderu projektu: {katalog}")
    sesja = f"archi-{nazwa}"
    istnieje = sesja_o_nazwie(katalog, sesja)
    polecenie = [claude_exe()]
    polecenie += ["--resume", istnieje] if istnieje else ["--name", sesja]
    polecenie += ["--model", "opus", "--effort", "medium", "--rc", "--autocompact", "250k", "--settings", str(USTAWIENIA),
                  "--append-system-prompt-file", str(ROLA)]
    if reszta:
        tryb = reszta[0].lstrip("/")
        prompt = " ".join(reszta)
        polecenie.append("/" + prompt.lstrip("/") if tryb in TRYBY else prompt)
    else:
        polecenie.append("start")
    print(("Wznawiam " if istnieje else "Nowy czat ") + sesja + f" w {katalog}")
    if pokaz:
        print("Polecenie:", " ".join(f'"{a}"' if " " in a else a for a in polecenie))
        return 0
    os.chdir(katalog)
    return subprocess.call(polecenie)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
