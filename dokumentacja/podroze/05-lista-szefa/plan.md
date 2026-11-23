# Podróż 05: lista-szefa
Start: 2026-11-23 · tryb: nadzorowany · gałąź: `main`
Zadania: Z7

## Cel
Poprawki szefa z 23.11 (jedno zadanie Z7): limit wyko w trybie autonomicznym, układ zadań i kryteriów, oś czasu
pracowników zamiast wykresu „Wątki”, stany wątków bez „?”, pasek po lewej z panelami, działające narzędzie tokenów.

## Kryteria sukcesu (zatwierdzone przez szefa)
- [x] `papa/SKILL.md` i `role/archi.md`: limit 3 wyko w trybie autonomicznym; decyzja w `Decyzje.md`.
- [x] Dziennik: kolumna „Zrobione w tej podróży”; „W toku” to tylko sekcja „W toku” z `Zadania.md`; skill opisuje przesuwanie.
- [x] Hook po scaleniu przypomina o kryteriach i zadaniach (dowód: wynik hooka na próbnym wejściu); kryteria lukrum 03 odhaczone.
  Dowód: hook na HEAD lukrum „Scalenie 03/zestawy…” zaczyna się od „Po scaleniu (zasada podróży…”, na zwykłym commicie 0 trafień;
  kryteria lukrum 03 odhaczył sam archi-lukrum przy zamykaniu podróży (7/7 `[x]`).
- [x] Żaden wątek nie ma „?” zamiast stanu (JSON lukrum, zrzut).
- [x] Oś czasu pracowników: domyślnie dziś, przesuwanie w lewo, Archi na górze z przerwami (zrzuty: komputer, telefon, przesunięta).
- [x] `zuzycie.py --projekt lukrum` działa, testy OK, archi-lukrum dostał brakujące liczby.
  Dowód: `--projekt lukrum --od 2026-11-23` → RAZEM 25,2M; testy `Ran 31 tests … OK`; liczby trybu autonomicznego (22,0M) wysłane.
- [x] Po uwagach szefa: wszystko widać przewijając w dół, projekty jako klocki, oś 6 h z rzędami „naraz” i podpisem przy lewej krawędzi (zrzuty).
  Dowód (05/dziennik2, scalone 26be214): testy 39 OK; lukrum 6 wyko naraz = 6 rzędów; podpisy zmieniają się przy przesunięciu (teraz 03/zestawy, −5 h 03/ukryte, −1 dzień 02/sklepy); telefon scrollWidth 390; strona opublikowana.
- [x] Pasek przycisków po lewej przełącza panele zamiast rozwijanych kart (zrzuty komputer i telefon).
- [x] Testy dziennika OK, strona opublikowana.
  Dowód (05/dziennik, scalone ee0fe12): `unittest discover` → OK (39 testów); JSON lukrum 22 wątki z kto i stanem;
  zrzuty 1280/390 px przejrzane (scrollWidth 390 ≤ 390); strona opublikowana (wersja 6). Ciemny tryb i dotyk: do obejrzenia przez szefa.

## Wątki
| Wątek | Kto | Plik | Stan |
|---|---|---|---|
| 05/dziennik | wyko | `watek-dziennik.md` | scalony |
| 05/dziennik2 | wyko | `watek-dziennik2.md` | scalony |
| 05/zasady | Archi | (bez pliku) | gotowe (skill i rola: zadania, kryteria; hook) |

## Podsumowanie
