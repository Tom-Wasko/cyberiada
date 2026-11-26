---
name: podroz
description: Archi zaczyna, kończy albo porzuca podróż (plan, wątki, scalanie, sprzątanie). Wywołuje go sam Archi po odpowiedzi szefa na pytanie startowe o podróż; szef nie wpisuje polecenia.
argument-hint: "[temat] | koniec | porzuc"
user-invocable: false
effort: high
---
Skill `podroz` z argumentem `$ARGUMENTS` (wywołuje go Archi, szef wybiera w okienku startowym). Wykonuje Archi w folderze projektu. Szablony: `C:/Users/PC/cyberiada/szablony/`.

## Start (`podroz` albo `podroz <temat>`)
1. `dokumentacja/Stan.md`: jeśli podróż jest w toku, powiedz to i zaproponuj okienkiem dalszą pracę albo zamknięcie.
2. Temat: z argumentu albo od szefa. Bez tematu zaproponuj 2–4 tematy z `Zadania.md` (okienko, rekomendacja).
3. **Tryb komp:** wejdź w plan mode (EnterPlanMode). Doprecyzuj cel pytaniami (okienko, po 4), ustal sprawdzalne
   kryteria sukcesu i wątki: kto (Archi sam: do ok. 20 poleceń; wyko: obszerny), pliki rozłączne między wątkami.
   Plan do zatwierdzenia przez ExitPlanMode; zatwierdzenie = zgoda szefa na cel i kryteria. Dalej auto mode.
   **Sen i szkoła:** bez plan mode; zacznij tylko podróż, której cel i kryteria są już w `Zadania.md` albo w ustaleniach;
   inaczej zapisz pytanie w „Czeka na szefa” i czekaj.
4. Utwórz `dokumentacja/podroze/NN-temat/plan.md` z `plan-podrozy.md` (NN = następny numer, dwie cyfry);
   w nagłówku numery zadań `Z<n>`, które podróż realizuje (nowe zadanie dostaje numer z licznika).
   Kryteria piszesz teraz, krótko (jedna linia, kilka słów; dowody w raporcie wątku, nie pod kryterium); gdy podróż się rozszerza, dopisujesz nowe. Zadania podróży przenieś w `Zadania.md` do „Następnie”. Wpisz podróż i wątki do `Stan.md`. Commit.
5. Dla każdego wątku wyko: `watek-<nazwa>.md` z `watek.md` (pełny brief), commit, potem
   `python -X utf8 C:/Users/PC/cyberiada/narzedzia/wyko.py <plik>`. Wątki Archiego robisz sam.
   Gdy wątek startuje, jego zadania idą do „W toku”; po scaleniu do „Zrobione w tej podróży”, a kryteria z dowodem
   odhaczasz w `plan.md` od razu (hook po scaleniu przypomina).
6. Odśwież dziennik.

## Koniec (`podroz koniec`)
Tylko po zgodzie szefa (okienko). Gdy kryteria są spełnione, Archi proponuje zamknięcie i czeka.
1. Każdy wątek scalony albo odłożony (→ `Zadania.md` „Zaplanowane”, z powodem). Każde kryterium z dowodem.
2. Podsumowanie w `plan.md`: co zrobione (numery `Z<n>` z sekcji „Zrobione w tej podróży”, potem ją wyczyść), co odłożone, koszt
   (`python -X utf8 C:/Users/PC/cyberiada/narzedzia/zuzycie.py --projekt . --od <data startu>`).
3. Dokumentacja: README, CLAUDE.md, `Zadania.md`, `Decyzje.md`, `funkcje/` (jeśli są).
4. Skrzynka (`C:/Users/PC/cyberiada/skrzynka.md`): w trybie nadzorowanym zaproponuj szefowi okienkiem, co przenieść
   do preferencji; przeniesione linie usuń. W śnie i szkole czeka do `/komp`.
5. Sprzątanie: sesje wyko (`claude agents --json`, `claude stop`, `claude rm`), `git worktree list` i scalone
   gałęzie, `_robocze/`.
6. `Stan.md`: „Brak podróży w toku”. Commit, push, dziennik.
7. Szefowi w czacie tabela: zrobione (`Z<n>`) · następnie · reszta do zrobienia (z `Zadania.md`).
8. Daj szefowi gotowe polecenie: `/compact Zakończona podróż NN-temat. Zachowaj: …` (stan, otwarte pytania).

## Porzucenie (`podroz porzuc`)
1. W trybie komp potwierdź okienkiem (z powodem). Zatrzymaj sesje wyko; gałęzie zostają.
2. `plan.md`: „Porzucona RRRR-MM-DD: powód”, niedokończone wątki → `Zadania.md` (z numerem `Z<n>` i nazwą gałęzi).
3. `Stan.md`: „Brak podróży w toku”. Commit, dziennik.
