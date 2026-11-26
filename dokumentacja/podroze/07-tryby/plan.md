# Podróż 07: tryby
Start: 2026-11-26 · tryb: nadzorowany · gałąź: `main`
Zadania: Z11, Z10

## Cel
Szef 26.11: tempa (żółw, zwykły, królik) i polecenia /hejo, /papa idą do archiwum. Szef zostawia mi zaprojektowanie nowego systemu poleceń.
Nowe tryby to **nadzorowany**, **sen** i **szkoła**. Uwagi szefa:
1. Archi nie otwiera nowych wyko po zamknięciu starych.
2. Archi na Sonnecie słabo pyta i planuje.
3. archi-lukrum (podróż 04) nie brał zadań zaplanowanych po skończeniu tych w toku.

Testy Z10 trwają od 27.11 do niedzieli 29.11, godz. 16:00, i dostają cały pozostały limit tygodnia (ok. 37%, reset w poniedziałek 30.11 o 16:00). Do tego czasu nowe tryby muszą działać, więc dziś budujemy, a jutro testujemy.

## Nowy system poleceń (zamiast /hejo, /papa, /podroz, /wznow)
| Polecenie | Co mówi szef | Tryb |
|---|---|---|
| `/komp` | siedzę przy komputerze | **nadzorowany**: szybko (jak dawny królik), okienka, plan mode |
| `/sen` | idę spać | **sen**: przed wyjściem plan nocy (krótko, okienkiem), potem całkiem sam |
| `/szkola 16:00` | wychodzę, wracam o 16:00 | **szkoła**, stan „sam” |
| `/hej` | w szkole: jestem / znikam (przełącza) | szkoła „jestem”: Archi zadaje zebrane pytania okienkiem (na telefonie też); szkoła „znikam”: pracuje sam. Archi w odpowiedzi zawsze potwierdza stan („Jesteś…” / „Znikasz…”) |

**Bez /podroz i /wznow:** przy otwarciu czatu Archi sam robi start.
- `archi <projekt>` wysyła prompt startowy, także przy wznowieniu sesji.
- Archi czyta `Stan.md`, sprawdza wyko, wznawia przerwaną pracę (dawne `/wznow`) i zadaje pierwsze pytanie okienkiem o podróż: dalej / nowa (z propozycjami tematów) / zamknąć / porzucić.
- Opis podróży (start, koniec, porzucenie) przechodzi ze skilla do `role/podroz.md`, który Archi czyta, gdy go potrzebuje.

Linia w `Stan.md`: `Tryb: sen od 23:10` albo `Tryb: szkoła do 16:00 (jestem)` (zamiast `Tryb:` i `Tempo:`).

## Zasady trybów
| | nadzorowany `/komp` | sen `/sen` | szkoła `/szkola` |
|---|---|---|---|
| Cel | szybko, bo szef ma mało czasu | cały limit 5 h zużyty w 5 h, bez przestojów | praca rozłożona do końca ramy |
| Hamulec | brak | tygodniowy: noc nie zjada więcej, niż wypada z równego rozłożenia tygodnia | tygodniowy (jak w śnie) |
| Pytania | okienkiem, od razu | brak, Archi bierze zadania bez decyzji szefa | przy „znikam”: zapisuje do „Czeka na szefa” + push, nie przerywa; przy „jestem” (`/hej`): okienkiem |
| Archi | Opus | Opus, mało tur, krótko | Opus |
| wyko | Sonnet medium, high przy trudnych; zadanie wolno dzielić na kilku | Sonnet low (mechaniczne) / medium, autocompact 120k, duże wątki | jak w śnie, liczba wyko z linii do końca ramy |
| Ile wyko | ile trzeba | z `tryb.py`, najwyżej 3 | z `tryb.py`, najwyżej 3 |
| Scalanie | `main` + push | gałąź `podroz-NN`, bez push i bez nieodwracalnych rzeczy | jak w śnie |
| Gdy zadania się skończą | razem nowy plan | sam bierze następne z listy (Następnie, potem Zaplanowane bez decyzji szefa) | jak w śnie |

- **Archi zawsze na Opusie** (uwaga 2). Rada `opusplan` znika.
- **Po końcu ramy szkoły** Archi robi podsumowanie z powiadomieniem push. Do `/komp` pracuje dalej jak w śnie.
- **Ciągłość (uwagi 1 i 3), we wszystkich trybach:** po scaleniu albo zatrzymaniu wyko Archi w tej samej turze bierze następne zadanie, pisze wątek i uruchamia wyko. Hook po scaleniu przypomina o tym, z numerem następnego zadania z `Zadania.md`.
- Liczby powyżej to punkt startowy. Po testach Z10 ustawiam je z wyników.

## Kryteria sukcesu (zatwierdzone przez szefa)
- [ ] `/komp`, `/sen`, `/szkola`, `/hej` działają, tryb w `Stan.md`
- [ ] nowy czat Archiego sam pyta o podróż
- [x] `tryb.py`: linia 5 h, rama szkoły, hamulec tygodnia
- [x] `wyko.py --tryb` ustawia model i effort
- [ ] po scaleniu Archi sam bierze następne zadanie
- [x] stare tryby w archiwum
- [x] tryb widać w dzienniku
- [ ] narzędzie eksperymentów gotowe
- [ ] testy Z10 zrobione do 29.11 16:00
- [ ] tryby poprawione z wyników

## Wątki
| Wątek | Kto | Plik | Stan |
|---|---|---|---|
| tryby | wyko | `watek-tryby.md` | scalony, strona opublikowana |
| eksperyment | wyko | `watek-eksperyment.md` | w toku |
| zasady | Archi | — | zrobiony |
| testy | Archi + narzędzie | — | plan (27.11–29.11 16:00) |

## Podsumowanie
<!-- Na końcu: co zrobione, co odłożone (→ Zadania.md), koszt (narzedzia/zuzycie.py). -->
