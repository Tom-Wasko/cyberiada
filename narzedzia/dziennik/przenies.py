"""Przenosi zadania między sekcjami `Zadania.md` (ruchy z dziennika: przeciąganie kart).

Użycie: python -X utf8 przenies.py --projekt <nazwa albo ścieżka> Z5=nastepnie Z1=w_toku ...
Kolumny: w_toku, nastepnie, zaplanowane, zrobione, odlozone. Brakująca sekcja powstaje przed kolejną w tej kolejności.
Zadanie przenosi się z podpunktami (linie wcięte pod nim). Końce linii pliku zostają.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from wspolne import projekty  # noqa: E402

SEKCJE = {"w_toku": "W toku", "nastepnie": "Następnie", "zaplanowane": "Zaplanowane",
          "zrobione": "Zrobione w tej podróży", "odlozone": "Odłożone"}


def przenies(tekst: str, ruchy: dict[str, str]) -> tuple[str, list[str]]:
    nl = "\r\n" if "\r\n" in tekst else "\n"
    linie = tekst.split(nl)
    zrobione = []
    for numer, cel in ruchy.items():
        if cel not in SEKCJE:
            raise SystemExit(f"Nieznana kolumna: {cel}")
        start = next((i for i, l in enumerate(linie) if re.match(rf"- {re.escape(numer)}\b", l)), None)
        if start is None:
            continue
        koniec = start + 1
        while koniec < len(linie) and linie[koniec].startswith((" ", "\t")) and linie[koniec].strip():
            koniec += 1
        blok = linie[start:koniec]
        del linie[start:koniec]
        naglowek = f"## {SEKCJE[cel]}"
        if naglowek not in linie:
            kolejne = list(SEKCJE.values())[list(SEKCJE).index(cel) + 1:]
            gdzie = next((i for i, l in enumerate(linie) if l in {f"## {k}" for k in kolejne}), len(linie))
            linie[gdzie:gdzie] = [naglowek, ""]
        i = linie.index(naglowek) + 1
        while i < len(linie) and not linie[i].startswith("## "):
            i += 1
        while i > linie.index(naglowek) + 1 and not linie[i - 1].strip():
            i -= 1
        linie[i:i] = blok
        zrobione.append(f"{numer} → {SEKCJE[cel]}")
    return nl.join(linie), zrobione


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--projekt", required=True)
    p.add_argument("ruchy", nargs="+", help="Z<n>=kolumna")
    a = p.parse_args()
    sciezka = projekty().get(a.projekt) or Path(a.projekt)
    plik = sciezka / "dokumentacja" / "Zadania.md"
    ruchy = dict(r.split("=", 1) for r in a.ruchy)
    tekst, zrobione = przenies(plik.read_bytes().decode("utf-8"), ruchy)
    plik.write_bytes(tekst.encode("utf-8"))
    print("; ".join(zrobione) or "nic do przeniesienia")
    return 0


if __name__ == "__main__":
    sys.exit(main())
