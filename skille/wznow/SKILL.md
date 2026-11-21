---
name: wznow
description: Archi wznawia pracę po restarcie komputera albo po wyczerpaniu limitu – odtwarza stan z plików i wznawia przerwane sesje wyko.
disable-model-invocation: true
---
Polecenie: `/wznow`. Stan jest w plikach i commitach, nie w pamięci sesji.

1. Przeczytaj `dokumentacja/Stan.md` (podróż, wątki, tryb, budżet).
2. `claude agents --json --all`: które sesje wyko żyją, które są zatrzymane.
3. Dla każdego wątku w toku: ostatnie commity gałęzi i raport w pliku wątku.
   - Raport gotowy → przegląd i scalenie jak zwykle.
   - Sesja zatrzymana bez raportu → `python -X utf8 C:/Users/PC/cyberiada/narzedzia/wyko.py --wznow <id albo nazwa>`
     (wznawia tę samą sesję w tle, z jej kontekstem).
4. Tryb autonomiczny: przelicz pozostały budżet; jeśli zostało, uruchom znów pętlę kontroli, inaczej koniec trybu autonomicznego.
5. Puls i wpis w `Stan.md` („Wznowione GG:MM po …”), dziennik. Szefowi 3–5 linii: co było przerwane, co wznowione.
