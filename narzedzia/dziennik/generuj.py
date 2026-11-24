"""Generator danych dziennika: z dokumentacji projektu, logów sesji i gita składa jeden plik JSON.

  python -X utf8 narzedzia/dziennik/generuj.py --projekt cyberiada
  ... --sciezka <folder>     folder zamiast nazwy z projekty.yaml (do testów)
  ... --wyjscie <plik>       domyślnie <cyberiada>/_robocze/dziennik/<nazwa>.json

Skąd dane (każdy plik może nie istnieć: wtedy puste pola):
  dokumentacja/Stan.md       puls, bieżąca podróż, tabela wątków, „Czeka na szefa”
  dokumentacja/Zadania.md    zadania (w toku, następnie, zaplanowane, zrobione w tej podróży, odłożone)
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
import zlib
from collections import defaultdict
from collections.abc import Iterator
from datetime import datetime, timedelta
from pathlib import Path

NARZEDZIA = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(NARZEDZIA))
from tempo import PLIK_LIMITU, tempo_nazwa  # noqa: E402
from wspolne import CYBERIADA, projekty, rejestr  # noqa: E402
from wspolne import SESJE_DIR, tytul_sesji  # noqa: E402
import zuzycie  # noqa: E402
from zuzycie import POLA, wazone  # noqa: E402

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
    otwarty = False
    for w in wiersze:
        if w.startswith("#") or (w.strip() and not w[0].isspace() and not w.startswith("- ")):
            # nagłówek (np. `### Ważne`) albo zwykły wiersz bez wcięcia (np. „Gra:”) kończy punkt
            otwarty = False
        elif w.startswith("- "):
            wynik.append([w[2:].strip()])
            otwarty = True
        elif otwarty and w.strip():
            wynik[-1].append(w.rstrip())
    return wynik


def sklej(wiersze: list[str]) -> str:
    return " ".join(w.strip() for w in wiersze if w.strip())


def tabela(wiersze: list[str]) -> list[dict[str, str | None]]:
    """Wiersze tabeli markdown jako słowniki {nazwa kolumny małymi literami: komórka}; bez separatora,
    komórki bez backticków. Brakująca kolumna: `.get` daje None."""
    wynik, naglowek = [], None
    for w in wiersze:
        if not w.strip().startswith("|"):
            continue
        # `|` wewnątrz grawisów nie dzieli komórki
        k = [c.strip().strip("`").strip() for c in re.split(r"\|(?=(?:[^`]*`[^`]*`)*[^`]*$)", w.strip().strip("|"))]
        if all(re.fullmatch(r":?-+:?", c) for c in k):
            continue
        if naglowek is None:
            naglowek = [c.lower() for c in k]
            continue
        wynik.append({n: c or None for n, c in zip(naglowek, k)})
    return wynik


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


def bez_kresek(t: str | None) -> str | None:
    """Pusta komórka albo sama kreska (— – -) to brak wartości."""
    return None if t is None or t.strip() in ("", "—", "–", "-") else t.strip()


def czytaj_stan(projekt: Path) -> dict:
    wstep, sek = sekcje(czytaj(projekt / "dokumentacja" / "Stan.md"))
    m = re.search(r"Archi żył:[ \t]*(.*)", "\n".join(wstep))
    puls = m.group(1).strip() if m else ""
    mt = re.search(r"^\s*(?:[-*]\s*)?\**Tempo:\**[ \t]*([^\s,;.]+)", "\n".join(wstep),
                   re.MULTILINE | re.IGNORECASE)
    podroz = None
    for w in sekcja(sek, "Podróż"):
        if w.strip():
            m = re.match(r"\W*(\d{2,})-([\w-]+)", w)
            if m:
                podroz = (m.group(1), m.group(2).strip("-"))
            break
    watki: dict[str, dict] = {}
    for wiersze in sek.values():  # tabela wątków może być w dowolnej sekcji (np. pod „Podróż”)
        for w in tabela(wiersze):
            if w.get("wątek") and w["wątek"] not in watki:
                watki[w["wątek"]] = {"stan": bez_kresek(w.get("stan")), "galaz": w.get("gałąź"),
                                     "kto": bez_kresek(w.get("kto")), "sesja": bez_kresek(w.get("sesja"))}
    return {"puls": None if puls in ("", "—", "–", "-") else puls,
            "tempo": tempo_nazwa(mt.group(1)) if mt else None,
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
    watki = [{"nazwa": w["wątek"], "kto": w.get("kto"), "plik": w.get("plik"), "stan": w.get("stan")}
             for w in tabela(sekcja(sek, "Wątki")) if w.get("wątek")]
    zadania = re.search(r"Zadania:\s*([^\n·]*)", naglowek)
    podsumowanie = "\n".join(sekcja(sek, "Podsumowanie")).strip()
    return {"start": szukaj(r"Start:\s*(\d{4}-\d{2}-\d{2})"),
            "koniec": szukaj(r"Koniec:\s*(\d{4}-\d{2}-\d{2})"),
            "tryb": szukaj(r"tryb:?\s*(\w+)"),
            "zadania": re.findall(r"Z\d+", zadania.group(1)) if zadania else [], "kryteria": kryteria, "watki": watki,
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
    """Zadania z Zadania.md według sekcji. Zadania między sekcjami przesuwa Archi, generator tylko czyta."""
    _, sek = sekcje(czytaj(projekt / "dokumentacja" / "Zadania.md"))
    return {k: [sklej(p) for p in punkty(sekcja(sek, n))]
            for k, n in (("w_toku", "W toku"), ("nastepnie", "Następnie"), ("zaplanowane", "Zaplanowane"),
                         ("zrobione", "Zrobione w tej podróży"), ("odlozone", "Odłożone"))}


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


def scalenie(projekt: Path, galaz: str, nazwa: str) -> tuple[str, str | None] | None:
    """(czas commita scalenia, czas pierwszego commita scalonej gałęzi) albo None. Scalenie: commit-merge z nazwą
    gałęzi w opisie albo commit „Scalenie <nazwa wątku>…”; start gałęzi tylko dla prawdziwego merge'a."""
    for szukaj in (("--merges", "--fixed-strings", f"--grep={galaz}"),
                   ("--fixed-strings", "--all-match", "--grep=Scalenie", f"--grep={nazwa}")):
        w = git(projekt, "log", *szukaj, "--format=%cI %P")
        if w:
            czas, *rodzice = w[0].split()
            start = None
            if len(rodzice) == 2:
                g = git(projekt, "log", f"{rodzice[0]}..{rodzice[1]}", "--reverse", "--format=%cI")
                start = g[0] if g else None
            return czas, start
    return None


def start_galezi(projekt: Path, galaz: str) -> str | None:
    """Czas pierwszego commita gałęzi (commity spoza main); brak gałęzi albo commitów → None."""
    for baza in ("main", "master"):
        w = git(projekt, "log", f"{baza}..{galaz}", "--reverse", "--format=%cI")
        if w:
            return w[0]
    return None


def koniec_galezi(projekt: Path, galaz: str) -> str | None:
    w = git(projekt, "log", "-1", "--format=%cI", galaz)
    return w[0] if w else None


def lokalny(iso: str) -> datetime:
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone()


# ---------- składanie ----------

def zbuduj_watek(projekt: Path, katalog: Path, numer: str, nazwa: str, kto: str | None, stan: str | None,
                 galaz: str | None, plik: str | None, start_podrozy: str | None) -> dict:
    """Wątek z czasami z gita: start (pierwszy commit gałęzi → dodanie pliku wątku → start podróży)
    i scalenie (commit scalenia → data ostatniego commita gałęzi, gdy stan zaczyna się od „scalone”)."""
    krotka = nazwa.split("/")[-1]
    galaz = galaz or f"worktree-podroz-{numer}-{krotka}"
    plik = (plik or "").strip()
    if not plik or plik.startswith("("):
        plik = f"watek-{krotka}.md"
    plik_wateku = katalog / plik
    ma_galaz = bool(re.fullmatch(r"[\w-]+(/[\w-]+)?", nazwa)) and nazwa.lower() != "archi"
    sc = scalenie(projekt, galaz, nazwa) if ma_galaz else None
    scalono = sc[0] if sc else None
    start = ((start_galezi(projekt, galaz) if ma_galaz else None) or (sc[1] if sc else None)
             or (data_dodania(projekt, plik_wateku) if plik_wateku.exists() else None)
             or data_dodania(projekt, katalog / "plan.md"))
    if not scalono and ma_galaz and (stan or "").lower().startswith("scalon"):
        scalono = koniec_galezi(projekt, galaz)
    return {"nazwa": nazwa, "kto": kto, "stan": stan, "galaz": galaz,
            "start": start or start_podrozy, "scalono": scalono}


def kto_watku(nazwa: str, numer: str, kto_plan: str | None, s: dict, sesje: set[str], projekt: str) -> str:
    """Kto pracuje: kolumna „Kto” (plan, potem Stan.md), `Archi` dla wiersza „Archi”, `wyko`, gdy w logach jest
    sesja wyko-<projekt>-NN-<nazwa> (albo kolumna „Sesja” zaczyna się od wyko-); inaczej „nie wiadomo”."""
    kto = bez_kresek(kto_plan) or s.get("kto")
    if kto:
        return kto
    if nazwa.strip().lower() == "archi":
        return "Archi"
    krotka = nazwa.split("/")[-1]
    if f"wyko-{projekt}-{numer}-{krotka}" in sesje or (s.get("sesja") or "").startswith("wyko-"):
        return "wyko"
    return "nie wiadomo"


def zbuduj_podroz(stan: dict, projekt: Path, plan: dict | None = None, sesje: set[str] | None = None,
                  nazwa_projektu: str = "") -> dict | None:
    if not stan["podroz"]:
        return None
    numer, temat = stan["podroz"]
    katalog = projekt / "dokumentacja" / "podroze" / f"{numer}-{temat}"
    plan = plan or czytaj_plan(katalog)
    sesje = sesje or set()
    watki, widziane = [], set()

    def nazwa_w_stanie(nazwa: str) -> str | None:
        if nazwa in stan["watki"]:
            return nazwa
        krotka = nazwa.split("/")[-1]
        return next((n for n in stan["watki"] if n.split("/")[-1] == krotka), None)

    for w in plan["watki"]:
        n = nazwa_w_stanie(w["nazwa"])
        s = stan["watki"].get(n, {})
        watki.append(zbuduj_watek(projekt, katalog, numer, w["nazwa"],
                                  kto_watku(w["nazwa"], numer, w["kto"], s, sesje, nazwa_projektu),
                                  s.get("stan") or w["stan"] or "nie wiadomo",
                                  s.get("galaz"), w["plik"], plan["start"]))
        widziane.add(n)
    for nazwa, s in stan["watki"].items():
        if nazwa not in widziane:
            watki.append(zbuduj_watek(projekt, katalog, numer, nazwa,
                                      kto_watku(nazwa, numer, None, s, sesje, nazwa_projektu),
                                      s["stan"] or "nie wiadomo", s["galaz"], None, plan["start"]))
    return {"numer": numer, "temat": temat, "start": plan["start"], "tryb": plan["tryb"],
            "kryteria": plan["kryteria"], "watki": watki}


def rola(sesja: str, agent: bool, model: str = "") -> str:
    """Rola do podziału kosztów; model Fable (też agenci na Fable) ma osobną rolę przed resztą."""
    if "fable" in model.lower():
        return "Fable"
    if agent:
        return "agenci"
    if sesja.startswith("archi-"):
        return "Archi"
    return "wyko" if sesja.startswith("wyko-") else "pomo"


def wszystkie_wpisy(katalog: Path | None) -> list[tuple[str, dict]]:
    """Wszystkie wpisy zużycia z dzienników sesji, czytane jeden raz: [(cwd, wpis)]. Pola wpisu jak w `zuzycie.wpisy`."""
    wynik = []
    for plik in (katalog or SESJE_DIR).glob("*/*.jsonl"):
        nazwa = tytul_sesji(plik) or f"(bez nazwy {plik.stem[:8]})"
        zrodla = [(plik, False)] + [(z, True) for z in plik.with_suffix("").glob("subagents/*.jsonl")]
        for zrodlo, agent in zrodla:
            cwdy: list[str] = []
            wpisy_pliku = zuzycie.czytaj(zrodlo, lambda cwd, czas: cwdy.append(cwd or "") or True)  # filtr woła się raz na wpis
            wynik.extend((c, {"sesja": nazwa, "agent": agent, **w}) for c, w in zip(cwdy, wpisy_pliku))
    return wynik


def wpisy_projektu(wsz: list[tuple[str, dict]], projekt: Path | None) -> Iterator[dict]:
    """Wpisy z `wszystkie_wpisy` dla projektu (po cwd, razem z worktree); bez projektu: wszystkie."""
    prefiks = str(projekt.resolve()).lower().replace("/", "\\").rstrip("\\") if projekt else None
    for cwd, w in wsz:
        c = cwd.lower().replace("/", "\\").rstrip("\\")
        if not prefiks or c == prefiks or c.startswith(prefiks + "\\"):
            yield w


PRZERWA = timedelta(minutes=30)
DNI_AKTYWNOSCI = 7


def aktywnosc(projekt: Path, nazwa: str, teraz: datetime, katalog: Path | None, wsz: list | None = None) -> list[dict]:
    """Odcinki pracy sesji z ostatnich 7 dni. Nowy odcinek zaczyna się po przerwie dłuższej niż 30 minut;
    wpisy agentów liczą się do sesji, która ich wywołała. Archi pierwszy, potem wg pierwszego startu."""
    granica = teraz - timedelta(days=DNI_AKTYWNOSCI)
    czasy: dict[str, list[datetime]] = defaultdict(list)
    wsz = wszystkie_wpisy(katalog) if wsz is None else wsz
    for w in wpisy_projektu(wsz, projekt):
        t = lokalny(w["czas"])
        if granica <= t <= teraz:
            czasy[w["sesja"]].append(t)
    wynik = []
    for sesja, lista in czasy.items():
        lista.sort()
        odcinki, start, ostatni = [], lista[0], lista[0]
        for t in lista[1:]:
            if t - ostatni > PRZERWA:
                odcinki.append([start, ostatni])
                start = t
            ostatni = t
        odcinki.append([start, ostatni])
        m = re.fullmatch(rf"wyko-{re.escape(nazwa)}-(\d+)-(.+)", sesja)
        wynik.append({"nazwa": sesja, "rola": rola(sesja, False),
                      "watek": f"{m.group(1)}/{m.group(2)}" if m else None,
                      "odcinki": [[a.isoformat(timespec="seconds"), b.isoformat(timespec="seconds")]
                                  for a, b in odcinki]})
    wynik.sort(key=lambda x: (x["rola"] != "Archi", x["odcinki"][0][0]))
    return wynik


def ostatnie_dni(teraz: datetime) -> list[str]:
    dzis = teraz.date()
    return [(dzis - timedelta(days=i)).isoformat() for i in range(DNI - 1, -1, -1)]


def koszty(projekt: Path, nazwa: str, historia: list[dict], teraz: datetime, katalog: Path | None,
           wsz: list | None = None) -> dict:
    wsz = wszystkie_wpisy(katalog) if wsz is None else wsz
    dni = ostatnie_dni(teraz)
    po_dniach = {d: {"dzien": d, "wazone": 0.0, **{k: 0 for k in POLA}} for d in dni}
    def granica(czas: str | None, dzien: str | None, koniec: bool) -> datetime | None:
        if czas:
            return lokalny(czas)
        if dzien:
            return datetime.fromisoformat(dzien + ("T23:59:59" if koniec else "T00:00:00")).astimezone()
        return None
    zakresy = [(h["numer"], granica(h.get("od"), h["start"], False),
                granica(h.get("do"), h["koniec"], True) or teraz)
               for h in historia if h.get("od") or h["start"]]
    role: dict[tuple[str, str], float] = defaultdict(float)
    # przed pierwszą podróżą: praca sprzed cyberiady (sama cyberiada nie ma „przed”)
    pierwszy = None if nazwa == "cyberiada" else min((od for _, od, _ in zakresy), default=None)
    for w in wpisy_projektu(wsz, projekt):
        chwila = lokalny(w["czas"])
        dzien = chwila.date().isoformat()
        v = wazone(w)
        if dzien in po_dniach:
            d = po_dniach[dzien]
            d["wazone"] += v
            for k in POLA:
                d[k] += w[k]
        m = re.match(rf"wyko-{re.escape(nazwa)}-(\d+)-", w["sesja"])
        podroz = m.group(1) if m else next((n for n, od, do in reversed(zakresy) if od <= chwila <= do),
                                                "przed" if pierwszy and chwila < pierwszy else "poza")
        role[(podroz, rola(w["sesja"], w["agent"], w.get("model") or ""))] += v
    for d in po_dniach.values():
        d["wazone"] = round(d["wazone"])
    return {"dni": [po_dniach[d] for d in dni],
            "role": [{"podroz": p, "rola": r, "wazone": round(v)}
                     for (p, r), v in sorted(role.items(), key=lambda kv: (kv[0][0] in ("poza", "przed"), kv[0]))],
            "okno5h": okno5h(teraz, katalog, wsz)}


def okno5h(teraz: datetime, katalog: Path | None, wsz: list | None = None) -> dict:
    """Okno limitu 5 h ze wszystkich projektów: od pełnej godziny pierwszego wpisu; po końcu okna nowe."""
    granica = teraz - timedelta(hours=24)
    lista = []
    wsz = wszystkie_wpisy(katalog) if wsz is None else wsz
    for w in wpisy_projektu(wsz, None):
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


def ostatnia_podroz(historia: list[dict], biezaca: str | None) -> dict | None:
    """Ostatnia zakończona podróż (nie bieżąca): {nazwa, od, do} albo None."""
    for h in reversed(historia):
        if h["numer"] == biezaca or not h["koniec"]:
            continue
        od = h.get("od") or h["start"]
        do = h.get("do") or h["koniec"]
        # data końca z planu bywa późniejsza niż ostatni commit: wtedy liczy się data z planu
        if od and do and do[:10] < h["koniec"]:
            do = h["koniec"]
        return {"nazwa": f"Podróż {h['numer']}", "od": od, "do": do}
    return None


def limit5h(plik: Path | None) -> dict | None:
    """Limit 5 h z pliku zapisywanego przez statusline.py (wspólny dla projektów) albo None."""
    try:
        d = json.loads((plik or PLIK_LIMITU).read_text(encoding="utf-8"))
        f = d.get("five_hour") or {}
        if f.get("used") is None or not f.get("resets_at"):
            return None
        return {"used": round(float(f["used"]), 1),
                "reset": datetime.fromtimestamp(f["resets_at"]).astimezone().isoformat(timespec="seconds"),
                "czas": d.get("czas")}
    except (OSError, ValueError, TypeError, AttributeError):
        return None


KOLORY_PROJEKTOW = tuple(f"s{i}" for i in range(1, 9))


def kolor_projektu(nazwa: str, kolor: str | None = None) -> str:
    """Stały kolor projektu: `kolor` z projekty.yaml (s1..s8), inaczej z listy według nazwy (nie kolejności)."""
    if kolor in KOLORY_PROJEKTOW:
        return kolor
    return KOLORY_PROJEKTOW[zlib.crc32(nazwa.encode("utf-8")) % len(KOLORY_PROJEKTOW)]


def zbuduj(projekt: Path, nazwa: str, opis: str | None = None, repo: str | None = None,
           teraz: datetime | None = None, katalog_sesji: Path | None = None,
           plik_limitu: Path | None = None, kolor: str | None = None) -> dict:
    teraz = (teraz or datetime.now()).astimezone()
    stan = czytaj_stan(projekt)
    plan_biezacy = None
    wsz = wszystkie_wpisy(katalog_sesji)  # logi czytane raz dla aktywności, kosztów i okna 5 h
    logi = aktywnosc(projekt, nazwa, teraz, katalog_sesji, wsz)
    if stan["podroz"]:
        plan_biezacy = czytaj_plan(projekt / "dokumentacja" / "podroze" / "-".join(stan["podroz"]))
    historia = []
    for numer, temat, d in katalogi_podrozy(projekt):
        p = czytaj_plan(d)
        od = data_dodania(projekt, d / "plan.md")
        do = None
        if p["podsumowanie"]:  # podróż zamknięta: koniec = ostatnia zmiana planu
            w = git(projekt, "log", "-1", "--format=%cI", "--", (d / "plan.md").relative_to(projekt).as_posix())
            do = w[0] if w else None
        koniec = p["koniec"] or (lokalny(do).date().isoformat() if do else None)
        historia.append({"numer": numer, "temat": temat, "start": p["start"], "koniec": koniec,
                         "od": od, "do": do, "podsumowanie": p["podsumowanie"]})
    return {"nazwa": nazwa, "opis": opis, "repo": repo, "kolor": kolor_projektu(nazwa, kolor),
            "wygenerowano": teraz.isoformat(timespec="seconds"), "puls": stan["puls"],
            "tempo": stan["tempo"],
            "podroz": zbuduj_podroz(stan, projekt, plan_biezacy, {x["nazwa"] for x in logi}, nazwa), "czeka": stan["czeka"],
            "decyzje": czytaj_decyzje(projekt), "zadania": czytaj_zadania(projekt),
            "historia": historia, "ostatnia_podroz": ostatnia_podroz(historia, (stan["podroz"] or (None,))[0]),
            "koszty": {**koszty(projekt, nazwa, historia, teraz, katalog_sesji, wsz),
                       "limit": limit5h(plik_limitu) if plik_limitu or katalog_sesji is None else None},
            "commity": commity(projekt, teraz), "aktywnosc": logi}


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
    dane = zbuduj(sciezka, nazwa, meta.get("opis"), meta.get("repo"), kolor=meta.get("kolor"))
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
