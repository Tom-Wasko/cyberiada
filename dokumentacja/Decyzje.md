# Decyzje

## Szefa
- 2026-11-21 · Nazwa cyberiada, prywatne repo `Tom-Wasko/cyberiada` na GitHubie.
- 2026-11-21 · Role: Pomocnik (domyślny), Archi (jeden na projekt), wyko (sesja w tle na wątek), agenci tylko do
  krótkich zadań.
- 2026-11-21 · W trybie autonomicznym (/papa) scalanie do gałęzi `podroz-NN`, do `main` po powrocie szefa (/hejo); odpowiedzi z telefonu czatem Remote Control;
  dziennik bez formularza.
- 2026-11-21 · Nazwy trybów: **tryb nadzorowany** (polecenie `/hejo`) i **tryb autonomiczny** (polecenie `/papa`);
  „hejo” i „papa” to tylko nazwy poleceń.
- 2026-11-21 · Jedna numeracja w każdym projekcie: zadanie `Z<n>`, podróż `NN`, wątek `NN/nazwa` (szczegóły: `role/archi.md`).
- 2026-11-21 · Polecenia osobne, wszystkie w ściągawce `README.md`; każde działa też zwykłym tekstem.
- 2026-11-21 · Dokumentacja projektu: README, CLAUDE.md, `Stan.md`, `Zadania.md`, `Decyzje.md`, `podroze/`.
- 2026-11-21 · Podróż 01 = dziennik. Plan mode przełączany automatycznie (szef obecny), potem auto mode.
- 2026-11-21 · Dziennik: Czeka na Ciebie, stan podróży i wątków, puls, decyzje Archiego, zadania i historia podróży,
  koszty; „lubię dużo informacji, danych i wykresów”.
- 2026-11-21 · Wykresy dziennika: tokeny dzień po dniu (według projektów), kto zużywa (Archi / wyko / agenci /
  Pomocnik na podróż), postęp podróży (oś czasu wątków + kryteria), commity dzień po dniu, szacunek okna 5 h.
- 2026-11-21 · Dane dziennika w bazie strony (`db`): strona publikowana raz, każdy Archi zapisuje tylko swój projekt.
- 2026-11-21 · Układ dziennika: jedna lista kart projektów (rozwijane), na górze „Czeka na Ciebie (N)”;
  przy pytaniach przycisk „kopiuj odpowiedź” (np. `cyberiada P1: A`).

- 2026-11-22 · Podróż 02 = migracja lukrum. `Pulpit/lukrum` to repo Tom-Wasko/Lukrum: w korzeniu README, CLAUDE.md,
  `dokumentacja/`, cały kod gry w `gra/` (jak w cyberiadzie).
- 2026-11-22 · Notatki lukrum w całości do `dokumentacja/` (Postęp → Zadania, Do decyzji → pytania w Stan, Funkcje →
  `funkcje/`, dziennik lidera, serie i rejestr → historia); repo Lukrum-notatki: ostatni commit z odnośnikiem i archiwizacja.
- 2026-11-22 · Warsztat lukrum do `archiwum/warsztat` (lokalnie), `.claude/agents` i import `@warsztat/ZESPOL.md` usunięte;
  stary panel zespołu zostaje, nieodświeżany.
- 2026-11-22 · Auto-pamięć lukrum: zasady codzienne do CLAUDE.md projektu, reszta do Decyzji; potem `--bez-pamieci`,
  foldery pamięci do archiwum.
- 2026-11-22 · Wiadomość dla majstra o nowym układzie pisze Archi (w dokumentacji), wysyła szef.
- 2026-11-22 · Lista poprawek od szefa: jedno zadanie Z<n> może obejmować wiele poprawek.
- 2026-11-22 · Próg kompaktowania: Archi 250k, wyko 200k (było 120k/100k; za częste i długie kompaktowanie).

## Archiego
- 2026-11-21 · `wiedza/` przeniesiona do `dokumentacja/wiedza/`, tak jak w szablonie projektu; reszta struktury
  repo bez zmian (każdy folder ma jedno zadanie).
- 2026-11-21 · Baza i preferencje przez dowiązanie `~/.claude/rules` (bez `@import`, bez pytań o zewnętrzne pliki).
- 2026-11-21 · Rola przez `--append-system-prompt-file` ze ścieżką bezwzględną, nie `--agent`.
- 2026-11-21 · Wyko: `--permission-mode auto` + lista dozwolonych/zakazanych, `--no-chrome`, worktree `-w podroz-NN-<wątek>`.
- 2026-11-21 · `attribution: false` w ustawieniach globalnych (wyko dopisywał Co-Authored-By).
- 2026-11-21 · Wyko to rola, nie definicja agenta; agenci tylko zwiadowca i recenzent.
- 2026-11-21 · Instalator: cienki `zainstaluj.ps1` + `narzedzia/instaluj.py`.
- 2026-11-21 · Dziennik: generator (`narzedzia/dziennik/generuj.py`, wyko) i strona (Archi) wiąże schemat JSON
  z `podroze/01-dziennik/watek-generator.md`; pytania w „Czeka na szefa” w formacie `P1:` + opcje `A:`.
- 2026-11-21 · Testy narzędzi na `unittest` z biblioteki standardowej (pytest nie jest zainstalowany).
- 2026-11-21 · Dziennik to zwykła strona z bazą `db` (zamiast typu Dashboard): własny układ kart, pytań i 5 wykresów.
