# Wątek: eksperyment (podróż 07)

## Brief
- **Cel:** narzędzie, które od jutra (27.11) samo puszcza testy Z10. Te same prawdziwe zadania z historii lukrum i cyberiady są powtarzane w różnych ustawieniach (model × effort × autocompact × wielkość zadania). Mierzy tokeny, czas i jakość, żeby ustawić tryby sen (najmniej tokenów przy dobrej jakości) i komp (najszybciej przy dobrej jakości).
- **Rodzaj:** trudny
- **Ustalone (nie sprawdzaj ponownie):**
  - **Zadania = powtórka historii.** Weź scalone wątki wyko, które mają plik wątku z briefem i testy:
    - lukrum: `C:/Users/PC/Pulpit/lukrum`, wątki w `dokumentacja/podroze/*/watek-*.md`; testy `python -X utf8 -m pytest -q -p no:cacheprovider testy/<plik>.py`, tylko dotknięte pliki, bo pełne trwają ok. 7 min;
    - cyberiada: ten repo, testy `python -X utf8 -m unittest discover -s narzedzia/dziennik/testy`.
    Dla każdego zadania potrzebne są: commit startowy (rodzic scalenia albo pierwszego commitu wątku), brief (sekcja „Brief” pliku wątku, bez „Raportu”), polecenie testów i diff wzorcowy (to, co naprawdę scalono).
    Wybierz **2 małe** (oryginalnie do ok. 1 h, jeden z lukrum, jeden z cyberiady) i **2 duże** (2 h i więcej). Zapisz je w `narzedzia/eksperyment/zadania.json` z uzasadnieniem.
  - **Kopia:** `git clone` repo do folderu **poza każdym repo i poza `C:/Users/PC/cyberiada`**, np. `C:/Users/PC/eksperyment/<przebieg>/`. Inaczej sesja wczyta `CLAUDE.md` z folderu nadrzędnego. Potem checkout commitu startowego i usunięcie zdalnego `origin`, żeby nic nie dało się wypchnąć. Plików prawdziwego lukrum nie zmieniasz (tylko czytasz historię).
  - **Przebieg:** `claude -p "<brief + krótka instrukcja: zrób zadanie, uruchom testy, zacommituj>" --output-format json` w kopii, z flagami z `wyko.py`.
    - Funkcja `wspolne_flagi(model, effort, autocompact)` ma model, effort, autocompact, uprawnienia i ustawienia. Importuj ją, nie kopiuj. Jej podpis się nie zmieni, choć wątek 07/tryby zmienia `wyko.py`.
    - Nazwa sesji `eks-<przebieg>`: hook dziennika działa tylko dla `wyko-`/`archi-`, więc przebiegi nie piszą do dziennika.
    - Sprawdź w dokumentacji, jakie pola daje `--output-format json` (`usage`, `duration_ms`, `num_turns`, `session_id`, `total_cost_usd`) i jak ustawić nazwę oraz limit tur. Źródła: https://code.claude.com/docs/en/headless i https://code.claude.com/docs/en/cli-reference, odnośnik w raporcie.
    - Limit czasu przebiegu: 90 min.
  - **Tokeny ważone** policz z logu sesji (`~/.claude/projects/*/<session_id>.jsonl`) funkcjami z `narzedzia/zuzycie.py` (`wpisy`, `wazone` itd., import). Dzięki temu liczby są porównywalne z resztą dziennika. `usage` z JSON zapisz obok jako sprawdzenie.
  - **Jakość:**
    - testy zadania w kopii po przebiegu: zaliczone / niezaliczone i liczby;
    - ocena 1–5 od osobnego `claude -p --model sonnet` z promptem recenzenta (`agenci/recenzent.md` jako wzór: brief, diff przebiegu, diff wzorcowy, wynik testów → JSON `{"ocena": n, "uzasadnienie": "…"}`); jej tokeny zapisz osobno.
  - **Limity (budżet: cały pozostały limit tygodnia, decyzja szefa 26.11):**
    - przed każdym przebiegiem sprawdź stop: suma ważonych przebiegów ≥ `--budzet` (domyślnie 45M), albo `~/.claude/cyberiada-limit.json` świeży (do 15 min) i `seven_day.used` ≥ 95, albo minął `--do` (domyślnie 2026-11-29 16:00);
    - gdy przebieg trafi na limit 5 h (błąd w JSON/stderr), poczekaj do resetu (`five_hour.resets_at` z pliku limitu albo z komunikatu; bez danych co 15 min) i powtórz ten przebieg;
    - najwyżej `--naraz` przebiegów naraz (domyślnie 3).
  - **Plan przebiegów** (`narzedzia/eksperyment/plan.json`, w kolejności ważności; narzędzie robi je po kolei, aż do stopu):
    1. Sonnet × effort low/medium/high × 4 zadania, autocompact 200k;
    2. autocompact 120k na dużych (Sonnet medium);
    3. Haiku low/medium na małych, Opus medium na dużych;
    4. drugie powtórzenia z punktu 1, potem z 2 i 3.
  - **Wynik:** każdy przebieg to jedna linia w `_robocze/eksperyment/wyniki.jsonl`: id, zadanie, wielkość, model, effort, autocompact, start, czas, tury, tokeny ważone i surowe, testy, ocena, koszt oceny, błędy. Plik jest odporny na przerwanie: po ponownym starcie pomija zrobione przebiegi (`--wznow`). Do tego `raport.py`: tabela Markdown w `_robocze/eksperyment/raport.md` i optimum. Dla snu najmniej ważonych przy ocenie ≥ 4 i zaliczonych testach, dla komp najkrótszy czas przy tych samych warunkach, osobno dla małych i dużych.
  - Testy `unittest` w `narzedzia/dziennik/testy/` (pytest nie ma); `claude` i git w testach udawaj (bez prawdziwych przebiegów).
- **Decyzje szefa (26.11):** testy od 27.11 do 29.11 16:00 na cały pozostały limit tygodnia (reset 30.11 16:00). Tryby i Z10 opisane w `dokumentacja/Decyzje.md`.
- **Do zrobienia:** wybór zadań (`zadania.json`), `narzedzia/eksperyment/{uruchom.py, raport.py, plan.json, zadania.json, README.md}`, testy. Na koniec **jedna próba na prawdziwym `claude`**: najmniejsze zadanie, Haiku, effort low, `--budzet 2M`, przez całą ścieżkę (kopia → przebieg → testy → ocena → wpis w `wyniki.jsonl` → `raport.md`). Kopię po próbie usuń.
- **Pliki do zmiany / utworzenia:** nowy folder `narzedzia/eksperyment/`, testy w `narzedzia/dziennik/testy/test_eksperyment.py`.
  **Nie ruszaj:** `wyko.py`, `tempo.py`/`tryb.py`, `zuzycie.py` (tylko import), `dziennik/`, `role/`, `skille/`, `zasady/`, `README.md`, dokumentacja, pliki lukrum.
- **Gotowe, gdy:**
  - `python -X utf8 -m unittest discover -s narzedzia/dziennik/testy` → OK;
  - próba Haiku daje pełny wpis w `_robocze/eksperyment/wyniki.jsonl` i `raport.md` (w raporcie: wpis i jego koszt);
  - `python -X utf8 narzedzia/eksperyment/uruchom.py --pokaz` wypisuje plan, stopy i szacowany koszt (bez uruchamiania).
- **Zrzuty ekranu:** nie.
- **Dokumenty do poprawienia:** `narzedzia/eksperyment/README.md` (jak uruchomić, wznowić, zatrzymać).
- **Archi:** archi-cyberiada

## Raport
**Zrobione:** narzedzie `narzedzia/eksperyment/` (`uruchom.py`, `raport.py`, `zadania.json`, `plan.json` z 40 przebiegami, `plan-proba.json`, `README.md`) i testy `narzedzia/dziennik/testy/test_eksperyment.py`. Stopy: budzet 45M, limit tygodniowy >= 95, termin 29.11 16:00, limit 5 h (czeka do resetu), `--naraz 3`, `--wznow`. Nie ruszone: pliki spoza briefu.

**Zadania (uzasadnienie w `zadania.json`):** male: `debet` (lukrum, blad w silniku, 2 pliki/29 linii), `generator` (cyberiada, nowe narzedzie, 700 linii); duze: `zestawy` (lukrum, 14 plikow, 4 warstwy), `tempo` (cyberiada, 9 plikow, 794 linie).

**Dowody:**
- `python -X utf8 -m unittest discover -s narzedzia/dziennik/testy` -> `Ran 96 tests in 9.568s` / `OK`
- `uruchom.py --pokaz` -> `Szacowany koszt niezrobionych: ~48M waznych`, stopy: budzet 45M, termin 2026-11-29 16:00, limit seven_day >= 95, naraz 3.
- Proba (Haiku, low, 200k, `debet`): `koniec debet-haiku-low-200k-p1: testy OK ocena 5 wazone 14937`. Wpis: czas 1129 s (z testami ok. 6,5 min), 24 tury, 1,16M tokenow surowych, 14937 waznych, koszt 0,030 USD; ocena Sonneta 5 (diff 90 linii), jej koszt 27488 waznych / 0,055 USD. Lacznie ok. 0,085 USD. Wpis i `raport.md` zostaly w `_robocze/eksperyment/` tego worktree (poza gitem).

**Uwagi / problemy znalezione przez probe i naprawione:**
- Pierwsza proba dala diff 0 i testy OK: test z briefu pada tylko w pelnym przebiegu (na starcie: 1 failed, 1026 passed), nie w `testy/pieniadze`. Polecenie testow `debet` to teraz caly folder `testy` (ok. 6,5 min na przebieg; wpisalem to w szacunek).
- Diff wzorcowy byl pusty (zla skladnia pathspec) i obejmowal cudze prace ze scalenia: teraz `:(exclude)` i diff konczy sie na drugim rodzicu scalenia (test z prawdziwym gitem).
- Zaden oryginal nie trwal 1 h ani 2 h+ (9-17 min): wielkosc = rozmiar diffu. Brak `--max-turns` w tej wersji: tylko limit czasu 90 min.
- Dokumentacji nie pobieralem (brak sieci): pola `--output-format json` sprawdzone probami, zrodla w README. Szacunek 48M jest zgrubny (popraw po pierwszych wynikach). Zadania lukrum uzywaja `.venv` z glownego lukrum.
- Kopie prob `C:/Users/PC/eksperyment/_proba` i `_ocena` leza poza worktree (moj zakres usuwania konczy sie na worktree): do skasowania recznie, nastepne przebiegi same usuwaja swoje kopie.

## Propozycje
- Przed pelnym planem puscic `--naraz 1` na 2-3 przebiegach i poprawic szacunek, bo `debet` jest wolny (testy 6,5 min).
