# cyberiada
System pracy z Claude Code (role, skille, agenci, narzędzia) używany we wszystkich projektach szefa.
Opis i ściągawka poleceń: `README.md`. Zasady ogólne ładują się same (`zasady/` przez `~/.claude/rules`).

## Polecenia
```
python -X utf8 narzedzia/instaluj.py --sprawdz     # stan instalacji na tym komputerze
python -X utf8 narzedzia/zuzycie.py --od RRRR-MM-DD
python -X utf8 narzedzia/wyko.py <plik wątku> --pokaz   # polecenie startu wyko bez uruchamiania
```

## Gdzie co jest
- Mapa repozytorium: `README.md`. Wyniki prób: `wiedza/testy.md`.
- `dokumentacja/`: `Stan.md` (teraz), `Zadania.md`, `Decyzje.md`, `podroze/NN-temat/`.
- `_robocze/` poza gitem.

## Zasady projektu
- Zmiana `zasady/`, `role/` albo `skille/` działa w innych sesjach od ich następnego startu (albo po `/compact`).
- `zasady/baza.md` ≤ 100 linii, `preferencje.md` ≤ 500 słów: każde słowo kosztuje w każdej sesji.
- Każde polecenie dla szefa trafia do ściągawki w `README.md`.
- Twierdzenia o Claude Code: ze źródła (code.claude.com/docs) albo z próby zapisanej w `wiedza/testy.md`.

## Compact instructions
Zachowaj: bieżącą podróż i wątki (stan, sesje wyko), decyzje szefa z tej sesji (są w `Decyzje.md`), pliki w toku,
wyniki testów, otwarte pytania.
