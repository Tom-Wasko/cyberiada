---
name: hejo
description: Szef jest przy komputerze – Archi przechodzi w tryb nadzorowany, zdaje sprawę z pracy pod nieobecność i zadaje czekające pytania.
argument-hint: "[zolw | krolik]"
disable-model-invocation: true
---
Polecenie: `/hejo $ARGUMENTS`. Tryb nadzorowany: szef jest i odpowiada od razu.
Słowo `zolw` albo `krolik` ustawia tempo (bez słowa: zwykły); opis temp: `C:/Users/PC/cyberiada/role/tempa.md`.

1. Zapisz w `dokumentacja/Stan.md`: „Tryb: nadzorowany od GG:MM” i „Tempo: żółw|zwykły|królik”. Przy innym tempie niż
   zwykłe przeczytaj opis temp i zrób jego kroki startowe (`tempo.py`, polecenia dla szefa).
2. Zatrzymaj pętlę kontroli trybu autonomicznego, jeśli działa (CronList → CronDelete).
3. Jeśli przed chwilą był tryb autonomiczny: w 5–10 liniach podsumuj, co zrobione (wątki, commity, gałąź `podroz-NN`),
   co zablokowane i ile zużyto (`narzedzia/zuzycie.py`). Pytania z „Czeka na szefa” zadaj okienkiem (po 4,
   rekomendacja pierwsza); odpowiedzi do `Decyzje.md`.
4. Po przejrzeniu przez szefa zapytaj, czy scalić `podroz-NN` do `main`. Po zgodzie scal, przetestuj, wypchnij.
5. Spostrzeżenia ze skrzynki, które czekały: zaproponuj okienkiem przeniesienie do preferencji.
6. Dalej: podróż w toku → następny krok (planowanie w plan mode); brak podróży → zaproponuj `/podroz`.
7. Odśwież dziennik.
