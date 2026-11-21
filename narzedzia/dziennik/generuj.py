"""Generator danych dziennika: z dokumentacji projektu, logów sesji i gita składa jeden plik JSON.

  python -X utf8 narzedzia/dziennik/generuj.py --projekt cyberiada
  ... --sciezka <folder>     folder zamiast nazwy z projekty.yaml (do testów)
  ... --wyjscie <plik>       domyślnie <cyberiada>/_robocze/dziennik/<nazwa>.json

Skąd dane (każdy plik może nie istnieć: wtedy puste pola):
  dokumentacja/Stan.md       puls, bieżąca podróż, tabela wątków, „Czeka na szefa”
  dokumentacja/Zadania.md    zadania (w toku, zaplanowane, odłożone)
  dokumentacja/Decyzje.md    decyzje szefa i Archiego
  dokumentacja/podroze/NN-temat/plan.md   podróże: kryteria, wątki, historia
  ~/.claude/projects         zużycie tokenów (przez zuzycie.py): dni, role, okno 5 h
  git                        start i scalenie wątków, commity z 30 dni
Schemat wyniku opisuje brief wątku (dokumentacja/podroze/01-dziennik/watek-generator.md).
Tylko biblioteka standardowa i yaml.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

NARZEDZIA = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(NARZEDZIA))
from wspolne import CYBERIADA, projekty, rejestr  # noqa: E402
from zuzycie import POLA, wazone, wpisy  # noqa: E402

DNI = 30


# ---------- czytanie dokumentów ----------

def czytaj(plik: Path) -> str:
    """Tekst pliku bez komentarzy `<!-- -->`; brak pliku albo błąd odczytu → pusty tekst."""
    try:
        tekst = plik.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    return re.sub(r"<!--.*?-->", "", tekst.replace("\r\n", "\n"), flags=re.DOTALL)


def sekcje(tekst: str) -> tuple[list[str], dict[str, list[str]]]:
    """(wiersze przed pierwszym `## `, {nagłówek `##`: wiersze})."""
    wstep: list[str] = []
    wynik: dict[str, list[str]] = {}
    biezaca = None
    for w in tekst.split("\n"):
        m = re.match(r"##\s+(.*?)\s*$", w)
        if m:
            biezaca = m.group(1)
            wynik.setdefault(biezaca, [])
        elif biezaca is None:
            wstep.append(w)
        else:
            wynik[biezaca].append(w)
    return wstep, wynik


def sekcja(sek: dict[str, list[str]], poczatek: str) -> list[str]:
    """Wiersze sekcji, której nagłówek zaczyna się od `poczatek` (bez względu na wielkość liter)."""
    for nazwa, wiersze in sek.items():
        if nazwa.lower().startswith(poczatek.lower()):
            return wiersze
    return []


def punkty(wiersze: list[str]) -> list[list[str]]:
    """Punkty listy `- ...`: każdy to jego wiersze (pierwszy bez `- `), wcięte kontynuacje doklejone."""
    wynik: list[list[str]] = []
    for w in wiersze:
        if w.startswith("- "):
            wynik.append([w[2:].strip()])
        elif wynik and w.strip():
            wynik[-1].append(w.rstrip())
    return wynik


def sklej(wiersze: list[str]) -> str:
    return " ".join(w.strip() for w in wiersze if w.strip())


def tabela(wiersze: list[str]) -> list[list[str]]:
    """Wiersze tabeli markdown bez nagłówka i separatora; komórki bez backticków."""
    wynik = []
    for w in wiersze:
        if not w.strip().startswith("|"):
            continue
        k = [c.strip().strip("`").strip() for c in w.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", c) for c in k):
            continue
        wynik.append(k)
    return wynik[1:]  # pierwszy wiersz to nagłówek


def komorka(wiersz: list[str], i: int) -> str | None:
    return (wiersz[i] or None) if i < len(wiersz) else None


# ---------- Stan.md ----------

def pytanie(p: list[str]) -> dict:
    m = re.match(r"P(\d+):\s*(.*)", p[0], flags=re.DOTALL)
    if not m:
        return {"id": None, "tresc": sklej(p), "opcje": []}
    tresc, opcje = [m.group(2)], []
    for w in p[1:]:
        o = re.match(r"\s+-\s+([A-Za-z]):\s*(.*)", w)
        if o:
            opcje.append([o.group(1), [o.group(2)]])
        elif opcje:
            opcje[-1][1].append(w)
        else:
            tresc.append(w)
    wynik = []
    for litera, tekst in opcje:
        t = sklej(tekst)
        rek = re.search(r"\s*\(rekomendowane\)\s*$", t, flags=re.IGNORECASE)
        if rek:
            t = t[:rek.start()].rstrip()
        wynik.append({"litera": litera, "tekst": t, "rekomendowana": bool(rek)})
    return {"id": "P" + m.group(1), "tresc": sklej(tresc), "opcje": wynik}


def czytaj_stan(projekt: Path) -> dict:
    wstep, sek = sekcje(czytaj(projekt / "dokumentacja" / "Stan.md"))
    m = re.search(r"Archi żył:[ \t]*(.*)", "\n".join(wstep))
    puls = m.group(1).strip() if m else ""
    podroz = None
    for w in sekcja(sek, "Podróż"):
        if w.strip():
            m = re.match(r"\W*(\d{2,})-([\w-]+)", w)
            if m:
                podroz = (m.group(1), m.group(2).strip("-"))
            break
    watki = {w[0]: {"stan": komorka(w, 3), "galaz": komorka(w, 2)}
             for w in tabela(sekcja(sek, "Wątki")) if w[0]}
    return {"puls": None if puls in ("", "—", "–", "-") else puls,
            "podroz": podroz, "watki": watki,
            "czeka": [pytanie(p) for p in punkty(sekcja(sek, "Czeka na szefa"))]}


# ---------- plan.md, Decyzje.md, Zadania.md ----------

def czytaj_plan(katalog: Path) -> dict:
    wstep, sek = sekcje(czytaj(katalog / "plan.md"))
    naglowek = "\n".join(wstep)

    def szukaj(wzor: str) -> str | None:
        m = re.search(wzor, naglowek)
        return m.group(1) if m else None

    kryteria = []
    for p in punkty(sekcja(sek, "Kryteria sukcesu")):
        m = re.match(r"\[( |x|X)\]\s*(.*)", p[0], flags=re.DOTALL)
        if m:
            kryteria.append({"tekst": sklej([m.group(2)] + p[1:]), "zrobione": m.group(1) != " "})
    watki = [{"nazwa": w[0], "kto": komorka(w, 1), "plik": komorka(w, 2), "stan": komorka(w, 3)}
             for w in tabela(sekcja(sek, "Wątki")) if w[0]]
    podsumowanie = "\n".join(sekcja(sek, "Podsumowanie")).strip()
    return {"start": szukaj(r"Start:\s*(\d{4}-\d{2}-\d{2})"),
            "koniec": szukaj(r"Koniec:\s*(\d{4}-\d{2}-\d{2})"),
            "tryb": szukaj(r"tryb:\s*(\w+)"), "kryteria": kryteria, "watki": watki,
            "podsumowanie": podsumowanie[:600]}


def czytaj_decyzje(projekt: Path) -> dict:
    _, sek = sekcje(czytaj(projekt / "dokumentacja" / "Decyzje.md"))

    def lista(nazwa: str) -> list[dict]:
        wynik = []
        for p in punkty(sekcja(sek, nazwa)):
            tekst = sklej(p)
            m = re.match(r"(\d{4}-\d{2}-\d{2})\s*·\s*(.*)", tekst)
            wynik.append({"data": m.group(1), "tresc": m.group(2)} if m else {"data": None, "tresc": tekst})
        return wynik
    return {"szefa": lista("Szefa"), "archiego": lista("Archiego")}


def czytaj_zadania(projekt: Path) -> dict:
    _, sek = sekcje(czytaj(projekt / "dokumentacja" / "Zadania.md"))
    return {k: [sklej(p) for p in punkty(sekcja(sek, n))]
            for k, n in (("w_toku", "W toku"), ("zaplanowane", "Zaplanowane"), ("odlozone", "Odłożone"))}


def katalogi_podrozy(projekt: Path) -> list[tuple[str, str, Path]]:
    """[(numer, temat, katalog)] posortowane po numerze."""
    wynik = []
    for d in (projekt / "dokumentacja" / "podroze").glob("*"):
        m = re.fullmatch(r"(\d+)-(.+)", d.name)
        if m and d.is_dir():
            wynik.append((m.group(1), m.group(2), d))
    return sorted(wynik, key=lambda x: (int(x[0]), x[1]))


# ---------- git ----------

def git(projekt: Path, *argumenty: str) -> list[str] | None:
    """Wiersze wyniku gita albo None, gdy git zawiódł (brak repo, brak gita)."""
    try:
        w = subprocess.run(["git", *argumenty], cwd=projekt, capture_output=True, text=True, encoding="utf-8")
    except (OSError, ValueError):
        return None
    return [x for x in w.stdout.split("\n") if x.strip()] if w.returncode == 0 else None


def data_dodania(projekt: Path, plik: Path) -> str | None:
    try:
        rel = plik.relative_to(projekt).as_posix()
    except ValueError:
        return None
    w = git(projekt, "log", "--diff-filter=A", "--format=%cI", "--", rel)
    return w[-1] if w else None


def data_scalenia(projekt: Path, galaz: str) -> str | None:
    w = git(projekt, "log", "--merges", "--fixed-strings", f"--grep={galaz}", "--format=%cI")
    return w[0] if w else None


def lokalny(iso: str) -> datetime:
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone()


# ---------- składanie ----------

def zbuduj_podroz(stan: dict, projekt: Path) -> dict | None:
    if not stan["podroz"]:
        return None
    numer, temat = stan["podroz"]
    katalog = projekt / "dokumentacja" / "podroze" / f"{numer}-{temat}"
    plan = czytaj_plan(katalog)
    watki, widziane = [], set()
    for w in plan["watki"]:
        s = stan["watki"].get(w["nazwa"], {})
        galaz = s.get("galaz")
        plik = (w["plik"] or "").strip()
        sciezka = katalog / plik if plik and not plik.startswith("(") else None
        start = data_dodania(projekt, sciezka) if sciezka else None
        watki.append({"nazwa": w["nazwa"], "kto": w["kto"], "stan": s.get("stan") or w["stan"],
                      "galaz": galaz, "start": start or plan["start"],
                      "scalono": data_scalenia(projekt, galaz) if galaz else None})
        widziane.add(w["nazwa"])
    for nazwa, s in stan["watki"].items():
        if nazwa not in widziane:
            watki.append({"nazwa": nazwa, "kto": None, "stan": s["stan"], "galaz": s["galaz"],
                          "start": plan["start"],
                          "scalono": data_scalenia(projekt, s["galaz"]) if s["galaz"] else None})
    return {"numer": numer, "temat": temat, "start": plan["start"], "tryb": plan["tryb"],
            "kryteria": plan["kryteria"], "watki": watki}


def rola(sesja: str, agent: bool) -> str:
    if agent:
        return "agenci"
    if sesja.startswith("archi-"):
        return "Archi"
    return "wyko" if sesja.startswith("wyko-") else "Pomocnik"


def ostatnie_dni(teraz: datetime) -> list[str]:
    dzis = teraz.date()
    return [(dzis - timedelta(days=i)).isoformat() for i in range(DNI - 1, -1, -1)]


def koszty(projekt: Path, nazwa: str, historia: list[dict], teraz: datetime, katalog: Path | None) -> dict:
    dni = ostatnie_dni(teraz)
    po_dniach = {d: {"dzien": d, "wazone": 0.0, **{k: 0 for k in POLA}} for d in dni}
    zakresy = [(h["numer"], h["start"], h["koniec"] or teraz.date().isoformat())
               for h in historia if h["start"]]
    role: dict[tuple[str, str], float] = defaultdict(float)
    for w in wpisy(projekt, katalog):
        dzien = lokalny(w["czas"]).date().isoformat()
        v = wazone(w)
        if dzien in po_dniach:
            d = po_dniach[dzien]
            d["wazone"] += v
            for k in POLA:
                d[k] += w[k]
        m = re.match(rf"wyko-{re.escape(nazwa)}-(\d+)-", w["sesja"])
        podroz = m.group(1) if m else next((n for n, od, do in zakresy if od <= dzien <= do), "poza")
        role[(podroz, rola(w["sesja"], w["agent"]))] += v
    for d in po_dniach.values():
        d["wazone"] = round(d["wazone"])
    return {"dni": [po_dniach[d] for d in dni],
            "role": [{"podroz": p, "rola": r, "wazone": round(v)}
                     for (p, r), v in sorted(role.items(), key=lambda kv: (kv[0][0] == "poza", kv[0]))],
            "okno5h": okno5h(teraz, katalog)}


def okno5h(teraz: datetime, katalog: Path | None) -> dict:
    """Okno limitu 5 h ze wszystkich projektów: od pełnej godziny pierwszego wpisu; po końcu okna nowe."""
    granica = teraz - timedelta(hours=24)
    lista = []
    for w in wpisy(None, katalog):
        t = lokalny(w["czas"])
        if granica <= t <= teraz:
            lista.append((t, wazone(w)))
    lista.sort(key=lambda x: x[0])
    start = koniec = None
    suma = 0.0
    for t, v in lista:
        if koniec is None or t >= koniec:
            start = t.replace(minute=0, second=0, microsecond=0)
            koniec, suma = start + timedelta(hours=5), 0.0
        suma += v
    if koniec is None or not start <= teraz < koniec:
        return {"od": None, "reset": None, "wazone": 0}
    return {"od": start.isoformat(timespec="seconds"), "reset": koniec.isoformat(timespec="seconds"),
            "wazone": round(suma)}


def commity(projekt: Path, teraz: datetime) -> list[dict]:
    w = git(projekt, "log", "--all", "--format=%cI")
    if w is None:
        return []
    licznik: dict[str, int] = defaultdict(int)
    for iso in w:
        licznik[lokalny(iso).date().isoformat()] += 1
    return [{"dzien": d, "liczba": licznik.get(d, 0)} for d in ostatnie_dni(teraz)]


def zbuduj(projekt: Path, nazwa: str, opis: str | None = None, repo: str | None = None,
           teraz: datetime | None = None, katalog_sesji: Path | None = None) -> dict:
    teraz = (teraz or datetime.now()).astimezone()
    stan = czytaj_stan(projekt)
    historia = []
    for numer, temat, d in katalogi_podrozy(projekt):
        p = czytaj_plan(d)
        historia.append({"numer": numer, "temat": temat, "start": p["start"], "koniec": p["koniec"],
                         "podsumowanie": p["podsumowanie"]})
    return {"nazwa": nazwa, "opis": opis, "repo": repo,
            "wygenerowano": teraz.isoformat(timespec="seconds"), "puls": stan["puls"],
            "podroz": zbuduj_podroz(stan, projekt), "czeka": stan["czeka"],
            "decyzje": czytaj_decyzje(projekt), "zadania": czytaj_zadania(projekt),
            "historia": historia, "koszty": koszty(projekt, nazwa, historia, teraz, katalog_sesji),
            "commity": commity(projekt, teraz)}


def main() -> int:
    p = argparse.ArgumentParser(description="Dane dziennika projektu (JSON).")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--projekt", help="nazwa z projekty.yaml")
    g.add_argument("--sciezka", type=Path, help="folder zamiast nazwy (do testów)")
    p.add_argument("--wyjscie", type=Path)
    a = p.parse_args()
    znane = projekty()
    if a.projekt:
        if a.projekt not in znane:
            print(f"Nieznany projekt: {a.projekt} (znane: {', '.join(znane) or 'brak'})", file=sys.stderr)
            return 1
        nazwa, sciezka = a.projekt, znane[a.projekt]
    else:
        sciezka = a.sciezka.resolve()
        nazwa = next((n for n, s in znane.items() if s.resolve() == sciezka), sciezka.name)
    meta = (rejestr().get("projekty") or {}).get(nazwa) or {}
    dane = zbuduj(sciezka, nazwa, meta.get("opis"), meta.get("repo"))
    wyjscie = a.wyjscie or CYBERIADA / "_robocze" / "dziennik" / f"{nazwa}.json"
    wyjscie.parent.mkdir(parents=True, exist_ok=True)
    with open(wyjscie, "w", encoding="utf-8", newline="\n") as f:
        json.dump(dane, f, ensure_ascii=False, indent=1)
        f.write("\n")
    watki = len((dane["podroz"] or {}).get("watki", []))
    print(f"zapisano {wyjscie} · czeka {len(dane['czeka'])} · wątki {watki} · "
          f"dni kosztów {len(dane['koszty']['dni'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
