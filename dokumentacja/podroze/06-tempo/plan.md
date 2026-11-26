# Podróż 06: tempo pracy
Start: 2026-11-24 · tryb: nadzorowany · gałąź: `main`
Zadania: Z8, Z9, Z10 (eksperymenty: pewnie piątek wieczorem)

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
- [ ] eksperymenty Z10 zrobione, tryby poprawione (przeniesione do podróży 07)
- [x] recenzja dziennika zrobiona, strona opublikowana

## Wątki
| Wątek | Kto | Plik | Stan |
|---|---|---|---|
| tempo | wyko | `watek-tempo.md` | scalony |
| zasady | Archi | — | zrobiony |
| recenzja | recenzent + wyko | `watek-recenzja.md` | scalony, strona opublikowana (wersja 9) |

## Podsumowanie
Zamknięta 2026-11-26 przez szefa. Zrobione: **Z8** (tempa żółw / zwykły / królik: badanie z logów w `tokeny.md`, `statusline.py`, `tempo.py`, `wyko.py --tempo`, skille), **Z9** (recenzja dziennika: 20 poprawek A/B/C, strona opublikowana; potem kolory: role jak przed recenzją, cyberiada kosmiczny fiolet, lukrum szmaragd). Przeniesione: **Z10** (eksperymenty) do podróży 07 (szef 26.11). Koszt od 24.11: 7,3M tokenów ważonych (Archi 4,8M, wyko 06/recenzja 1,0M, wyko 06/tempo 1,0M, agenci 0,4M). Wniosek: tempa trafiają do archiwum, szef 26.11 zastępuje je trybami nadzorowany / sen / szkoła (podróż 07).
