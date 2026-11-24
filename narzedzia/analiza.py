"""Badanie kosztów z logów sesji (wszystkie projekty, ten komputer): skąd bierze się zużycie tokenów.

  python -X utf8 narzedzia/analiza.py [--od 2026-11-01] [--do ...] [--json] [--katalog <logi>]

Raport Markdown (do 60 linii) albo --json. Koszt = „ważone” z zuzycie.py (jednostki wejścia Sonneta).
Tura = jedno wywołanie modelu (wpis assistant). Agenci liczą się do sesji, która ich wywołała, ale w udziałach
są osobno. Czytanie wpisów i wagi: import z zuzycie.py (bez kopiowania).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean, median

sys.path.insert(0, str(Path(__file__).resolve().parent))
import zuzycie  # noqa: E402
from wspolne import SESJE_DIR, tytul_sesji  # noqa: E402

PRZEDZIALY = [("<50k", 0, 50_000), ("50–100k", 50_000, 100_000), ("100–200k", 100_000, 200_000),
              (">200k", 200_000, 10**12)]
EDYCJE = {"Edit", "Write", "NotebookEdit", "MultiEdit"}


def czas(t: str) -> datetime:
    return datetime.fromisoformat(t.replace("Z", "+00:00"))


def zapis_wazony(w: dict) -> float:
    """Koszt samego zapisu do cache w jednym wpisie."""
    z5 = min(w.get("cache_zapis_5m", 0), w["cache_zapis"])
    return zuzycie.mnoznik(w["model"]) * (2.0 * (w["cache_zapis"] - z5) + 1.25 * z5)


def skan(katalog: Path) -> dict:
    """Dodatkowe fakty, których nie ma we wpisach zużycia: zmiany plików i commity (po czasie pierwszej
    linii komunikatu), granice /compact, effort z żądań. Klucze: nazwa sesji."""
    flagi: dict[tuple[str, str], set] = defaultdict(set)
    kompakty: dict[str, list] = defaultdict(list)
    effort: dict[str, Counter] = defaultdict(Counter)
    for plik in katalog.glob("*/*.jsonl"):
        nazwa = tytul_sesji(plik) or f"(bez nazwy {plik.stem[:8]})"
        zrodla = [(plik, False)] + [(s, True) for s in plik.with_suffix("").glob("subagents/*.jsonl")]
        for zrodlo, agent in zrodla:
            pierwszy: dict[str, str] = {}
            try:
                f = open(zrodlo, encoding="utf-8", errors="replace")
            except OSError:
                continue
            with f:
                for linia in f:
                    try:
                        if linia.startswith('{"type":"api-request"'):
                            d = json.loads(linia)
                            if not agent and d.get("querySource") == "repl_main_thread":
                                e = ((d.get("params") or {}).get("output_config") or {}).get("effort")
                                if e:
                                    effort[nazwa][e] += 1
                        elif '"compact_boundary"' in linia:
                            d = json.loads(linia)
                            if d.get("subtype") == "compact_boundary":
                                m = d.get("compactMetadata") or {}
                                kompakty[nazwa].append({"czas": d.get("timestamp", ""), "przed": m.get("preTokens"),
                                                        "po": m.get("postTokens")})
                        elif '"tool_use"' in linia and '"assistant"' in linia:
                            d = json.loads(linia)
                            m = d.get("message") or {}
                            klucz = m.get("id") or ""
                            ts = pierwszy.setdefault(klucz, d.get("timestamp", ""))
                            for c in m.get("content") or []:
                                if not isinstance(c, dict) or c.get("type") != "tool_use":
                                    continue
                                if c.get("name") in EDYCJE:
                                    flagi[(nazwa, ts)].add("edycja")
                                elif c.get("name") == "Bash":
                                    kom = (c.get("input") or {}).get("command", "")
                                    if "git" in kom and " commit" in kom:
                                        flagi[(nazwa, ts)].add("commit")
                        elif '"assistant"' in linia[:80] or '"type":"assistant"' in linia:
                            d = json.loads(linia)
                            m = d.get("message") or {}
                            pierwszy.setdefault(m.get("id") or "", d.get("timestamp", ""))
                    except ValueError:
                        continue
    return {"flagi": flagi, "kompakty": kompakty, "effort": effort}


def rodzaj(nazwa: str) -> str:
    return "archi" if nazwa.startswith("archi-") else "wyko" if nazwa.startswith("wyko-") else "inne"


def sr(lista: list[float]) -> float:
    return round(mean(lista), 1) if lista else 0.0


def analizuj(katalog: Path, od: str | None, do: str | None) -> dict:
    wpisy = [w for w in zuzycie.wpisy(katalog=katalog)
             if (not od or w["czas"][:10] >= od) and (not do or w["czas"][:10] <= do)]
    fakty = skan(katalog)
    razem = sum(zuzycie.wazone(w) for w in wpisy) or 1.0
    wynik: dict = {"od": od, "do": do, "wpisow": len(wpisy), "razem_wazone": round(razem)}

    udzial = defaultdict(float)
    for w in wpisy:
        udzial["agenci" if w["agent"] else rodzaj(w["sesja"])] += zuzycie.wazone(w)
    wynik["udzial_proc"] = {k: round(100 * v / razem, 1) for k, v in sorted(udzial.items())}

    glowne = defaultdict(list)  # sesja -> wpisy głównego wątku, chronologicznie
    for w in sorted((w for w in wpisy if not w["agent"]), key=lambda w: w["czas"]):
        glowne[w["sesja"]].append(w)

    # Archi: koszt tury a wielkość kontekstu
    kosz = {n: [] for n, _, _ in PRZEDZIALY}
    for nazwa, lista in glowne.items():
        if rodzaj(nazwa) != "archi":
            continue
        for w in lista:
            ctx = w["wejscie"] + w["cache_zapis"] + w["cache_odczyt"]
            for n, a, b in PRZEDZIALY:
                if a <= ctx < b:
                    kosz[n].append(zuzycie.wazone(w))
    wynik["archi_kontekst"] = {n: {"tur": len(v), "srednio": round(sr(v))} for n, v in kosz.items()}

    # przerwy (wszystkie sesje, główny wątek): ponowny zapis cache po przerwie
    przerwy = {}
    for prog, nazwa_progu in ((300, ">5 min"), (3600, ">1 h")):
        po = [w for lista in glowne.values() for a, w in zip(lista, lista[1:])
              if (czas(w["czas"]) - czas(a["czas"])).total_seconds() > prog]
        zapis = [zapis_wazony(w) for w in po]
        przerwy[nazwa_progu] = {"tur": len(po), "zapis_suma": round(sum(zapis)), "zapis_srednio": round(sr(zapis)),
                                "proc_calosci": round(100 * sum(zapis) / razem, 1)}
    wszystkie = [zapis_wazony(w) for lista in glowne.values() for w in lista]
    przerwy["srednio_zapis_na_ture_ogolem"] = round(sr(wszystkie))
    wynik["przerwy"] = przerwy

    # wyko: start, sesja, commity, długość
    wyko = []
    for nazwa, lista in glowne.items():
        if rodzaj(nazwa) != "wyko" or len(lista) < 2:
            continue
        n_start = next((i + 1 for i, w in enumerate(lista)
                        if "edycja" in fakty["flagi"].get((nazwa, w["czas"]), ())), None) or min(3, len(lista))
        start = sum(zuzycie.wazone(w) for w in lista[:n_start])
        cala = sum(zuzycie.wazone(w) for w in wpisy if w["sesja"] == nazwa)
        commity = sum("commit" in fakty["flagi"].get((nazwa, w["czas"]), ()) for w in lista)
        minuty = (czas(lista[-1]["czas"]) - czas(lista[0]["czas"])).total_seconds() / 60
        wyko.append({"sesja": nazwa, "tur": len(lista), "tur_startu": n_start, "start": round(start),
                     "cala": round(cala), "commity": commity, "minut": round(minuty),
                     "na_commit": round(cala / commity) if commity else None})
    wynik["wyko"] = {"sesji": len(wyko), "start_srednio": round(sr([x["start"] for x in wyko])),
                     "start_proc_sesji": round(100 * sum(x["start"] for x in wyko) / (sum(x["cala"] for x in wyko) or 1), 1),
                     "tur_startu_mediana": median([x["tur_startu"] for x in wyko]) if wyko else 0,
                     "cala_srednio": round(sr([x["cala"] for x in wyko])),
                     "commitow_srednio": sr([x["commity"] for x in wyko]),
                     "na_commit_srednio": round(sr([x["na_commit"] for x in wyko if x["na_commit"]])),
                     "sesje": sorted(wyko, key=lambda x: -x["cala"])[:8]}
    dl = {}
    for nazwa_d, a, b in (("<30 min", 0, 30), ("30–120 min", 30, 120), (">120 min", 120, 10**9)):
        g = [x for x in wyko if a <= x["minut"] < b]
        dl[nazwa_d] = {"sesji": len(g), "cala_srednio": round(sr([x["cala"] for x in g])),
                       "na_ture": round(sum(x["cala"] for x in g) / (sum(x["tur"] for x in g) or 1))}
    wynik["wyko_dlugosc"] = dl

    # /compact
    kompakty = []
    for nazwa, lista in fakty["kompakty"].items():
        for k in lista:
            if od and k["czas"][:10] < od or do and k["czas"][:10] > do:
                continue
            nast = next((w for w in glowne.get(nazwa, []) if w["czas"] > k["czas"]), None)
            kompakty.append({"przed": k["przed"], "po": k["po"],
                             "nastepna_tura": round(zuzycie.wazone(nast)) if nast else None})
    wynik["compact"] = {"ile": len(kompakty),
                        "przed_srednio": round(sr([k["przed"] for k in kompakty if k["przed"]])),
                        "po_srednio": round(sr([k["po"] for k in kompakty if k["po"]])),
                        "nastepna_tura_srednio": round(sr([k["nastepna_tura"] for k in kompakty if k["nastepna_tura"]]))}

    # model i effort (effort: najczęstszy w sesji)
    grupy = defaultdict(lambda: {"sesji": 0, "tur": 0, "wazone": 0.0})
    for nazwa, lista in glowne.items():
        e = fakty["effort"].get(nazwa)
        model = Counter(w["model"].replace("claude-", "") for w in lista).most_common(1)[0][0]
        g = grupy[(rodzaj(nazwa), model, e.most_common(1)[0][0] if e else "?")]
        g["sesji"] += 1
        g["tur"] += len(lista)
        g["wazone"] += sum(zuzycie.wazone(w) for w in lista)
    wynik["model_effort"] = [{"rodzaj": k[0], "model": k[1], "effort": k[2], "sesji": g["sesji"], "tur": g["tur"],
                              "na_ture": round(g["wazone"] / g["tur"]), "wazone": round(g["wazone"])}
                             for k, g in sorted(grupy.items(), key=lambda kv: -kv[1]["wazone"])]
    return wynik


def raport(r: dict) -> str:
    z = f"{r['od'] or 'początek'} – {r['do'] or 'dziś'}"
    L = [f"# Analiza kosztów z logów ({z})",
         f"Wpisów: {r['wpisow']:,}, razem ważone: {r['razem_wazone']:,} (jednostki wejścia Sonneta).", "",
         "## Udział w zużyciu",
         " · ".join(f"{k} {v}%" for k, v in r["udzial_proc"].items()), "",
         "## Archi: koszt tury a kontekst (ważone na turę)", "| kontekst | tur | średnio |", "|---|---|---|"]
    L += [f"| {n} | {v['tur']:,} | {v['srednio']:,} |" for n, v in r["archi_kontekst"].items()]
    p = r["przerwy"]
    L += ["", "## Przerwy: ponowny zapis cache (wszystkie sesje, główny wątek)",
          "| przerwa | tur po niej | zapis razem | średnio | % całości |", "|---|---|---|---|---|"]
    L += [f"| {k} | {p[k]['tur']:,} | {p[k]['zapis_suma']:,} | {p[k]['zapis_srednio']:,} | {p[k]['proc_calosci']}% |"
          for k in (">5 min", ">1 h")]
    L += [f"Dla porównania: średni zapis cache na dowolną turę {p['srednio_zapis_na_ture_ogolem']:,}."]
    w = r["wyko"]
    L += ["", f"## Wyko ({w['sesji']} sesji)",
          f"- Start (do pierwszej zmiany pliku, albo 3 tury): średnio {w['start_srednio']:,} ważonych "
          f"= {w['start_proc_sesji']}% sesji, mediana {w['tur_startu_mediana']} tur.",
          f"- Cała sesja: średnio {w['cala_srednio']:,}; commitów średnio {w['commitow_srednio']}; "
          f"koszt na commit średnio {w['na_commit_srednio']:,}.",
          "| długość | sesji | cała średnio | na turę |", "|---|---|---|---|"]
    L += [f"| {k} | {v['sesji']} | {v['cala_srednio']:,} | {v['na_ture']:,} |" for k, v in r["wyko_dlugosc"].items()]
    c = r["compact"]
    L += ["", "## /compact",
          f"Razem {c['ile']}; kontekst przed {c['przed_srednio']:,} → po {c['po_srednio']:,} tokenów; "
          f"pierwsza tura po nim kosztuje średnio {c['nastepna_tura_srednio']:,}.", "",
          "## Model i effort (według sesji; „?” = brak żądań w logu)", "| rodzaj | model | effort | sesji | tur | na turę |",
          "|---|---|---|---|---|---|"]
    L += [f"| {m['rodzaj']} | {m['model']} | {m['effort']} | {m['sesji']} | {m['tur']:,} | {m['na_ture']:,} |"
          for m in r["model_effort"][:10]]
    return "\n".join(L)


def main() -> int:
    p = argparse.ArgumentParser(description="Badanie kosztów z logów sesji.")
    p.add_argument("--od")
    p.add_argument("--do")
    p.add_argument("--json", action="store_true")
    p.add_argument("--katalog", type=Path, default=SESJE_DIR, help="zamiast ~/.claude/projects (testy)")
    a = p.parse_args()
    r = analizuj(a.katalog, a.od, a.do)
    print(json.dumps(r, ensure_ascii=False, indent=1) if a.json else raport(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
