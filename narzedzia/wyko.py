"""Uruchamia wyko: sesję Claude Code w tle na jeden wątek podróży.

Użycie (Archi, z folderu projektu albo z dowolnego miejsca):
  python -X utf8 C:/Users/PC/cyberiada/narzedzia/wyko.py <plik wątku> [--tryb komp|sen|szkola] [--model sonnet] [--effort medium] [--pokaz]
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
from tryb import tryb_nazwa, tryb_ze_stanu  # noqa: E402
from wspolne import CYBERIADA, agenci_w_tle, claude_exe, projekt_dla  # noqa: E402

ROLA = CYBERIADA / "role" / "wyko.md"
USTAWIENIA = CYBERIADA / "narzedzia" / "wyko" / "ustawienia.json"


def ustawienia_trybu(tryb: str, tresc: str) -> dict:
    """Model, effort i autocompact dla trybu (komp/sen/szkola) i briefu (`Rodzaj: mechaniczny|trudny`)."""
    rodzaj = re.search(r"^\s*(?:[-*]\s*)?\**Rodzaj:\**\s*(mechaniczny|trudny)\b", tresc, re.IGNORECASE | re.MULTILINE)
    rodzaj = rodzaj.group(1).lower() if rodzaj else ""
    if tryb == "komp":
        return {"model": "sonnet", "effort": "high" if rodzaj == "trudny" else "medium", "autocompact": "200k"}
    return {"model": "sonnet", "effort": "low" if rodzaj == "mechaniczny" else "medium", "autocompact": "120k"}


def wspolne_flagi(model: str, effort: str = "medium", autocompact: str = "200k") -> list[str]:
    return ["--model", model, "--effort", effort, "--autocompact", autocompact, "--no-chrome",
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


def nowy(plik: Path, model: str | None, effort: str | None, tryb: str | None, pokaz: bool) -> int:
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
    # Worktree powstaje z gałęzi zdalnej: niewypchnięty commit z plikiem wątku byłby niewidoczny dla wyko.
    if not pokaz and git("rev-parse", "--abbrev-ref", "@{u}", cwd=korzen) and \
            git("rev-list", "--count", "@{u}..HEAD", cwd=korzen) not in ("", "0"):
        print("Wypycham commity, żeby worktree miał plik wątku:", git("push", "-q", cwd=korzen) or "ok")
    tryb = tryb or tryb_ze_stanu(korzen)["tryb"]
    tresc = plik.read_text(encoding="utf-8")
    ust = ustawienia_trybu(tryb, tresc)
    print(f"Tryb: {tryb} (model {model or ust['model']}, effort {effort or ust['effort']}, "
          f"autocompact {ust['autocompact']})")
    nazwa = f"wyko-{projekt}-{nn}-{watek}"
    if not pokaz and any(a.get("name") == nazwa and a.get("status") not in ("stopped", "done")
                         for a in agenci_w_tle()):
        raise SystemExit(f"Sesja {nazwa} już działa (claude agents).")
    m_archi = re.search(r"\*\*Archi:\*\*\s*`?(archi-[a-z0-9-]+)", tresc)
    archi = m_archi.group(1) if m_archi else f"archi-{projekt}"
    prompt = (f"Jesteś wyko. Twój plik wątku: {wzgl} (w Twoim worktree, ścieżka względna). "
              f"Przeczytaj brief na górze pliku i wykonaj go według swojej roli. "
              f"Archi to sesja {archi}. Już jesteś w swoim worktree: nie wołaj EnterWorktree i nie rób cd poza niego.")
    polecenie = [claude_exe(), "--bg", "--name", nazwa, *wspolne_flagi(model or ust["model"], effort or ust["effort"],
                                                                  ust["autocompact"]),
                 "-w", f"podroz-{nn}-{watek}", prompt]
    return uruchom(polecenie, korzen, pokaz)


def wznow(cel: str, pokaz: bool) -> int:
    sesje = [a for a in agenci_w_tle() if cel in (a.get("name"), a.get("sessionId"), a.get("id"))
             or (len(cel) >= 8 and (a.get("sessionId") or "").startswith(cel))]
    if not sesje:
        raise SystemExit(f"Nie znaleziono sesji {cel} w `claude agents --json --all`.")
    s = sesje[0]
    sid = s.get("sessionId") or s.get("id")
    # Bez flag: sesja w tle ma zapisane własne opcje (model, uprawnienia, --settings). Z flagami albo skróconym
    # id Claude Code startuje kopię pod nowym id (próba 22.11, Z5). Ustawienia z pliku czyta od nowa.
    polecenie = [claude_exe(), "--bg", "--resume", sid,
                 "Wznowienie po przerwie. Sprawdź `git log` i raport w pliku wątku, dokończ brief."]
    return uruchom(polecenie, Path(s.get("cwd") or "."), pokaz)


def tryb_nazwa_arg(tekst: str) -> str:
    t = tryb_nazwa(tekst)
    if not t:
        raise argparse.ArgumentTypeError("komp, sen albo szkola")
    return t


def main() -> int:
    p = argparse.ArgumentParser(description="Uruchamia wyko (sesję w tle) dla wątku podróży.")
    p.add_argument("plik", nargs="?", type=Path, help="plik wątku")
    p.add_argument("--wznow", metavar="SESJA", help="wznów zatrzymaną sesję wyko (id albo nazwa)")
    p.add_argument("--model", help="wygrywa z trybem (domyślnie sonnet)")
    p.add_argument("--effort", choices=["low", "medium", "high", "xhigh", "max"], help="wygrywa z trybem")
    p.add_argument("--tryb", type=tryb_nazwa_arg, help="komp|sen|szkola (domyślnie linia Tryb: w Stan.md projektu, "
                   "potem komp)")
    p.add_argument("--pokaz", action="store_true", help="tylko wypisz polecenie")
    a = p.parse_args()
    if a.wznow:
        return wznow(a.wznow, a.pokaz)
    if not a.plik:
        p.error("podaj plik wątku albo --wznow")
    return nowy(a.plik, a.model, a.effort, a.tryb, a.pokaz)


if __name__ == "__main__":
    sys.exit(main())
