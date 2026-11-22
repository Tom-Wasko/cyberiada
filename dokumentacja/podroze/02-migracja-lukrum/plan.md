# Podróż 02: migracja-lukrum
Start: 2026-11-22 · tryb: nadzorowany · gałąź: `main`
Zadania: Z2

## Cel
LUKRUM w układzie cyberiady: `Pulpit/lukrum` to jedno repo (kod w `gra/`, dokumentacja w korzeniu),
notatki i warsztat przeniesione, auto-pamięć zamieniona na pliki, `archi lukrum` działa jak w każdym projekcie.

## Kryteria sukcesu (zatwierdzone przez szefa)
- [x] `Pulpit/lukrum` to repo Lukrum: kod w `gra/` (historia jako zmiana nazw), w korzeniu README, CLAUDE.md ≤80 linii,
      `dokumentacja/` wg `szablony/projekt/` (`git log --stat -1`, `git status`).
- [x] Testy gry przechodzą z nowego układu (`pytest -q` w `gra/` + `node --check`).
- [x] Praca w `_robocze/wnetrza-cenniki` zachowana (commit na jej gałęzi, `git worktree list`).
- [x] Cała treść notatek w `dokumentacja/` (mapa plik → miejsce w raporcie wątku); Zadania z numerami Z<n>.
- [x] Lukrum-notatki: ostatni commit z odnośnikiem, repo zarchiwizowane (`gh repo view --json isArchived`).
- [x] Wiadomość dla majstra w `dokumentacja/wiedza/wspolpraca.md`.
- [x] `archiwum/warsztat`, `archiwum/notatki`, brak `lukrum/.claude/agents`.
- [x] Każdy fakt z pamięci ma miejsce; `--bez-pamieci` włączone; foldery pamięci w archiwum.
- [x] lukrum w `projekty.yaml`, `archi lukrum` startuje, dziennik pokazuje kartę lukrum.
- [x] W gicie lukrum brak REVAS, baz, `lokalne.json`, `archiwum/`, `_robocze/`.

## Wątki
| Wątek | Kto | Plik | Stan |
|---|---|---|---|
| szkielet | Archi | (ten plan) | gotowe |
| notatki | wyko (repo lukrum, `wyko-lukrum-01-notatki`) | `Pulpit/lukrum/dokumentacja/podroze/01-migracja/watek-notatki.md` | gotowe (dokończył Archi) |
| domkniecie | Archi | (ten plan) | gotowe |

## Podsumowanie
Zakończona 2026-11-22. Zrobione: Z2.
- Szkielet: kod w `gra/` (lukrum 4027bf5, 51d3acf; 876 testów OK), README, CLAUDE.md (43 linie), `dokumentacja/`;
  `wnetrza-cenniki` zachowana (4e53940); `.claude/agents` usunięte; lukrum w `projekty.yaml`.
- Notatki: cała treść w `lukrum/dokumentacja/` (0340624; mapa plików w raporcie `watek-notatki.md`), Z1–Z28, P1–P24;
  grep nazw starej gry i `[[` → pusto; `git ls-files` bez baz, `lokalne.json`, archiwum i `_robocze`.
- Domknięcie: Lukrum-notatki 71a3c9e + `isArchived: true`; wiadomość dla majstra (wpis 22.11 w `wiedza/wspolpraca.md`);
  `autoMemoryEnabled: false`; `_archiwum/{warsztat,notatki,pamiec}`; dziennik z kartą lukrum.
- Problemy: wyko notatki dwa razy padł na „Autocompact is thrashing” (próg 100k/120k) → progi 250k/200k (4e1151e);
  sesja Archiego też miała stare 120k, pomógł restart przez `archi`.
- Odłożone: nic.
- Koszt (`zuzycie.py --od 2026-11-22`): archi-cyberiada 8,82 mln ważonych tokenów, wyko-lukrum-01-notatki 0,55 mln,
  razem 9,38 mln.
