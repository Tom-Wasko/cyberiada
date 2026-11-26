"""Raport z wyników eksperymentu: tabela Markdown i optimum (sen, komp) osobno dla małych i dużych zadań.

  python -X utf8 narzedzia/eksperyment/raport.py [--wyniki plik.jsonl] [--wyjscie raport.md]
Optimum (tylko ustawienia, w których wszystkie przebiegi mają zaliczone testy i średnią ocenę >= 4):
  sen  = najmniej tokenów ważonych (średnio),
  komp = najkrótszy czas (średnio).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean

KORZEN = Path(__file__).resolve().parent.parent.parent
WYNIKI = KORZEN / "_robocze" / "eksperyment" / "wyniki.jsonl"
WYJSCIE = KORZEN / "_robocze" / "eksperyment" / "raport.md"
PROG_OCENY = 4


def wczytaj(plik: Path) -> list[dict]:
    wynik = []
    if plik.is_file():
        for linia in plik.read_text(encoding="utf-8").splitlines():
            try:
                wynik.append(json.loads(linia))
            except ValueError:
                continue
    return wynik


def zalicza(w: dict) -> bool:
    return bool((w.get("testy") or {}).get("zaliczone"))


def ustawienie(w: dict) -> tuple:
    return (w["model"], w["effort"], w["autocompact"])


def grupuj(wyniki: list[dict]) -> dict[tuple, list[dict]]:
    """Przebiegi z wykonanym pomiarem (tokeny i ocena), po (wielkość, model, effort, autocompact)."""
    g: dict[tuple, list[dict]] = defaultdict(list)
    for w in wyniki:
        if w.get("tokeny_wazone") is not None and w.get("ocena") is not None:
            g[(w["wielkosc"], *ustawienie(w))].append(w)
    return g


def srednie(grupa: list[dict]) -> dict:
    return {"n": len(grupa), "wazone": mean(w["tokeny_wazone"] for w in grupa),
            "czas": mean(w.get("czas_s") or 0 for w in grupa), "ocena": mean(w["ocena"] for w in grupa),
            "testy": sum(zalicza(w) for w in grupa), "dobre": all(zalicza(w) for w in grupa)
            and mean(w["ocena"] for w in grupa) >= PROG_OCENY}


def optimum(wyniki: list[dict]) -> dict[str, dict]:
    """{wielkosc: {sen: (ustawienie, srednie) | None, komp: ...}}"""
    wyn: dict[str, dict] = {}
    for (wielkosc, *ust), grupa in grupuj(wyniki).items():
        s = srednie(grupa)
        o = wyn.setdefault(wielkosc, {"sen": None, "komp": None, "kandydaci": 0})
        if not s["dobre"]:
            continue
        o["kandydaci"] += 1
        if o["sen"] is None or s["wazone"] < o["sen"][1]["wazone"]:
            o["sen"] = (tuple(ust), s)
        if o["komp"] is None or s["czas"] < o["komp"][1]["czas"]:
            o["komp"] = (tuple(ust), s)
    return wyn


def mln(x: float | None) -> str:
    return "–" if x is None else f"{x / 1e6:.2f}M"


def min_s(x: float | None) -> str:
    return "–" if x is None else f"{x / 60:.1f} min"


def opis_ust(u: tuple) -> str:
    return f"{u[0]} {u[1]} (autocompact {u[2]})"


def raport(wyniki: list[dict]) -> str:
    kompletne = [w for w in wyniki if w.get("kompletny")]
    out = ["# Eksperyment Z10: wyniki", "",
           f"Przebiegów: {len(wyniki)}, z pełnym pomiarem: {len(kompletne)}. "
           f"Tokeny ważone: przebiegi {mln(sum(w.get('tokeny_wazone') or 0 for w in wyniki))}, "
           f"oceny {mln(sum(w.get('ocena_wazone') or 0 for w in wyniki))}.", "",
           "## Optimum", "",
           f"Warunek: wszystkie przebiegi ustawienia mają zaliczone testy, a średnia ocena ≥ {PROG_OCENY}. "
           "Sen = najmniej tokenów ważonych, komp = najkrótszy czas.", ""]
    opt = optimum(wyniki)
    for wielkosc, nazwa in (("male", "Małe zadania"), ("duze", "Duże zadania")):
        o = opt.get(wielkosc)
        out.append(f"### {nazwa}")
        if not o or not o["sen"]:
            out += ["Brak ustawienia spełniającego warunek (za mało przebiegów albo jakość poniżej progu).", ""]
            continue
        sen, komp = o["sen"], o["komp"]
        out += [f"- **sen:** {opis_ust(sen[0])}: {mln(sen[1]['wazone'])}, {min_s(sen[1]['czas'])}, "
                f"ocena {sen[1]['ocena']:.1f}, testy {sen[1]['testy']}/{sen[1]['n']}",
                f"- **komp:** {opis_ust(komp[0])}: {min_s(komp[1]['czas'])}, {mln(komp[1]['wazone'])}, "
                f"ocena {komp[1]['ocena']:.1f}, testy {komp[1]['testy']}/{komp[1]['n']}",
                f"- ustawień spełniających warunek: {o['kandydaci']}", ""]
    out += ["## Ustawienia (średnie z powtórzeń)", "",
            "| wielkość | model | effort | autocompact | n | tokeny ważone | czas | tury | ocena | testy | warunek |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    for klucz, grupa in sorted(grupuj(wyniki).items()):
        s = srednie(grupa)
        tury = mean(w.get("tury") or 0 for w in grupa)
        out.append(f"| {klucz[0]} | {klucz[1]} | {klucz[2]} | {klucz[3]} | {s['n']} | {mln(s['wazone'])} | "
                   f"{min_s(s['czas'])} | {tury:.0f} | {s['ocena']:.1f} | {s['testy']}/{s['n']} | "
                   f"{'tak' if s['dobre'] else 'nie'} |")
    out += ["", "## Przebiegi", "",
            "| id | zadanie | czas | tury | tokeny ważone | surowe | testy | ocena | koszt oceny (wazone) | błędy |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for w in sorted(wyniki, key=lambda x: x["id"]):
        t = w.get("testy") or {}
        blad = "; ".join(w.get("bledy") or []) or "–"
        out.append(f"| {w['id']} | {w['zadanie']} ({w['wielkosc']}) | {min_s(w.get('czas_s'))} | {w.get('tury', '–')} | "
                   f"{mln(w.get('tokeny_wazone'))} | {w.get('tokeny_surowe', '–')} | "
                   f"{'tak' if t.get('zaliczone') else 'nie'} | {w.get('ocena', '–')} | {mln(w.get('ocena_wazone'))} | "
                   f"{blad[:120]} |")
    return "\n".join(out) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description="Raport z wyników eksperymentu.")
    p.add_argument("--wyniki", type=Path, default=WYNIKI)
    p.add_argument("--wyjscie", type=Path, default=WYJSCIE)
    a = p.parse_args()
    tekst = raport(wczytaj(a.wyniki))
    a.wyjscie.parent.mkdir(parents=True, exist_ok=True)
    a.wyjscie.write_text(tekst, encoding="utf-8")
    print(f"Zapisano {a.wyjscie}")
    print(tekst.split("## Ustawienia")[0].strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
