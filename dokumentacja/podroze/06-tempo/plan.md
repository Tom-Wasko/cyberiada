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
- [ ] `/hejo zolw|krolik`, `/papa zolw` działają, tempo w `Stan.md`
- [ ] `wyko.py --tempo` ustawia model i effort
- [ ] `tempo.py` pokazuje linię idealną i radę
- [ ] statusline zapisuje limit 5h
- [ ] tempo widać w dzienniku
- [ ] badanie z logów w `tokeny.md`, tryby ustawione z liczb
- [ ] eksperymenty zapisane jako Z10
- [ ] recenzja dziennika zrobiona, strona opublikowana

## Wątki
| Wątek | Kto | Plik | Stan |
|---|---|---|---|
| tempo | wyko | `watek-tempo.md` | w toku |
| zasady | Archi | — | plan |
| recenzja | Archi + recenzent | — | plan |

## Podsumowanie
<!-- Na końcu: co zrobione, co odłożone (→ Zadania.md), koszt (narzedzia/zuzycie.py). -->
