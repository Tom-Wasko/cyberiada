"""Tryb pracy (komp / sen / szkoła): gdzie jesteśmy w oknie 5 h i tygodniu i jaka rada o tempie.

  python -X utf8 narzedzia/tryb.py [--tryb komp|sen|szkola] [--do GG:MM] [--json] [--plik <limit.json>]
                                   [--bez-hamulca] [--teraz <ISO>]

Dane: ~/.claude/cyberiada-limit.json (zapisuje statusline.py). Tryb domyślnie z linii `Tryb: ...`
w dokumentacja/Stan.md bieżącego folderu (też z folderu nadrzędnego); brak linii → komp.
  komp    tylko liczby (okno, tydzień, prognoza), bez rady.
  sen     cel: limit 5 h zużyty równo w oknie (linia idealna od startu do resetu); hamulec tygodniowy.
  szkola  jak sen, ale cel to 100% w chwili T = min(reset okna, koniec ramy `do GG:MM`); hamulec tygodniowy.
Nigdy „czekaj”: tempo reguluje się oszczędnością (effort, liczba wyko), nie przerwami.
Pole `wyko`: ile wyko dodać (+1), zostawić (0) albo odjąć (-1).
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
TYDZIEN = timedelta(days=7)
MARGINES = 10  # pp, okno 5 h
MARGINES_TYGODNIA = 5  # pp
STARE_MIN = 15
TRYBY = ("komp", "sen", "szkola")
STARE_NAZWY = {"nadzorowany": "komp", "autonomiczny": "sen"}


def tryb_nazwa(tekst: str | None) -> str | None:
    """komp/Komp, sen, szkoła/szkola, stare nadzorowany → komp, autonomiczny → sen; nieznane → None."""
    if not tekst:
        return None
    t = unicodedata.normalize("NFKD", tekst.strip().lower().replace("ł", "l"))
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = STARE_NAZWY.get(t, t)
    return t if t in TRYBY else None


def tryb_z_tekstu(tekst: str) -> dict | None:
    """Linia `Tryb: ...` z tekstu → {"tryb","od","do","stan"}; brak linii albo nieznany tryb → None."""
    m = re.search(r"^\s*(?:[-*]\s*)?\**Tryb:\**[ \t]*(.+)$", tekst, re.MULTILINE | re.IGNORECASE)
    if not m:
        return None
    reszta = m.group(1)
    slowo = re.match(r"\s*\**([^\W\d_]+)", reszta)
    tryb = tryb_nazwa(slowo.group(1)) if slowo else None
    if not tryb:
        return None
    od = re.search(r"\bod\s+(\d{1,2}):(\d{2})", reszta, re.IGNORECASE)
    do = re.search(r"\bdo\s+(\d{1,2}):(\d{2})", reszta, re.IGNORECASE)
    stan = re.search(r"\(\s*(jestem|znikam)\s*\)", reszta, re.IGNORECASE)
    return {"tryb": tryb,
            "od": f"{int(od.group(1)):02d}:{od.group(2)}" if od else None,
            "do": f"{int(do.group(1)):02d}:{do.group(2)}" if do else None,
            "stan": stan.group(1).lower() if stan else None}


KOMP = {"tryb": "komp", "od": None, "do": None, "stan": None}


def tryb_ze_stanu(folder: Path) -> dict:
    """Tryb z dokumentacja/Stan.md folderu albo jego rodziców; brak pliku albo linii → komp."""
    for f in [folder.resolve(), *folder.resolve().parents]:
        stan = f / "dokumentacja" / "Stan.md"
        if stan.is_file():
            return tryb_z_tekstu(stan.read_text(encoding="utf-8")) or dict(KOMP)
    return dict(KOMP)


def godz(t: datetime) -> str:
    return f"{t:%H:%M}"


def koniec_ramy(do: str | None, teraz: datetime) -> datetime | None:
    if not do:
        return None
    g, m = (int(x) for x in do.split(":"))
    return teraz.replace(hour=g, minute=m, second=0, microsecond=0)


def rada_okna(roznica: float) -> tuple[str, int]:
    if roznica > MARGINES:
        return "oszczędniej: effort low, bez nowego wyko", -1
    if roznica < -MARGINES:
        return "dodaj wyko albo wyższy effort", 1
    return "tempo dobre", 0


def licz(limit: dict, teraz: datetime, tryb: dict | str | None, bez_hamulca: bool = False) -> dict:
    """Liczby i rada. `tryb`: słownik z tryb_ze_stanu albo sama nazwa; `teraz` z strefą czasową."""
    if not isinstance(tryb, dict):
        tryb = {**KOMP, "tryb": tryb_nazwa(tryb) or "komp"}
    nazwa = tryb["tryb"]
    wynik: dict = {**tryb, "ostrzezenia": [], "wyko": 0}
    czas_pliku = limit.get("czas")
    if czas_pliku:
        try:
            wiek = (teraz - datetime.fromisoformat(czas_pliku)).total_seconds() / 60
            if wiek > STARE_MIN:
                wynik["ostrzezenia"].append(f"dane limitu sprzed {wiek:.0f} min (statusline nie odświeża pliku)")
        except ValueError:
            pass
    # tydzień
    t = limit.get("seven_day") or {}
    if t.get("used") is not None and t.get("resets_at"):
        t_koniec = datetime.fromtimestamp(t["resets_at"]).astimezone()
        t_uplynelo = teraz - (t_koniec - TYDZIEN)
        if timedelta(0) <= t_uplynelo <= TYDZIEN:
            tc = t_uplynelo / TYDZIEN * 100
            wynik |= {"tydzien_czas_proc": round(tc, 1), "tydzien_proc": round(float(t["used"]), 1),
                      "tydzien_roznica_pp": round(float(t["used"]) - tc, 1), "tydzien_reset": f"{t_koniec:%d.%m %H:%M}"}
    # okno 5 h
    f = limit.get("five_hour") or {}
    if f.get("used") is None or not f.get("resets_at"):
        wynik["ostrzezenia"].append("brak danych o limicie 5 h")
        return _hamulec(wynik, nazwa, bez_hamulca)
    koniec = datetime.fromtimestamp(f["resets_at"]).astimezone()
    start = koniec - OKNO
    uplynelo = teraz - start
    if uplynelo > OKNO:
        wynik["ostrzezenia"].append("okno 5 h z pliku już się skończyło: dane nieaktualne")
        return _hamulec(wynik, nazwa, bez_hamulca)
    uzyte = float(f["used"])
    cel = koniec  # chwila, w której limit ma dojść do 100%
    rama = koniec_ramy(tryb.get("do"), teraz) if nazwa == "szkola" else None
    if nazwa == "szkola" and rama is None:
        wynik["ostrzezenia"].append("tryb szkoła bez ramy czasowej (`do GG:MM`): liczę jak sen")
    if rama is not None:
        if rama <= teraz:
            wynik["po_ramie"] = True
        if start < rama < koniec:
            cel = rama
    zakres = cel - start
    uplynelo_s = max(timedelta(0), uplynelo)
    czas_proc = min(100.0, uplynelo_s / zakres * 100) if zakres.total_seconds() > 0 else 100.0
    wynik |= {"czas_proc": round(czas_proc, 1), "limit_proc": round(uzyte, 1),
              "roznica_pp": round(uzyte - czas_proc, 1), "reset": godz(koniec), "start_okna": godz(start),
              "cel": godz(cel)}
    if uzyte > 0 and uplynelo.total_seconds() > 60:
        sto = start + uplynelo * (100 / uzyte)
        wynik["prognoza_100"] = godz(sto)
        wynik["przed_resetem"] = sto < koniec
    if nazwa != "komp":
        wynik["rada"], wynik["wyko"] = rada_okna(wynik["roznica_pp"])
        if wynik.get("po_ramie"):
            wynik["rada"] = "rama minęła: podsumowanie dla szefa, dalej jak w śnie (" + wynik["rada"] + ")"
    return _hamulec(wynik, nazwa, bez_hamulca)


def _hamulec(wynik: dict, nazwa: str, bez_hamulca: bool) -> dict:
    """Hamulec tygodniowy (sen, szkoła): tydzień przed linią o więcej niż 5 pp wygrywa z „dodaj wyko”."""
    r = wynik.get("tydzien_roznica_pp")
    if nazwa != "komp" and not bez_hamulca and r is not None and r > MARGINES_TYGODNIA:
        wynik["rada_tygodnia"] = f"tydzień przed linią o {r:.0f} pp: oszczędniej, bez nowego wyko"
        wynik["rada"] = wynik["rada_tygodnia"]
        wynik["wyko"] = -1
    return wynik


def tekst(w: dict) -> str:
    opis = w["tryb"] + (f" od {w['od']}" if w.get("od") else "") + (f" do {w['do']}" if w.get("do") else "") \
        + (f" ({w['stan']})" if w.get("stan") else "")
    L = [f"Tryb: {opis}"]
    if "limit_proc" in w:
        cel = f", cel 100% o {w['cel']}" if w["cel"] != w["reset"] else ""
        L.append(f"Okno 5 h: minęło {w['czas_proc']:.0f}% czasu do celu (start {w['start_okna']}, reset {w['reset']}{cel}), "
                 f"zużyto {w['limit_proc']:.0f}% limitu, różnica {round(w['roznica_pp']):+d} pp.")
        if "prognoza_100" in w:
            L.append(f"Prognoza: 100% limitu około {w['prognoza_100']}"
                     + (" (przed resetem)." if w["przed_resetem"] else " (po resecie: limit starczy)."))
    if "tydzien_proc" in w:
        L.append(f"Tydzień: minęło {w['tydzien_czas_proc']:.0f}% czasu (reset {w['tydzien_reset']}), "
                 f"zużyto {w['tydzien_proc']:.0f}% limitu, różnica {round(w['tydzien_roznica_pp']):+d} pp.")
    if "rada" in w:
        L.append(f"Rada: {w['rada']}. Wyko: {w['wyko']:+d}.")
    L += [f"Uwaga: {o}." for o in w["ostrzezenia"]]
    return "\n".join(L)


def main() -> int:
    p = argparse.ArgumentParser(description="Tryb pracy i tempo względem limitu 5 h i tygodnia.")
    p.add_argument("--tryb", help="komp|sen|szkola (domyślnie z Stan.md)")
    p.add_argument("--do", metavar="GG:MM", help="koniec ramy (szkoła); nadpisuje Stan.md")
    p.add_argument("--plik", type=Path, default=PLIK_LIMITU)
    p.add_argument("--json", action="store_true")
    p.add_argument("--bez-hamulca", action="store_true", help="bez hamulca tygodniowego (np. testy zużywające tydzień)")
    p.add_argument("--teraz", help="ISO, tylko do testów")
    a = p.parse_args()
    tryb = tryb_ze_stanu(Path.cwd())
    if a.tryb:
        nazwa = tryb_nazwa(a.tryb)
        if not nazwa:
            p.error("tryb: komp, sen albo szkola")
        tryb = {**tryb, "tryb": nazwa} if tryb["tryb"] == nazwa else {**KOMP, "tryb": nazwa}
    if a.do:
        if not re.fullmatch(r"\d{1,2}:\d{2}", a.do):
            p.error("--do w formacie GG:MM")
        tryb["do"] = f"{int(a.do.split(':')[0]):02d}:{a.do.split(':')[1]}"
    try:
        limit = json.loads(a.plik.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        limit = {}
        print("Brak pliku limitu (uruchom Claude Code ze statusline z cyberiady: instaluj.py).", file=sys.stderr)
    teraz = datetime.fromisoformat(a.teraz).astimezone() if a.teraz else datetime.now().astimezone()
    w = licz(limit, teraz, tryb, a.bez_hamulca)
    print(json.dumps(w, ensure_ascii=False, indent=1) if a.json else tekst(w))
    return 0


if __name__ == "__main__":
    sys.exit(main())
