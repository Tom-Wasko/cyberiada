# Podróż 02: migracja-lukrum
Start: 2026-11-22 · tryb: nadzorowany · gałąź: `main`
Zadania: Z2

## Cel
LUKRUM w układzie cyberiady: `Pulpit/lukrum` to jedno repo (kod w `gra/`, dokumentacja w korzeniu),
notatki i warsztat przeniesione, auto-pamięć zamieniona na pliki, `archi lukrum` działa jak w każdym projekcie.

## Kryteria sukcesu (zatwierdzone przez szefa)
- [ ] `Pulpit/lukrum` to repo Lukrum: kod w `gra/` (historia jako zmiana nazw), w korzeniu README, CLAUDE.md ≤80 linii,
      `dokumentacja/` wg `szablony/projekt/` (`git log --stat -1`, `git status`).
- [ ] Testy gry przechodzą z nowego układu (`pytest -q` w `gra/` + `node --check`).
- [ ] Praca w `_robocze/wnetrza-cenniki` zachowana (commit na jej gałęzi, `git worktree list`).
- [ ] Cała treść notatek w `dokumentacja/` (mapa plik → miejsce w raporcie wątku); Zadania z numerami Z<n>.
- [ ] Lukrum-notatki: ostatni commit z odnośnikiem, repo zarchiwizowane (`gh repo view --json isArchived`).
- [ ] Wiadomość dla majstra w `dokumentacja/wiedza/wspolpraca.md`.
- [ ] `archiwum/warsztat`, `archiwum/notatki`, brak `lukrum/.claude/agents`.
- [ ] Każdy fakt z pamięci ma miejsce; `--bez-pamieci` włączone; foldery pamięci w archiwum.
- [ ] lukrum w `projekty.yaml`, `archi lukrum` startuje, dziennik pokazuje kartę lukrum.
- [ ] W gicie lukrum brak REVAS, baz, `lokalne.json`, `archiwum/`, `_robocze/`.

## Wątki
| Wątek | Kto | Plik | Stan |
|---|---|---|---|
| szkielet | Archi | (ten plan) | w toku |
| notatki | wyko (repo lukrum, `wyko-lukrum-01-notatki`) | `Pulpit/lukrum/dokumentacja/podroze/01-migracja/watek-notatki.md` | plan |
| domkniecie | Archi | (ten plan) | plan |

## Podsumowanie
