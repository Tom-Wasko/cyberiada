# Wątek: wiedza (podróż 04)

## Brief
- **Cel:** trzy krótkie notatki w `dokumentacja/wiedza/` ze źródłami, żeby Archi i szef mieli sprawdzoną wiedzę
  zamiast domysłów (Z3).
- **Ustalone (nie sprawdzaj ponownie):** cyberiada to system pracy szefa z Claude Code (README.md). Wyniki prób
  na tym komputerze są w `dokumentacja/wiedza/testy.md` (T1–T18). Zużycie liczy `narzedzia/zuzycie.py` (funkcja
  `wazone`: wagi cache odczyt 0,1, cache zapis 2, wyjście 5, mnożniki modeli w `mnoznik`).
  Źródła: przede wszystkim code.claude.com/docs i docs.claude.com / anthropic.com (oficjalne), potem inne.
- **Decyzje szefa:** wiedza ze źródeł, nie wymyślona; teksty proste, bez żargonu (`zasady/preferencje.md`).
- **Pliki do utworzenia:** `dokumentacja/wiedza/tokeny.md`, `telefon.md`, `claude-code.md`. **Nie ruszaj:** nic innego
  (bez zmian w kodzie, testy.md, README — README poprawi Archi).
- **Treść** (każda notatka do ok. 1 strony, po polsku, prosto; każde twierdzenie z odnośnikiem; na górze
  „Sprawdzone: 2026-11-22”):
  1. `tokeny.md`: jak liczą się tokeny i koszt (wejście, wyjście, cache odczyt/zapis i jego czas życia, różnice
     modeli), limity planu (okno 5 h, limit tygodniowy), co zjada kontekst (start sesji, agenci, skille, MCP),
     praktyczne zasady oszczędzania. Na końcu: czy wagi w `zuzycie.py` zgadzają się ze źródłami (tak/nie, co poprawić).
  2. `telefon.md`: Remote Control, powiadomienia push, artefakty claude.ai w telefonie: co działa, ograniczenia.
  3. `claude-code.md`: funkcje, których używa cyberiada: sesje w tle (`--bg`, `claude agents`), worktree (`-w`),
     hooki (PostToolUse), `--settings`, `--append-system-prompt-file`, skille, podagenci, auto mode, plan mode,
     artefakty z bazą (`db`). Dla każdej: co robi (1–2 zdania), odnośnik, gdzie cyberiada jej używa (plik).
  Gdy źródło przeczy wynikowi z `testy.md`: zapisz uwagę „sprzeczne z T<n>”, nie rozstrzygaj.
- **Gotowe, gdy:** 3 pliki istnieją; `grep -c "https://" dokumentacja/wiedza/*.md` → co najmniej 5 na notatkę;
  żadna sekcja bez odnośnika. Raport poniżej z listą sprzeczności (albo „brak”).
- **Zrzuty ekranu:** nie.
- **Dokumenty do poprawienia:** brak (README robi Archi).
- **Archi:** archi-cyberiada

## Raport
