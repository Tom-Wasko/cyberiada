# Eksperyment Z10: ustawienia trybów sen i komp

Narzędzie powtarza prawdziwe zadania z historii (lukrum i cyberiada) w różnych ustawieniach
(model × effort × autocompact × wielkość zadania) i mierzy tokeny, czas i jakość. Z wyników wychodzi,
co ustawić w trybie **sen** (najmniej tokenów przy dobrej jakości) i **komp** (najszybciej przy dobrej jakości).

## Uruchomienie
```
python -X utf8 narzedzia/eksperyment/uruchom.py --pokaz     # plan, stopy, szacunek kosztu (nic nie uruchamia)
python -X utf8 narzedzia/eksperyment/uruchom.py             # start, nowy plik wyników
python -X utf8 narzedzia/eksperyment/uruchom.py --wznow     # dokończ po przerwie (pomija zrobione przebiegi)
python -X utf8 narzedzia/eksperyment/raport.py              # tabela i optimum -> _robocze/eksperyment/raport.md
```
Opcje: `--budzet 45M` (stop po tylu ważonych tokenach), `--do 2026-11-29T16:00` (stop w terminie),
`--naraz 3`, `--plan`, `--zachowaj` (nie usuwaj kopii), `--nowy` (odłóż stary plik wyników).

## Zatrzymanie i wznowienie
Ctrl+C (albo zamknięcie okna) zatrzymuje. Wyniki są w `_robocze/eksperyment/wyniki.jsonl`, jedna linia na
przebieg, dopisywana od razu po przebiegu. `--wznow` pomija przebiegi z `"kompletny": true`; niedokończone
(błąd, brak oceny) robi od nowa. Kopie są w `C:/Users/PC/eksperyment/<id>/` (poza każdym repo); po przerwaniu
mogą zostać, kolejny start czyści kopię danego przebiegu.

## Jak działa przebieg
1. `git clone` repo do `~/eksperyment/<id>`, checkout commitu startowego, usunięty `origin` (nic nie wypchnie).
2. `claude -p --output-format json --name eks-<id>` z flagami z `wyko.py: wspolne_flagi`; brief + krótka
   instrukcja idą przez stdin. Limit czasu 90 min.
3. Tokeny: z logu sesji `~/.claude/projects/*/<session_id>.jsonl` (z podagentami) funkcjami `zuzycie.py`;
   `usage` z JSON zapisane obok (`usage_json`).
4. Testy zadania w kopii (zaliczone = kod 0).
5. Ocena 1–5: osobny `claude -p --model sonnet` (brief, diff przebiegu, diff wzorcowy, wynik testów);
   jej tokeny osobno (`ocena_wazone`).
6. Linia w `wyniki.jsonl`, kopia usunięta.

## Stopy i limity
Przed każdym przebiegiem: suma ważonych (przebiegi + oceny) ≥ `--budzet`; albo `~/.claude/cyberiada-limit.json`
świeży (do 15 min) i `seven_day.used` ≥ 95; albo minął `--do`. Limit 5 h w odpowiedzi: czeka do
`five_hour.resets_at` (bez danych 15 min) i powtarza przebieg od zera.

## Pliki
- `zadania.json`: 4 zadania (2 małe, 2 duże), commit startowy, wzorcowy, testy, uzasadnienie.
- `plan.json`: kolejność przebiegów. `plan-proba.json`: jeden przebieg do próby.
- `uruchom.py`, `raport.py`; testy: `narzedzia/dziennik/testy/test_eksperyment.py`.

## Uwagi
- Wielkość zadania to rozmiar zmiany, nie czas: oryginalne sesje trwały 9–17 min (~0,4–1 mln ważonych).
- Ta wersja `claude` nie ma `--max-turns`; ogranicza tylko czas (90 min).
- Pola JSON (`usage`, `duration_ms`, `num_turns`, `session_id`, `total_cost_usd`) sprawdzone na próbnym
  wywołaniu; źródła: https://code.claude.com/docs/en/headless, https://code.claude.com/docs/en/cli-reference.
- Zadania lukrum używają `.venv` z głównego lukrum (kopia go nie ma); plików lukrum narzędzie nie zmienia.
