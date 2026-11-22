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
- 2026-11-22 · Dziennik (Z4): kolor projektu (pasek i nagłówek karty, kafle, etykiety stanów), tło jasne; postęp na żywo
  po każdym commicie każdego wyko i Archiego (pilnuje hook); „Czeka na Ciebie” zwinięta, rozwija się sama tylko przy
  nowej sprawie; bez przycisków odpowiedzi, sama lista pytań; „Pomocnik” na stronie jako „pomo”; Fable osobno w zużyciu.
- 2026-11-22 · Dziennik: stare pytania lukrum (P1–P24 z dawnego „Do decyzji”) usunięte; zużycie lukrum osobno przed i po cyberiadzie; zadania jako „Z<n> · krótki tytuł”, opis po kliknięciu, każde w osobnej karcie.
- 2026-11-22 · Przy zamykaniu podróży tabela: zrobione / następnie / reszta do zrobienia (też w preferencjach).
- 2026-11-22 · Dziennik, Zadania: kolumny „W toku”, „Następnie”, „Zaplanowane”; karty przeciągane myszką między kolumnami.

- 2026-11-22 · Dziennik: sekcja „Pracownicy” (kto i gdzie, stan i ostatni krok, tokeny i model, zakończeni dziś zwinięci), odświeżana po każdym commicie; w kolumnach zadań widać 6 pierwszych, reszta po „Pokaż jeszcze”; pasek szybkiego przejścia na górze.
- 2026-11-22 · Wyko: wątek będący kontynuacją (te same pliki) idzie do istniejącego wyko wiadomością; nowy wyko tylko na nowy obszar kodu.
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
- 2026-11-22 · Hook zapisu postępu tylko w sesjach wyko i Archi (`--settings` w `wyko.py`/`archi.py`), bez zmian w globalnym `settings.json`.
- 2026-11-22 · Przesunięcia zadań w dzienniku idą do bazy (`uklad/<projekt>`, zapis tylko właściciel); strona pokazuje je od razu, Archi przenosi je do `Zadania.md` (`przenies.py`, wskazówka z hooka) i kasuje dokument.
- 2026-11-22 · Lista pracowników: `dziennik/pracownicy.py` (claude agents + logi + git) liczy ją hook po commicie, sesja tylko wysyła plik do `pracownicy/lista`.
