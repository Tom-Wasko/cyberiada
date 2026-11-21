"""Polecenie `archi <projekt> [tryb]`: otwiera czat Archiego projektu (wznawia, jeśli już był).

  archi                 lista projektów tego komputera
  archi lukrum          czat archi-lukrum w folderze projektu
  archi lukrum hejo     to samo i od razu /hejo
  archi lukrum papa 4h  to samo i od razu /papa 4h
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wspolne import CYBERIADA, claude_exe, komputer, projekt_dla, projekty, sesja_o_nazwie  # noqa: E402

ROLA = CYBERIADA / "role" / "archi.md"
TRYBY = {"hejo", "papa", "wznow", "podroz"}


def main(argv: list[str]) -> int:
    znane = projekty()
    if not argv:
        tutaj = projekt_dla(Path.cwd())
        if not tutaj:
            print(f"Projekty na komputerze {komputer()}:")
            for nazwa, p in znane.items():
                print(f"  archi {nazwa:<14} {p}")
            print("Tryb na start: archi <projekt> hejo | papa 4h | wznow")
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
    polecenie += ["--model", "opus", "--effort", "medium", "--rc", "--autocompact", "120k",
                  "--append-system-prompt-file", str(ROLA)]
    if reszta:
        tryb = reszta[0].lstrip("/")
        prompt = " ".join(reszta)
        polecenie.append("/" + prompt.lstrip("/") if tryb in TRYBY else prompt)
    print(("Wznawiam " if istnieje else "Nowy czat ") + sesja + f" w {katalog}")
    os.chdir(katalog)
    return subprocess.call(polecenie)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
