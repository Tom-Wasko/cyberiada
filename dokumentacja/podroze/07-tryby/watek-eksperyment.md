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
<!-- Pisze wyko na końcu. -->
