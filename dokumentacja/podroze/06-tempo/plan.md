# Podróż 06: tempo pracy
Start: 2026-11-24 · tryb: nadzorowany · gałąź: `main`
Zadania: Z8, Z9 (Z10 odłożone do „Zaplanowane”)

## Cel
Trzy tempa pracy: żółw (najwięcej pracy z limitu 5h, bez przestojów), zwykły (jak dziś), królik (szybko teraz).
Parametry trybów z badania logów. Na końcu auto recenzja dziennika.

## Tryby (punkt startowy, poprawiany po badaniu z logów)
| | żółw | zwykły | królik |
|---|---|---|---|
| Archi | szef wpisuje `/model opusplan` i `/autocompact 150k`; mało tur, krótkie odpowiedzi, `/compact` po scaleniu | jak dziś | Opus, jak dziś |
| wyko | Sonnet, effort low (mechaniczne) / medium, autocompact 120k, duże wątki, Haiku do drobnych | Sonnet medium | Sonnet medium, high przy trudnych; zadanie wolno dzielić |
| Ile wyko | tyle, by trzymać linię idealną (`tempo.py`); autonomicznie max 3 | jak dziś | ile trzeba; autonomicznie max 3 |
| Czekanie | nigdy: Archi robi małe zadania, gdy wyko pracują | — | — |

## Kryteria sukcesu (zatwierdzone przez szefa)
- [x] `/hejo zolw|krolik`, `/papa zolw` działają, tempo w `Stan.md`
- [x] `wyko.py --tempo` ustawia model i effort
- [x] `tempo.py` pokazuje linię idealną i radę
- [x] statusline zapisuje limit 5h
- [x] tempo widać w dzienniku
- [x] badanie z logów w `tokeny.md`, tryby ustawione z liczb
- [x] eksperymenty zapisane jako Z10
- [ ] recenzja dziennika zrobiona, strona opublikowana

## Wątki
| Wątek | Kto | Plik | Stan |
|---|---|---|---|
| tempo | wyko | `watek-tempo.md` | scalony |
| zasady | Archi | — | zrobiony |
| recenzja | Archi + recenzent | — | w toku |

## Podsumowanie
<!-- Na końcu: co zrobione, co odłożone (→ Zadania.md), koszt (narzedzia/zuzycie.py). -->
