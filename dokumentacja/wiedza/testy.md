# Testy cyberiady

Wyniki prób, od których zależy układ systemu. Każdy wpis: data, wersja Claude Code, wynik, wniosek.
Przy aktualizacji Claude Code powtórz testy oznaczone ⟳.

## 21.11.2026 · Claude Code 2.1.330 · Windows 11

| Test | Wynik | Wniosek |
|---|---|---|
| T1 ⟳ Archi uruchamia `claude --bg` z Basha, rola przez `--append-system-prompt-file` | ✓ | Działa. Sesja w tle sama zakłada worktree `.claude/worktrees/<nazwa>` i gałąź `worktree-<nazwa>`. Rola działa (ścieżka bezwzględna). `--agent` niepotrzebny. |
| T1a Folder bez zaufania | ✗ `Workspace not trusted` | Zaufanie jest na folder (podfolder repo osobno). Instalator i `/nowy-projekt` wpisują `hasTrustDialogAccepted` do `~/.claude.json`. Worktree w zaufanym repo działa bez wpisu. |
| T1b `--permission-mode dontAsk` bez listy | commit odrzucony | Bez listy dozwolonych wyko nie zrobi commita; potrzebne `narzedzia/wyko/ustawienia.json`. |
| T8 Wznowienie po nazwie | ✓ | `claude -r <nazwa>` wznawia sesję nazwaną `-n <nazwa>`. |
| T15 ⟳ Junction dla skilli i agentów | ✓ | `~/.claude/agents` → `cyberiada/agenci` i `~/.claude/skills/<skill>` → `cyberiada/skille/<skill>`: nowa sesja widzi oba. |
| T14 ⟳ Wyko bez próśb o zgodę (`--permission-mode auto` + `narzedzia/wyko/ustawienia.json`) | ✓ (próba krótka, nie 1 h) | 2 commity bez pytań; `git push` odrzucony (polecenie złożone odrzucane w całości). Bez ustawienia `attribution` wyko dopisał `Co-Authored-By: Claude`: instalator ustawia `"attribution": false`. |
| T16 `--bg` + `-w <nazwa>` | ✓ | Worktree `.claude/worktrees/<nazwa>`, gałąź `worktree-<nazwa>`, zablokowany. `claude stop <id>` + `claude rm <id>` usuwa sesję, worktree i gałąź (najpierw scalić!). Status po skończonej turze: `idle`. |
| T17 `~/.claude/rules` jako junction do `cyberiada/zasady` | ✓ | Nowa sesja w każdym folderze wczytuje `baza.md` i `preferencje.md` bez `@import` (bez pytania o zewnętrzne pliki). |
| T18 Hook PostToolUse przez `--settings` w sesji `--bg` (22.11) | ✓ | Sesja próbna (Haiku, `-w`, `narzedzia/wyko/ustawienia.json`): po `git commit` hook `dziennik/hook_commit.py` dał instrukcję, ArtifactData dostępne po ToolSearch, auto mode go nie zablokował, zapis `postep/<sesja>` wersja 1. |
| T19 Wznowienie sesji w tle (22.11) | ✓ | `claude --bg --resume <pełne id>` bez flag wznawia tę samą sesję (to samo id, zapisane opcje). Z flagami albo skróconym id startuje kopia pod nowym id. Poprawione w `wyko.py --wznow` (Z5). |
| T4 Skille z telefonu (22.11) | ✓ | Szef napisał `/hejo` w czacie Remote Control na telefonie; skill uruchomił się w sesji archi-cyberiada jak z klawiatury. |
| T5 Narzut startu zwiadowcy (22.11) | ✓ | Pierwsza tura agenta `zwiadowca` (Haiku): 6,3 tys. tokenów kontekstu, całe zadanie 7,6 tys. (log `subagents/*.jsonl`). Dla porównania sesja wyko `--bg`: 47,6 tys. Zwiadowca jest tani; drogi jest start sesji, nie agenta. |
| T6 % limitu w statusline (22.11) | ✓ (źródło) | Skrypt statusline dostaje `rate_limits.five_hour.used_percentage` i `.resets_at`, też `seven_day.*` (plany Pro/Max, po pierwszej odpowiedzi API) oraz `context_window.used_percentage`. Źródło: https://code.claude.com/docs/en/statusline. Statusline na tym komputerze jeszcze nie ustawiony. |

### Narzut startu (pomiar z logów)
- Sesja `-p`, Haiku, folder bez CLAUDE.md: 27,5k tokenów kontekstu na start.
- Sesja `--bg` (interaktywna), Haiku: 47,6k na pierwszą turę. Różnica to m.in. narzędzia MCP (Chrome, Docs)
  i opisy skilli. Wyko startuje z `--no-chrome`; dalsze cięcie: test T5.

### Sprawdzone przez szefa
- **T2** ✓ (2026-11-21) Remote Control na Windows + push: sesja `archi-cyberiada` w aplikacji Claude działa
  (szef: „wszystko na telefonie działa”).
- **T3** ✓ (2026-11-21) Okienko pytań przez Remote Control: odpowiedź z telefonu działa.

### Do zrobienia przez szefa
- **T13** Restart w trakcie: uruchom wyko, zrestartuj Windows, potem `archi cyberiada` i `/wznow`.
