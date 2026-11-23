"""Baza zużycia: tokeny z lokalnych dzienników sesji Claude Code (~/.claude/projects), według nazwy sesji.

  python -X utf8 C:/Users/PC/cyberiada/narzedzia/zuzycie.py                 wszystko, według sesji
  ... --projekt lukrum               tylko sesje projektu: nazwa z projekty.yaml albo folder (z worktree)
  ... --od 2026-11-21 [--do 2026-11-22]   zakres dat (UTC, z dziennika)
  ... --nazwa wyko-lukrum-03          sesje o nazwie zaczynającej się od tego tekstu
  ... --json                          wynik maszynowy (dla dziennika)

Liczby: wejście, zapis do cache, odczyt z cache, wyjście; „ważone” = przybliżony koszt w jednostkach
wejścia Sonneta według cennika (dokumentacja/wiedza/tokeny.md): cache odczyt 0,1 (Opus/Sonnet 5.5: 0,05,
Fable: 0,025), zapis 1 h 2,0, zapis 5 min 1,25, wyjście 5,0; Opus ×2, Fable ×4, Haiku ×0,05. Tylko ten komputer.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from collections.abc import Iterator
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wspolne import SESJE_DIR, projekty, tytul_sesji  # noqa: E402

MNOZNIK_MODELU = {"opus": 2.0, "sonnet": 1.0, "haiku": 0.05, "fable": 4.0}
# odczyt z cache względem ceny wejścia danego modelu (domyślnie 0,1)
ODCZYT_CACHE = (("fable", 0.025), ("opus-5-5", 0.05), ("sonnet-5-5", 0.05))
POLA = ("wejscie", "cache_zapis", "cache_odczyt", "wyjscie")


def mnoznik(model: str) -> float:
    for klucz, m in MNOZNIK_MODELU.items():
        if klucz in model:
            return m
    return 1.0


def odczyt_cache(model: str) -> float:
    return next((w for klucz, w in ODCZYT_CACHE if klucz in model), 0.1)


def czytaj(plik: Path, filtr) -> list[dict]:
    """Wiersze zużycia z jednego dziennika, bez powtórzeń tego samego komunikatu."""
    widziane, wynik, cwd = set(), [], None
    try:
        f = open(plik, encoding="utf-8", errors="replace")
    except OSError:
        return []
    with f:
        for linia in f:
            if '"usage"' not in linia:
                if cwd is None and '"cwd"' in linia:
                    try:
                        cwd = json.loads(linia).get("cwd")
                    except ValueError:
                        pass
                continue
            try:
                d = json.loads(linia)
            except ValueError:
                continue
            cwd = d.get("cwd") or cwd
            m = d.get("message") or {}
            u = m.get("usage")
            if d.get("type") != "assistant" or not u:
                continue
            klucz = (m.get("id"), d.get("requestId"))
            if klucz in widziane:
                continue
            widziane.add(klucz)
            czas = d.get("timestamp", "")
            if not filtr(cwd or "", czas):
                continue
            wynik.append({"model": m.get("model", "?"), "czas": czas,
                          "wejscie": u.get("input_tokens", 0),
                          "cache_zapis": u.get("cache_creation_input_tokens", 0),
                          "cache_zapis_5m": (u.get("cache_creation") or {}).get("ephemeral_5m_input_tokens", 0),
                          "cache_odczyt": u.get("cache_read_input_tokens", 0),
                          "wyjscie": u.get("output_tokens", 0)})
    return wynik


def wazone(wpis: dict) -> float:
    """Przybliżony koszt jednego wpisu w jednostkach wejścia Sonneta."""
    z5m = min(wpis.get("cache_zapis_5m", 0), wpis["cache_zapis"])
    return mnoznik(wpis["model"]) * (wpis["wejscie"] + odczyt_cache(wpis["model"]) * wpis["cache_odczyt"]
                                     + 2.0 * (wpis["cache_zapis"] - z5m) + 1.25 * z5m + 5.0 * wpis["wyjscie"])


def folder_projektu(tekst: str) -> Path:
    """Nazwa projektu z projekty.yaml albo ścieżka folderu."""
    if not Path(tekst).is_dir():
        try:
            znany = projekty().get(tekst.lower())
        except Exception:  # noqa: BLE001 - brak rejestru: zostaje ścieżka
            znany = None
        if znany:
            return znany
    return Path(tekst)


def wpisy(projekt: Path | None = None, katalog: Path | None = None) -> Iterator[dict]:
    """Wszystkie wpisy zużycia: pola sesja, agent (bool), model, czas (UTC z dziennika), wejscie,
    cache_zapis, cache_odczyt, wyjscie. `projekt` filtruje po cwd (z worktree), `katalog` zastępuje ~/.claude/projects."""
    prefiks = str(projekt.resolve()).lower().replace("/", "\\").rstrip("\\") if projekt else None

    def filtr(cwd: str, czas: str) -> bool:
        c = cwd.lower().replace("/", "\\").rstrip("\\")
        return not prefiks or c == prefiks or c.startswith(prefiks + "\\")

    for plik in (katalog or SESJE_DIR).glob("*/*.jsonl"):
        nazwa = tytul_sesji(plik) or f"(bez nazwy {plik.stem[:8]})"
        zrodla = [(plik, False)]
        zrodla += [(s, True) for s in plik.with_suffix("").glob("subagents/*.jsonl")]
        for zrodlo, agent in zrodla:
            for w in czytaj(zrodlo, filtr):
                yield {"sesja": nazwa, "agent": agent, **w}


def main() -> int:
    p = argparse.ArgumentParser(description="Zużycie tokenów według sesji (ten komputer).")
    p.add_argument("--projekt", type=folder_projektu, help="nazwa projektu (projekty.yaml) albo folder")
    p.add_argument("--od")
    p.add_argument("--do")
    p.add_argument("--nazwa")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    sumy: dict[str, dict] = defaultdict(lambda: {"modele": defaultdict(int), "od": "", "do": "",
                                                 **{k: 0 for k in POLA}, "wazone": 0.0})
    for w in wpisy(a.projekt):
        if a.nazwa and not w["sesja"].startswith(a.nazwa):
            continue
        if a.od and w["czas"][:10] < a.od:
            continue
        if a.do and w["czas"][:10] > a.do:
            continue
        s = sumy[w["sesja"] + (" · agenci" if w["agent"] else "")]
        for k in POLA:
            s[k] += w[k]
        s["modele"][w["model"]] += w["wyjscie"]
        s["wazone"] += wazone(w)
        s["od"] = min(s["od"] or w["czas"], w["czas"])
        s["do"] = max(s["do"], w["czas"])

    wiersze = sorted(sumy.items(), key=lambda kv: kv[1]["wazone"], reverse=True)
    if a.json:
        print(json.dumps([{"sesja": n, **{k: v for k, v in s.items() if k != "modele"},
                           "modele": dict(s["modele"])} for n, s in wiersze],
                         ensure_ascii=False, indent=1))
        return 0
    if not wiersze:
        print("Brak danych dla tych filtrów.")
        return 0
    print(f"{'sesja':<34}{'wejście':>10}{'cache zap.':>12}{'cache odc.':>13}{'wyjście':>10}"
          f"{'ważone':>12}  model")
    razem = {k: 0 for k in POLA} | {"wazone": 0.0}
    for n, s in wiersze:
        model = max(s["modele"], key=s["modele"].get).replace("claude-", "")
        print(f"{n[:33]:<34}{s['wejscie']:>10,}{s['cache_zapis']:>12,}{s['cache_odczyt']:>13,}"
              f"{s['wyjscie']:>10,}{s['wazone']:>12,.0f}  {model}")
        for k in razem:
            razem[k] += s[k]
    print(f"{'RAZEM':<34}{razem['wejscie']:>10,}{razem['cache_zapis']:>12,}"
          f"{razem['cache_odczyt']:>13,}{razem['wyjscie']:>10,}{razem['wazone']:>12,.0f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
