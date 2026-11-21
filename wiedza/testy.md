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

### Narzut startu (pomiar z logów)
- Sesja `-p`, Haiku, folder bez CLAUDE.md: 27,5k tokenów kontekstu na start.
- Sesja `--bg` (interaktywna), Haiku: 47,6k na pierwszą turę. Różnica to m.in. narzędzia MCP (Chrome, Docs)
  i opisy skilli. Wyko startuje z `--no-chrome`; dalsze cięcie: test T5.

### Do zrobienia przez szefa (wymagają telefonu albo restartu)
- **T2** Remote Control na Windows + push: `archi cyberiada`, w telefonie aplikacja Claude → sesja `archi-cyberiada`,
  napisz „test”; w `/config` włącz „Push when Claude decides”, Archi wyśle push.
- **T3** Okienko pytań przez RC: Archi zada pytanie okienkiem; odpowiedz z telefonu.
- **T13** Restart w trakcie: uruchom wyko, zrestartuj Windows, potem `archi cyberiada` i `/wznow`.
- **T4–T6** (po T2): skille z telefonu (`/hejo` napisane w telefonie), narzut startu zwiadowcy (`/context`),
  odczyt % limitu ze statusline.
