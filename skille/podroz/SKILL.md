---
name: podroz
description: Archi zaczyna, kończy albo porzuca podróż (sesję pracy nad projektem) – plan, wątki, scalanie, sprzątanie.
argument-hint: "[temat] | koniec | porzuc"
disable-model-invocation: true
effort: high
---
Polecenie: `/podroz $ARGUMENTS`. Wykonuje Archi w folderze projektu. Szablony: `C:/Users/PC/cyberiada/szablony/`.

## Start (`/podroz` albo `/podroz <temat>`)
1. `dokumentacja/Stan.md`: jeśli podróż jest w toku, powiedz to i zaproponuj `/podroz koniec` albo dalszą pracę.
2. Temat: z argumentu albo od szefa. Bez tematu zaproponuj 2–4 tematy z `Zadania.md` (okienko, rekomendacja).
3. **Tryb hejo:** wejdź w plan mode (EnterPlanMode). Doprecyzuj cel pytaniami (okienko, po 4), ustal sprawdzalne
   kryteria sukcesu i wątki: kto (Archi sam: do ok. 20 poleceń; wyko: obszerny), pliki rozłączne między wątkami.
   Plan do zatwierdzenia przez ExitPlanMode; zatwierdzenie = zgoda szefa na cel i kryteria. Dalej auto mode.
   **Tryb papa:** bez plan mode; zacznij tylko podróż, której cel i kryteria są już w `Zadania.md` albo w ustaleniach;
   inaczej zapisz pytanie w „Czeka na szefa” i czekaj.
4. Utwórz `dokumentacja/podroze/NN-temat/plan.md` z `plan-podrozy.md` (NN = następny numer, dwie cyfry).
   Wpisz podróż i wątki do `Stan.md`. Commit.
5. Dla każdego wątku wyko: `watek-<nazwa>.md` z `watek.md` (pełny brief), commit, potem
   `python -X utf8 C:/Users/PC/cyberiada/narzedzia/wyko.py <plik>`. Wątki Archiego robisz sam.
6. Odśwież dziennik.

## Koniec (`/podroz koniec`)
1. Każdy wątek scalony albo odłożony (→ `Zadania.md` „Zaplanowane”, z powodem). Każde kryterium z dowodem.
2. Podsumowanie w `plan.md`: co zrobione, co odłożone, koszt
   (`python -X utf8 C:/Users/PC/cyberiada/narzedzia/zuzycie.py --projekt . --od <data startu>`).
3. Dokumentacja: README, CLAUDE.md, `Zadania.md`, `Decyzje.md`, `funkcje/` (jeśli są).
4. Skrzynka (`C:/Users/PC/cyberiada/skrzynka.md`): w trybie hejo zaproponuj szefowi okienkiem, co przenieść
   do preferencji; przeniesione linie usuń. W trybie papa czeka do /hejo.
5. Sprzątanie: sesje wyko (`claude agents --json`, `claude stop`, `claude rm`), `git worktree list` i scalone
   gałęzie, `_robocze/`.
6. `Stan.md`: „Brak podróży w toku”. Commit, push, dziennik.
7. Daj szefowi gotowe polecenie: `/compact Zakończona podróż NN-temat. Zachowaj: …` (stan, otwarte pytania).

## Porzucenie (`/podroz porzuc`)
1. W trybie hejo potwierdź okienkiem (z powodem). Zatrzymaj sesje wyko; gałęzie zostają.
2. `plan.md`: „Porzucona RRRR-MM-DD: powód”, niedokończone wątki → `Zadania.md` (z nazwą gałęzi).
3. `Stan.md`: „Brak podróży w toku”. Commit, dziennik.
