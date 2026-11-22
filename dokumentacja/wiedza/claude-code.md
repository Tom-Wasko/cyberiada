# Funkcje Claude Code używane w cyberiadzie

Sprawdzone: 2026-11-22 (dokumentacja; wersja na tym komputerze: 2.1.330, `testy.md`). Część stron jest długa i była czytana fragmentami.

| Funkcja | Co robi | Odnośnik | Gdzie w cyberiadzie |
|---|---|---|---|
| Sesje w tle: `--bg`, `claude agents`, `attach`, `stop`, `rm` | Uruchamia sesję bez terminala, lista i podgląd sesji, zatrzymanie i usunięcie. Funkcja w fazie „research preview”. | https://code.claude.com/docs/en/agent-view | `narzedzia/wyko.py`, `skille/wznow`, `narzedzia/wspolne.py` (T1, T16) |
| Worktree: `-w` / `--worktree` | Osobna kopia repo w `.claude/worktrees/<nazwa>` na gałęzi `worktree-<nazwa>`. | https://code.claude.com/docs/en/worktrees | `narzedzia/wyko.py`, `role/wyko.md` (T16) |
| Hooki, PostToolUse | Polecenie uruchamiane po użyciu narzędzia; może dołożyć tekst do kontekstu sesji (`additionalContext`, do 10 000 znaków). | https://code.claude.com/docs/en/hooks | `narzedzia/dziennik/hook_commit.py`, `narzedzia/wyko/ustawienia.json` (T18) |
| `--settings` | Dokłada plik ustawień (hooki, uprawnienia, `attribution`) tylko dla tej sesji; limit 2 MiB. Pole `attribution` nie sprawdzone w dokumentacji (strona bardzo długa), opieramy się na T14. | https://code.claude.com/docs/en/cli-reference , https://code.claude.com/docs/en/settings-reference | `narzedzia/wyko.py`, `narzedzia/archi.py` |
| `--append-system-prompt-file` | Dokłada tekst z pliku do promptu systemowego (u nas: rola). | https://code.claude.com/docs/en/cli-reference | `narzedzia/wyko.py`, `narzedzia/archi.py`, `role/` (T1) |
| Skille | Folder z `SKILL.md` (opis + instrukcje), ładowany na żądanie; leży w `~/.claude/skills/` lub `.claude/skills/`. | https://code.claude.com/docs/en/skills | `skille/` (junction, T15) |
| Podagenci | Plik z frontmatterem (`name`, `description`, `tools`, `model`…) w `~/.claude/agents/`; własne okno kontekstu. | https://code.claude.com/docs/en/sub-agents | `agenci/zwiadowca.md`, `agenci/recenzent.md` (T5, T15) |
| Tryby uprawnień: auto, plan, dontAsk | `plan`: tylko planowanie, bez zmian; `auto`: działa bez pytań z kontrolą bezpieczeństwa; `dontAsk`: odrzuca to, czego nie ma na liście. | https://code.claude.com/docs/en/permission-modes | `narzedzia/wyko.py` (auto, T14), `zasady/baza.md` (plan), `skille/podroz` |
| Artefakty z Claude Code | Sesja publikuje stronę pod prywatnym adresem (claude.ai). | https://code.claude.com/docs/en/artifacts | `narzedzia/dziennik/` |
| Przechowywanie danych w artefakcie (u nas `db`, narzędzie ArtifactData) | Dane trzymane między sesjami, osobiste lub wspólne; domyślnie 100 MB i 25 000 dokumentów. Nazwy `db` i `ArtifactData` **nie znaleziono** w publicznej dokumentacji; to funkcja widoczna w narzędziach sesji. | https://support.claude.com/en/articles/17153992-what-are-artifacts-and-how-do-i-use-them | `narzedzia/dziennik/strona.html`, `hook_commit.py` (T18) |

## Uwagi
- Aliasy modeli i wymagane wersje (np. Sonnet 5.5 od v2.1.284): https://code.claude.com/docs/en/model-config
- `claude attach` po nazwie działa od v2.1.290 (https://code.claude.com/docs/en/agent-view).
- Sprzeczności z `testy.md`: brak.
