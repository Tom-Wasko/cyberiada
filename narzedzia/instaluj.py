"""Instalator cyberiady na tym komputerze (idempotentny: można uruchamiać wielokrotnie).

  python -X utf8 narzedzia/instaluj.py              instaluje / naprawia
  python -X utf8 narzedzia/instaluj.py --sprawdz    tylko lista kontrolna, nic nie zmienia
  python -X utf8 narzedzia/instaluj.py --zaufaj [folder]   tylko zaufanie folderowi (domyślnie bieżący)
  python -X utf8 narzedzia/instaluj.py --bez-pamieci        dodatkowo wyłącza auto-pamięć

Robi: dowiązania ~/.claude/{rules,agents,skills/<skill>} do repo, scalenie ~/.claude/settings.json
(kopia zapasowa), zaufanie folderom projektów w ~/.claude.json (kopia zapasowa), polecenie `archi` w PATH.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wspolne import CLAUDE_DIR, CYBERIADA, DOM, komputer, projekty  # noqa: E402

USTAWIENIA = CLAUDE_DIR / "settings.json"
STAN_CLAUDE = DOM / ".claude.json"
BIN = CYBERIADA / "narzedzia" / "bin"
ZAKAZ_AGENTOW = ["Agent(Explore)", "Agent(Plan)", "Agent(general-purpose)"]
STEMPEL = time.strftime("%Y%m%d-%H%M%S")
problemy: list[str] = []


def ok(tekst: str) -> None:
    print("  ✓", tekst)


def zle(tekst: str) -> None:
    print("  ✗", tekst)
    problemy.append(tekst)


def wersja(polecenie: list[str]) -> str | None:
    exe = shutil.which(polecenie[0])
    if not exe:
        return None
    try:
        w = subprocess.run([exe, *polecenie[1:]], capture_output=True, text=True,
                           encoding="utf-8", timeout=30)
        return (w.stdout or w.stderr).strip().splitlines()[0] if w.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired, IndexError):
        return None


def lista_kontrolna() -> None:
    print("Lista kontrolna:")
    for nazwa, pol in [("Claude Code", ["claude", "--version"]), ("git", ["git", "--version"]),
                       ("GitHub CLI", ["gh", "--version"])]:
        w = wersja(pol)
        (ok if w else zle)(f"{nazwa}: {w or 'brak w PATH'}")
    ok(f"Python {sys.version.split()[0]}") if sys.version_info >= (3, 10) else zle("Python < 3.10")
    gh = shutil.which("gh")
    if gh:
        z = subprocess.run([gh, "auth", "status"], capture_output=True, text=True, encoding="utf-8")
        (ok if z.returncode == 0 else zle)("gh zalogowany" if z.returncode == 0
                                            else "gh niezalogowany: gh auth login")
    k = komputer()
    (ok if k in (projekty_rejestr_komputery()) else zle)(
        f"komputer {k} w projekty.yaml" if k in projekty_rejestr_komputery()
        else f"komputer {k} nie ma wpisu w projekty.yaml (komputery: {k}: <katalog bazowy>)")


def projekty_rejestr_komputery() -> set[str]:
    import yaml
    with open(CYBERIADA / "projekty.yaml", encoding="utf-8") as f:
        return {str(x).upper() for x in (yaml.safe_load(f).get("komputery") or {})}


def jest_dowiazaniem(p: Path) -> bool:
    return p.is_symlink() or (hasattr(os.path, "isjunction") and os.path.isjunction(p))


def dowiazanie(link: Path, cel: Path, sprawdz: bool) -> None:
    if jest_dowiazaniem(link):
        if Path(os.path.realpath(link)) == cel.resolve():
            ok(f"{link} → {cel}")
            return
        if sprawdz:
            zle(f"{link} wskazuje gdzie indziej: {os.path.realpath(link)}")
            return
        os.unlink(link)
    elif link.exists():
        if sprawdz:
            zle(f"{link} to zwykły folder (instalator zrobi kopię i dowiązanie)")
            return
        kopia = link.with_name(f"{link.name}.kopia-{STEMPEL}")
        link.rename(kopia)
        print(f"    kopia dawnego folderu: {kopia}")
    elif sprawdz:
        zle(f"brak {link}")
        return
    link.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(cel)], check=True,
                   capture_output=True)
    ok(f"{link} → {cel} (utworzone)")


def dowiazania(sprawdz: bool) -> None:
    print("Dowiązania:")
    dowiazanie(CLAUDE_DIR / "rules", CYBERIADA / "zasady", sprawdz)
    dowiazanie(CLAUDE_DIR / "agents", CYBERIADA / "agenci", sprawdz)
    for skill in sorted(p for p in (CYBERIADA / "skille").iterdir() if p.is_dir()):
        dowiazanie(CLAUDE_DIR / "skills" / skill.name, skill, sprawdz)


def zapisz_json(plik: Path, dane: dict) -> None:
    if plik.exists():
        shutil.copy2(plik, plik.with_name(f"{plik.name}.kopia-{STEMPEL}"))
    tmp = plik.with_name(plik.name + ".tmp")
    tmp.write_text(json.dumps(dane, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, plik)


def ustawienia(sprawdz: bool, bez_pamieci: bool) -> None:
    print("Ustawienia (~/.claude/settings.json):")
    d = json.loads(USTAWIENIA.read_text(encoding="utf-8")) if USTAWIENIA.exists() else {}
    chce = {"model": "sonnet", "effortLevel": "medium", "attribution": False}
    if bez_pamieci:
        chce["autoMemoryEnabled"] = False
    zmiany = []
    for k, v in chce.items():
        if d.get(k) != v:
            zmiany.append(f"{k} = {json.dumps(v)}")
            d[k] = v
    sonnet = d.setdefault("modelSettings", {}).setdefault("claude-sonnet-5-5", {})
    if sonnet.get("effortLevel") != "medium":
        sonnet["effortLevel"] = "medium"
        zmiany.append("modelSettings.claude-sonnet-5-5.effortLevel = medium")
    perm = d.setdefault("permissions", {})
    if perm.get("defaultMode") != "auto":
        perm["defaultMode"] = "auto"
        zmiany.append("permissions.defaultMode = auto")
    deny = perm.setdefault("deny", [])
    for r in ZAKAZ_AGENTOW:
        if r not in deny:
            deny.append(r)
            zmiany.append(f"permissions.deny += {r}")
    env = d.setdefault("env", {})
    if env.get("CLAUDE_CODE_GOAL_CHECKIN_MINUTES") != "0":
        env["CLAUDE_CODE_GOAL_CHECKIN_MINUTES"] = "0"
        zmiany.append("env.CLAUDE_CODE_GOAL_CHECKIN_MINUTES = 0")
    if not zmiany:
        ok("wszystko ustawione")
    elif sprawdz:
        for z in zmiany:
            zle(f"do ustawienia: {z}")
    else:
        zapisz_json(USTAWIENIA, d)
        for z in zmiany:
            ok(z)


def zaufaj(foldery: list[Path], sprawdz: bool) -> None:
    print("Zaufanie folderom (~/.claude.json):")
    d = json.loads(STAN_CLAUDE.read_text(encoding="utf-8"))
    proj = d.setdefault("projects", {})
    nowe = []
    for f in foldery:
        klucz = f.resolve().as_posix()
        if proj.get(klucz, {}).get("hasTrustDialogAccepted"):
            ok(klucz)
        elif sprawdz:
            zle(f"bez zaufania: {klucz}")
        else:
            proj.setdefault(klucz, {})["hasTrustDialogAccepted"] = True
            nowe.append(klucz)
    if nowe:
        zapisz_json(STAN_CLAUDE, d)
        for k in nowe:
            ok(f"{k} (dodane)")


def sciezka_path(sprawdz: bool) -> None:
    import winreg
    print("PATH użytkownika:")
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0,
                        winreg.KEY_READ | winreg.KEY_WRITE) as k:
        try:
            wartosc, typ = winreg.QueryValueEx(k, "Path")
        except FileNotFoundError:
            wartosc, typ = "", winreg.REG_EXPAND_SZ
        czesci = [c for c in wartosc.split(";") if c]
        if any(Path(c).resolve() == BIN.resolve() for c in czesci if c.strip()):
            ok(f"{BIN} (polecenie archi)")
        elif sprawdz:
            zle(f"brak {BIN} w PATH")
        else:
            winreg.SetValueEx(k, "Path", 0, typ, ";".join([*czesci, str(BIN)]))
            ok(f"{BIN} dodane – działa w NOWYM terminalu")
    if not sprawdz:
        ogloszenie_zmiany_srodowiska()


def ogloszenie_zmiany_srodowiska() -> None:
    """Powiadamia Windows (Eksplorator) o nowym PATH; bez tego nowe okna dostają stary PATH."""
    import ctypes
    wynik = ctypes.c_ulong()
    ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001A, 0, "Environment", 0x0002, 5000,
                                             ctypes.byref(wynik))


def main() -> int:
    p = argparse.ArgumentParser(description="Instalator cyberiady.")
    p.add_argument("--sprawdz", action="store_true")
    p.add_argument("--zaufaj", nargs="?", const=".", metavar="FOLDER")
    p.add_argument("--bez-pamieci", action="store_true")
    a = p.parse_args()
    if a.zaufaj:
        zaufaj([Path(a.zaufaj)], False)
        return 0
    print(f"cyberiada: {CYBERIADA}  ({'sprawdzanie' if a.sprawdz else 'instalacja'})")
    lista_kontrolna()
    dowiazania(a.sprawdz)
    ustawienia(a.sprawdz, a.bez_pamieci)
    zaufaj(list(dict.fromkeys([CYBERIADA, *projekty().values()])), a.sprawdz)
    sciezka_path(a.sprawdz)
    print("Gotowe." if not problemy else f"Do poprawy: {len(problemy)}")
    return 1 if problemy else 0


if __name__ == "__main__":
    sys.exit(main())
