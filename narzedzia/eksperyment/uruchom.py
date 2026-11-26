"""Eksperyment Z10: te same prawdziwe zadania z historii powtarzane w różnych ustawieniach.

Mierzy tokeny (ważone jak w dzienniku), czas i jakość (testy + ocena 1-5), żeby ustawić tryby sen i komp.
  python -X utf8 narzedzia/eksperyment/uruchom.py --pokaz            # plan, stopy, szacunek (bez uruchamiania)
  python -X utf8 narzedzia/eksperyment/uruchom.py                    # start (nowy plik wyników)
  python -X utf8 narzedzia/eksperyment/uruchom.py --wznow            # dokończ po przerwie (pomija zrobione)
Opis: narzedzia/eksperyment/README.md
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import stat
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path

NARZEDZIA = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(NARZEDZIA))
import zuzycie  # noqa: E402
from wspolne import SESJE_DIR, claude_exe  # noqa: E402
from wyko import wspolne_flagi  # noqa: E402

EKS = Path(__file__).resolve().parent
KORZEN = NARZEDZIA.parent
WYNIKI = KORZEN / "_robocze" / "eksperyment" / "wyniki.jsonl"
KATALOG = Path.home() / "eksperyment"  # poza każdym repo: sesja nie wczyta CLAUDE.md z folderu nadrzędnego
LIMIT_PLIK = Path.home() / ".claude" / "cyberiada-limit.json"
BUDZET = 45_000_000
DO = "2026-11-29T16:00"
LIMIT_ZDROWY_MIN = 15
MAX_CZAS_S = 90 * 60
MAX_CZAS_TESTOW_S = 25 * 60
MAX_POWTORZEN_LIMITU = 20
EFFORT_WSPOLCZYNNIK = {"low": 0.7, "medium": 1.0, "high": 1.5, "xhigh": 2.0, "max": 2.5}
MAX_DIFF = 40_000


def w_repo(sciezka: Path) -> bool:
    """Czy folder leży w jakimś repo albo w folderze cyberiady (sesja wczytałaby stamtąd CLAUDE.md)."""
    p = sciezka.resolve()
    cyberiada = Path.home().resolve() / "cyberiada"
    return any((x / ".git").exists() or x == cyberiada for x in [p, *p.parents])


def czytaj_json(sciezka: Path) -> dict:
    return json.loads(sciezka.read_text(encoding="utf-8"))


def teraz() -> datetime:
    return datetime.now().astimezone()


def parsuj_czas(tekst: str) -> datetime:
    t = datetime.fromisoformat(tekst)
    return t if t.tzinfo else t.astimezone()


def parsuj_budzet(tekst: str) -> int:
    t = tekst.strip().lower().replace(",", ".").replace("_", "")
    mnoznik = 1
    if t.endswith("m"):
        mnoznik, t = 1_000_000, t[:-1]
    elif t.endswith("k"):
        mnoznik, t = 1_000, t[:-1]
    return int(float(t) * mnoznik)


# ---------- plan ----------

def rozwin_plan(plan: dict, zadania: list[dict]) -> list[dict]:
    """Lista przebiegów w kolejności ważności (grupy po kolei, bez powtórzeń identyfikatorów)."""
    wynik, widziane = [], set()
    for grupa in plan["grupy"]:
        ids = []
        for z in grupa["zadania"]:
            if z in ("male", "duze"):
                ids += [x["id"] for x in zadania if x["wielkosc"] == z]
            elif z == "wszystkie":
                ids += [x["id"] for x in zadania]
            else:
                ids.append(z)
        po_id = {x["id"]: x for x in zadania}
        for zid in ids:
            for model in grupa["modele"]:
                for effort in grupa["effort"]:
                    for ac in grupa.get("autocompact", ["200k"]):
                        n = grupa.get("powtorzenie", 1)
                        rid = f"{zid}-{model}-{effort}-{ac}-p{n}"
                        if rid in widziane:
                            continue
                        widziane.add(rid)
                        wynik.append({"id": rid, "zadanie": zid, "wielkosc": po_id[zid]["wielkosc"], "model": model,
                                      "effort": effort, "autocompact": ac, "powtorzenie": n,
                                      "grupa": grupa.get("opis", "")})
    return wynik


def szacunek(spec: dict, zadanie: dict) -> float:
    """Zgrubny szacunek ważonych tokenów jednego przebiegu (z oryginalnej sesji; do poprawy po pierwszych wynikach)."""
    baza = zadanie.get("oryginal", {}).get("wazone_mln", 1.0) * 1e6
    return baza * zuzycie.mnoznik(spec["model"]) * EFFORT_WSPOLCZYNNIK.get(spec["effort"], 1.0) * 1.3 + 150_000


# ---------- wyniki i stopy ----------

def wczytaj_wyniki(plik: Path) -> list[dict]:
    if not plik.is_file():
        return []
    wynik = []
    for linia in plik.read_text(encoding="utf-8").splitlines():
        try:
            wynik.append(json.loads(linia))
        except ValueError:
            continue  # urwana linia po przerwaniu
    return wynik


def suma_wazone(wyniki: list[dict]) -> float:
    return sum((w.get("tokeny_wazone") or 0) + (w.get("ocena_wazone") or 0) for w in wyniki)


def stan_limitu(plik: Path, teraz_: datetime) -> dict | None:
    """Zawartość pliku limitu, gdy świeża (do 15 min); inaczej None."""
    try:
        d = json.loads(plik.read_text(encoding="utf-8"))
        czas = parsuj_czas(d["czas"])
    except (OSError, ValueError, KeyError, TypeError):
        return None
    return d if teraz_ - czas <= timedelta(minutes=LIMIT_ZDROWY_MIN) else None


def powod_stopu(wyniki: list[dict], budzet: float, do: datetime, teraz_: datetime, limit_plik: Path) -> str | None:
    suma = suma_wazone(wyniki)
    if suma >= budzet:
        return f"budżet: {suma / 1e6:.1f}M ≥ {budzet / 1e6:.1f}M tokenów ważonych"
    d = stan_limitu(limit_plik, teraz_)
    if d:
        uzyte = (d.get("seven_day") or {}).get("used")
        if isinstance(uzyte, (int, float)) and uzyte >= 95:
            return f"limit tygodnia: seven_day.used = {uzyte} ≥ 95"
    if teraz_ >= do:
        return f"minął termin {do:%Y-%m-%d %H:%M}"
    return None


def kompletny(w: dict) -> bool:
    return bool(w.get("kompletny"))


# ---------- limit 5 h ----------

def to_limit_5h(dane: dict | None, tekst: str) -> bool:
    t = ((dane or {}).get("result") or "") + " " + tekst
    if dane and dane.get("api_error_status") == 429:
        return True
    return bool(re.search(r"(usage|rate|session|5[- ]?hour)\s+limit|limit\s+(reached|will reset)|hit your limit", t, re.I)
                ) and bool((dane or {}).get("is_error", True))


def sekundy_do_resetu(limit_plik: Path, teraz_: datetime) -> int:
    """Do resetu okna 5 h: z pliku limitu (five_hour.resets_at), inaczej 15 min."""
    d = stan_limitu(limit_plik, teraz_)
    try:
        reset = float(d["five_hour"]["resets_at"]) if d else 0
    except (KeyError, TypeError, ValueError):
        reset = 0
    reszta = reset - teraz_.timestamp()
    return int(reszta) + 60 if reszta > 0 else 15 * 60


# ---------- git ----------

def git(repo: Path | str, *args: str, timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout)


def usun_katalog(sciezka: Path) -> None:
    def popraw(fun, p, _):
        Path(p).chmod(stat.S_IWRITE)
        fun(p)
    if sciezka.exists():
        shutil.rmtree(sciezka, onerror=popraw)


def przygotuj_kopie(zadanie: dict, folder: Path) -> None:
    """Klon repo poza każdym repo, commit startowy, bez zdalnego origin."""
    usun_katalog(folder)
    folder.parent.mkdir(parents=True, exist_ok=True)
    w = subprocess.run(["git", "clone", "-q", "--no-checkout", zadanie["repo"], str(folder)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
    if w.returncode:
        raise RuntimeError(f"git clone: {w.stderr.strip()[-300:]}")
    for polecenie in (["checkout", "-q", "-b", "eksperyment", zadanie["start"]], ["remote", "remove", "origin"]):
        w = git(folder, *polecenie)
        if w.returncode:
            raise RuntimeError(f"git {' '.join(polecenie)}: {w.stderr.strip()[-300:]}")


def brief_zadania(zadanie: dict) -> str:
    """Sekcja Brief pliku wątku z commitu wzorcowego (bez Raportu)."""
    w = git(zadanie["repo"], "show", f"{zadanie['wzorzec']}:{zadanie['plik_watku']}")
    if w.returncode:
        raise RuntimeError(f"brak pliku wątku: {w.stderr.strip()[-200:]}")
    return brief_z_tekstu(w.stdout)


def brief_z_tekstu(tekst: str) -> str:
    m = re.search(r"^## Brief\s*\n(.*?)(?=^## Raport|\Z)", tekst, re.S | re.M)
    return (m.group(1) if m else tekst).strip()


POMIN = (":(exclude)dokumentacja/podroze", ":(exclude)_robocze")


def koniec_watku(repo: str, wzorzec: str) -> str:
    """Wzorzec to scalenie: zmiany wątku kończą się na jego drugim rodzicu (pierwszy niesie cudze prace)."""
    rodzice = git(repo, "rev-list", "--parents", "-n1", wzorzec).stdout.split()
    return rodzice[2] if len(rodzice) > 2 else wzorzec


def diff_wzorcowy(zadanie: dict) -> str:
    koniec = koniec_watku(zadanie["repo"], zadanie["wzorzec"])
    return git(zadanie["repo"], "diff", zadanie["start"], koniec, "--", ".", *POMIN).stdout


def diff_przebiegu(folder: Path, start: str) -> str:
    git(folder, "add", "-A")
    return git(folder, "diff", "--cached", start, "--", ".", *POMIN).stdout


def polecenie_testow(zadanie: dict) -> list[str]:
    return [zadanie["python"] if a == "{python}" else a for a in zadanie["testy"]]


def prompt_przebiegu(brief: str, zadanie: dict) -> str:
    testy = " ".join(f'"{a}"' if " " in a else a for a in polecenie_testow(zadanie))
    return (
        "To jest zadanie do wykonania w tym repozytorium (jest to kopia do eksperymentu: nie ma pliku wątku ani raportu, "
        "brief jest poniżej). Zrób zadanie z briefu, uruchom testy i zacommituj zmiany "
        "(`git -c user.name=Tom-Wasko commit`, bez dopisków o AI). Nie rób zrzutów ekranu i nie uruchamiaj serwerów. "
        f"Nie ma sieci i zdalnego repo; nie pisz do plików poza tym repozytorium.\n"
        f"Testy uruchamiasz poleceniem (katalog: {zadanie['testy_cwd']}): {testy}\n"
        "Na końcu odpowiedz krótko: co zrobiłeś i wynik testów.\n\n"
        f"=== BRIEF ===\n{brief}\n"
    )


# ---------- claude ----------

def uruchom_proces(polecenie: list[str], cwd: Path, wejscie: str | None, limit_s: int) -> tuple[int, str, str, bool]:
    p = subprocess.Popen(polecenie, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, encoding="utf-8", errors="replace")
    try:
        out, err = p.communicate(wejscie, timeout=limit_s)
        return p.returncode, out, err, False
    except subprocess.TimeoutExpired:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
        else:
            p.kill()
        out, err = p.communicate()
        return -1, out or "", err or "", True


def parsuj_odpowiedz(stdout: str) -> dict | None:
    """Ostatni obiekt JSON ze stdout (--output-format json)."""
    for linia in reversed(stdout.strip().splitlines()):
        try:
            d = json.loads(linia)
        except ValueError:
            continue
        if isinstance(d, dict):
            return d
    try:
        d = json.loads(stdout)
        return d if isinstance(d, dict) else None
    except ValueError:
        return None


def tokeny_z_logu(session_id: str, katalog_logow: Path = SESJE_DIR) -> dict | None:
    """Tokeny sesji z jej dziennika (razem z podagentami), funkcjami zuzycie.py: ważone i surowe."""
    pliki = list(katalog_logow.glob(f"*/{session_id}.jsonl"))
    if not pliki:
        return None
    zrodla = [pliki[0], *sorted(pliki[0].with_suffix("").glob("subagents/*.jsonl"))]
    razem = {"wazone": 0.0, "surowe": 0, "wpisy": 0, "modele": {}}
    for zrodlo in zrodla:
        for w in zuzycie.czytaj(zrodlo, lambda _c, _t: True):
            razem["wazone"] += zuzycie.wazone(w)
            razem["surowe"] += sum(w[k] for k in zuzycie.POLA)
            razem["wpisy"] += 1
            razem["modele"][w["model"]] = razem["modele"].get(w["model"], 0) + 1
    return razem


def policz_testy(rc: int, tekst: str, przekroczono: bool) -> dict:
    ogon = tekst.strip().splitlines()[-1] if tekst.strip() else ""
    liczby = {}
    for klucz, wzor in (("zaliczone", r"(\d+) passed"), ("niezaliczone", r"(\d+) failed"), ("bledy", r"(\d+) errors?")):
        m = re.search(wzor, tekst)
        if m:
            liczby[klucz] = int(m.group(1))
    m = re.search(r"Ran (\d+) tests?", tekst)
    if m:
        liczby["uruchomione"] = int(m.group(1))
        m = re.search(r"FAILED \((.*?)\)", tekst)
        if m:
            liczby["niezaliczone"] = sum(int(x) for x in re.findall(r"=(\d+)", m.group(1)))
    return {"zaliczone": rc == 0 and not przekroczono, "kod": rc, "przekroczono_czas": przekroczono,
            "liczby": liczby, "ostatnia_linia": ogon[:200]}


def prompt_oceny(brief: str, diff: str, wzor: str, testy: dict, tekst_testow: str) -> str:
    def przytnij(t: str) -> str:
        return t if len(t) <= MAX_DIFF else t[:MAX_DIFF] + "\n[...przycięte...]"
    return (
        "Jesteś recenzentem. Oceń wykonanie zadania przez inny model. Nie zmieniasz kodu, nie używasz narzędzi. "
        "Porównaj DIFF PRZEBIEGU z DIFFEM WZORCOWYM (to, co naprawdę scalono) w świetle BRIEFU i WYNIKU TESTÓW. "
        "Oceń 1-5: 5 = cel z briefu spełniony w całości, dobra jakość, bez zbędnych zmian; 4 = spełniony, drobne braki; "
        "3 = częściowo; 2 = poważne braki lub błędy; 1 = nie zrobione albo szkodliwe. "
        "Pusty diff przebiegu to ocena 1. Nie karz za inne, równie dobre rozwiązanie niż wzorcowe.\n"
        'Odpowiedz WYŁĄCZNIE jednym obiektem JSON: {"ocena": <1-5>, "uzasadnienie": "<do 3 zdań po polsku>"}\n\n'
        f"=== BRIEF ===\n{brief}\n\n=== WYNIK TESTÓW ===\nzaliczone: {testy['zaliczone']}\n"
        f"{tekst_testow.strip()[-1500:]}\n\n=== DIFF PRZEBIEGU ===\n{przytnij(diff) or '(pusty)'}\n\n"
        f"=== DIFF WZORCOWY ===\n{przytnij(wzor)}\n")


def parsuj_ocene(tekst: str) -> tuple[int, str] | None:
    m = re.search(r'\{[^{}]*"ocena"[^{}]*\}', tekst or "", re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
        ocena = int(d["ocena"])
    except (ValueError, KeyError, TypeError):
        return None
    return (ocena, str(d.get("uzasadnienie", ""))) if 1 <= ocena <= 5 else None


# ---------- przebieg ----------

class Kontekst:
    def __init__(self, a: argparse.Namespace, zadania: dict[str, dict], wyniki: list[dict]):
        self.a = a
        self.zadania = zadania
        self.wyniki = wyniki
        self.blokada = threading.Lock()
        self.stop: str | None = None

    def powod_stopu(self) -> str | None:
        with self.blokada:
            return powod_stopu(self.wyniki, self.a.budzet, parsuj_czas(self.a.do), teraz(), LIMIT_PLIK)

    def zapisz(self, wpis: dict) -> None:
        with self.blokada:
            self.wyniki[:] = [w for w in self.wyniki if w["id"] != wpis["id"]] + [wpis]
            self.a.wyniki.parent.mkdir(parents=True, exist_ok=True)
            with open(self.a.wyniki, "a", encoding="utf-8") as f:
                f.write(json.dumps(wpis, ensure_ascii=False) + "\n")


def przebieg(spec: dict, ctx: Kontekst) -> dict | None:
    zadanie = ctx.zadania[spec["zadanie"]]
    folder = ctx.a.katalog / spec["id"]
    wpis = {k: spec[k] for k in ("id", "zadanie", "wielkosc", "model", "effort", "autocompact", "powtorzenie")}
    wpis.update({"start": teraz().isoformat(timespec="seconds"), "bledy": [], "proby": 0, "kompletny": False})
    try:
        przygotuj_kopie(zadanie, folder)
        brief = brief_zadania(zadanie)
        prompt = prompt_przebiegu(brief, zadanie)
        dane = None
        for proba in range(1, MAX_POWTORZEN_LIMITU + 1):
            wpis["proby"] = proba
            if proba > 1 and (powod := ctx.powod_stopu()):
                ctx.stop = ctx.stop or powod
                wpis["bledy"].append(f"przerwano przed powtórką po limicie: {powod}")
                break
            t0 = time.time()
            polecenie = [claude_exe(), "-p", "--output-format", "json", "--name", f"eks-{spec['id']}",
                         *wspolne_flagi(spec["model"], spec["effort"], spec["autocompact"])]
            rc, out, err, przekroczono = uruchom_proces(polecenie, folder, prompt, MAX_CZAS_S)
            wpis["czas_s"] = round(time.time() - t0)
            dane = parsuj_odpowiedz(out)
            if przekroczono:
                wpis["bledy"].append(f"przekroczono limit czasu {MAX_CZAS_S // 60} min")
                break
            if to_limit_5h(dane, err) and (dane is None or dane.get("is_error")):
                czekaj = sekundy_do_resetu(LIMIT_PLIK, teraz())
                wpis["bledy"].append(f"limit 5 h (próba {proba}): czekam {czekaj // 60} min")
                przygotuj_kopie(zadanie, folder)  # powtórka od zera
                time.sleep(czekaj)
                continue
            break
        if dane is None:
            wpis["bledy"].append("brak JSON z claude -p: " + (out or err)[-200:].strip())
        else:
            wpis.update({"session_id": dane.get("session_id"), "tury": dane.get("num_turns"),
                         "czas_api_s": round((dane.get("duration_api_ms") or 0) / 1000),
                         "koszt_usd": dane.get("total_cost_usd"), "usage_json": dane.get("usage"),
                         "blad_claude": bool(dane.get("is_error")), "koniec": dane.get("terminal_reason")})
            if dane.get("is_error"):
                wpis["bledy"].append("claude zgłosił błąd: " + str(dane.get("result"))[:200])
            tok = tokeny_z_logu(dane["session_id"]) if dane.get("session_id") else None
            if tok:
                wpis.update({"tokeny_wazone": round(tok["wazone"]), "tokeny_surowe": tok["surowe"]})
            else:
                wpis["bledy"].append("brak dziennika sesji w ~/.claude/projects")
        # jakość: testy
        rc, out, err, przekroczono = uruchom_proces(polecenie_testow(zadanie), folder / zadanie["testy_cwd"], None,
                                                    MAX_CZAS_TESTOW_S)
        tekst_testow = out + "\n" + err
        wpis["testy"] = policz_testy(rc, tekst_testow, przekroczono)
        diff = diff_przebiegu(folder, zadanie["start"])
        wpis["diff_linie"] = len(diff.splitlines())
        # jakość: ocena
        wpis.update(ocen(brief, diff, diff_wzorcowy(zadanie), wpis["testy"], tekst_testow, spec["id"], ctx.a.katalog))
        wpis["kompletny"] = (wpis.get("tokeny_wazone") is not None and wpis.get("ocena") is not None
                             and not wpis["bledy"])
    except Exception as e:  # noqa: BLE001 - jeden przebieg nie zatrzymuje reszty
        wpis["bledy"].append(f"{type(e).__name__}: {e}"[:300])
    finally:
        if not ctx.a.zachowaj:
            usun_katalog(folder)
    ctx.zapisz(wpis)
    return wpis


def ocen(brief: str, diff: str, wzor: str, testy: dict, tekst_testow: str, rid: str, katalog: Path) -> dict:
    """Osobny `claude -p --model sonnet`: ocena 1-5. Jego tokeny osobno (ocena_*)."""
    wynik: dict = {"ocena": None, "uzasadnienie": None, "ocena_wazone": 0, "ocena_surowe": 0, "koszt_oceny_usd": None}
    neutralny = katalog / "_ocena"
    neutralny.mkdir(parents=True, exist_ok=True)
    polecenie = [claude_exe(), "-p", "--output-format", "json", "--model", "sonnet", "--effort", "medium",
                 "--name", f"eks-{rid}-ocena", "--no-chrome", "--disable-slash-commands", "--tools", ""]
    rc, out, err, przekroczono = uruchom_proces(polecenie, neutralny, prompt_oceny(brief, diff, wzor, testy,
                                                                                tekst_testow), 15 * 60)
    dane = parsuj_odpowiedz(out)
    if not dane:
        wynik["blad_oceny"] = ("przekroczono czas" if przekroczono else (out or err)[-200:].strip()) or "brak odpowiedzi"
        return wynik
    wynik["koszt_oceny_usd"] = dane.get("total_cost_usd")
    tok = tokeny_z_logu(dane["session_id"]) if dane.get("session_id") else None
    if tok:
        wynik.update({"ocena_wazone": round(tok["wazone"]), "ocena_surowe": tok["surowe"]})
    ocena = parsuj_ocene(dane.get("result", ""))
    if ocena:
        wynik["ocena"], wynik["uzasadnienie"] = ocena
    else:
        wynik["blad_oceny"] = "nie udało się odczytać oceny: " + str(dane.get("result"))[:150]
    return wynik


# ---------- pokaz i main ----------

def pokaz(przebiegi: list[dict], ctx: Kontekst, zrobione: set[str]) -> None:
    a = ctx.a
    opisy = [f"{z['id']} ({z['wielkosc']}, {z['projekt']})" for z in ctx.zadania.values()]
    print("Zadania: " + ", ".join(opisy))
    print(f"Plan: {a.plan.name}, {len(przebiegi)} przebiegów, zrobionych: {len(zrobione & {p['id'] for p in przebiegi})}")
    suma = 0.0
    grupa = None
    for i, p in enumerate(przebiegi, 1):
        if p["grupa"] != grupa:
            grupa = p["grupa"]
            print(f"\n== {grupa or '(grupa)'}")
        s = szacunek(p, ctx.zadania[p["zadanie"]])
        znak = "zrobiony" if p["id"] in zrobione else f"~{s / 1e6:.1f}M"
        if p["id"] not in zrobione:
            suma += s
        print(f"{i:3}. {p['id']:<34} {p['wielkosc']:<5} {znak}")
    print(f"\nSzacowany koszt niezrobionych: ~{suma / 1e6:.0f}M ważonych (zgrubnie: oryginał × model × effort × 1,3 "
          f"+ ocena; popraw po pierwszych wynikach)")
    print("Stopy:")
    print(f"  budżet:  {a.budzet / 1e6:.0f}M ważonych (zużyte dotąd: {suma_wazone(ctx.wyniki) / 1e6:.1f}M)")
    print(f"  termin:  {parsuj_czas(a.do):%Y-%m-%d %H:%M}")
    d = stan_limitu(LIMIT_PLIK, teraz())
    uzyte = (d or {}).get("seven_day", {}).get("used") if d else None
    print(f"  limit:   stop przy seven_day.used ≥ 95 (plik limitu {'świeży, teraz ' + str(uzyte) if d else 'nieświeży albo brak: pomijam'})")
    print(f"  naraz:   {a.naraz}, limit czasu przebiegu {MAX_CZAS_S // 60} min, limit 5 h: czeka do resetu i powtarza")
    print(f"  kopie:   {a.katalog}/<id>  ·  wyniki: {a.wyniki}")
    stop = ctx.powod_stopu()
    print(f"Stop teraz: {stop or 'brak'}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Eksperyment Z10: powtórki prawdziwych zadań w różnych ustawieniach.")
    p.add_argument("--plan", type=Path, default=EKS / "plan.json")
    p.add_argument("--zadania", type=Path, default=EKS / "zadania.json")
    p.add_argument("--wyniki", type=Path, default=WYNIKI)
    p.add_argument("--katalog", type=Path, default=KATALOG, help="gdzie powstają kopie (poza repo)")
    p.add_argument("--budzet", type=parsuj_budzet, default=BUDZET, help="stop: suma ważonych (np. 45M, 2M)")
    p.add_argument("--do", default=DO, help="stop: termin (ISO, np. 2026-11-29T16:00)")
    p.add_argument("--naraz", type=int, default=3)
    p.add_argument("--wznow", action="store_true", help="dopisz do wyników, pomiń zrobione")
    p.add_argument("--nowy", action="store_true", help="odłóż stary plik wyników i zacznij od zera")
    p.add_argument("--zachowaj", action="store_true", help="nie usuwaj kopii po przebiegu")
    p.add_argument("--pokaz", action="store_true", help="tylko plan, stopy i szacunek")
    a = p.parse_args(argv)
    if w_repo(a.katalog):
        raise SystemExit("--katalog musi leżeć poza każdym repo i poza folderem cyberiady.")

    zadania_lista = czytaj_json(a.zadania)["zadania"]
    przebiegi = rozwin_plan(czytaj_json(a.plan), zadania_lista)
    if a.nowy and a.wyniki.is_file() and not a.pokaz:
        a.wyniki.rename(a.wyniki.with_name(f"wyniki-{datetime.now():%Y%m%d-%H%M%S}.jsonl"))
    wyniki = wczytaj_wyniki(a.wyniki)
    if wyniki and not (a.wznow or a.pokaz):
        raise SystemExit(f"{a.wyniki} już istnieje: użyj --wznow (dokończ) albo --nowy (od zera).")
    zrobione = {w["id"] for w in wyniki if kompletny(w)}
    ctx = Kontekst(a, {z["id"]: z for z in zadania_lista}, wyniki)
    if a.pokaz:
        pokaz(przebiegi, ctx, zrobione)
        return 0

    do_zrobienia = [s for s in przebiegi if s["id"] not in zrobione]
    print(f"Przebiegi: {len(do_zrobienia)} do zrobienia, {len(zrobione)} zrobionych. Zatrzymanie: Ctrl+C "
          f"(wznowienie: --wznow).")
    kolejka = iter(do_zrobienia)
    blokada_kolejki = threading.Lock()

    def pracownik() -> None:
        while True:
            with blokada_kolejki:
                powod = ctx.stop or ctx.powod_stopu()
                if powod:
                    ctx.stop = powod
                    return
                spec = next(kolejka, None)
            if spec is None:
                return
            print(f"[{teraz():%H:%M:%S}] start {spec['id']}", flush=True)
            w = przebieg(spec, ctx)
            print(f"[{teraz():%H:%M:%S}] koniec {spec['id']}: testy {'OK' if w['testy']['zaliczone'] else 'NIE'}"
                  if w and w.get("testy") else f"[{teraz():%H:%M:%S}] koniec {spec['id']} z błędem: {w['bledy']}",
                  f"ocena {w.get('ocena')} wazone {w.get('tokeny_wazone')}", flush=True)

    try:
        with ThreadPoolExecutor(max_workers=max(1, a.naraz)) as ex:
            for f in [ex.submit(pracownik) for _ in range(max(1, a.naraz))]:
                f.result()
    except KeyboardInterrupt:
        print("Przerwano. Wznów: --wznow")
        return 130
    print(f"Koniec. Stop: {ctx.stop or 'plan wykonany'}. Zużyte: {suma_wazone(ctx.wyniki) / 1e6:.1f}M ważonych.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
