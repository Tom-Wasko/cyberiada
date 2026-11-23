---
name: papa
description: Szef wychodzi – tryb autonomiczny: Archi pracuje sam w ramach budżetu (czas, godzina, tokeny albo zakres), bez okienek i bez rzeczy nieodwracalnych.
argument-hint: "4h | do 18:00 | 2M | do skończenia <czego>"
disable-model-invocation: true
---
Polecenie: `/papa $ARGUMENTS`. Tryb autonomiczny: szefa nie ma, odpowiada z telefonu przez czat Remote Control.

## Zanim szef wyjdzie (jest jeszcze chwilę)
1. Budżet z argumentu: `4h` (czas), `do 18:00` (godzina), `2M` (tokeny wszystkich sesji projektu z
   `narzedzia/zuzycie.py`), `do skończenia X` (zakres). Brak budżetu → jedno pytanie okienkiem teraz.
2. Sprawdź komputer i ostrzeż szefa jednym zdaniem, jeśli trzeba:
   - uśpienie na zasilaniu: `powercfg /query SCHEME_CURRENT SUB_SLEEP STANDBYIDLE` (AC różne od 0 → komputer zaśnie);
   - czekający restart po aktualizacji: klucz rejestru
     `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired` istnieje.
3. Zapisz w `Stan.md`: „Tryb: autonomiczny od GG:MM, budżet …, koniec najpóźniej GG:MM”. Gałąź `podroz-NN` z `main`,
   jeśli jej nie ma (wszystkie scalenia w tym trybie idą tam). Odśwież dziennik. Napisz szefowi: „Możesz iść.”

## Praca
- Nowe kroki zaczynasz tylko do 85% budżetu; reszta na dokończenie i podsumowanie.
- Najwyżej 3 wyko naraz (decyzja szefa 23.11). Scalasz do `podroz-NN` tylko wątki bez spraw do potwierdzenia.
- **Bez okienka pytań i bez plan mode** (blokują turę do powrotu szefa). Pytanie „co i po co”: tekstem w czacie
  (opcje + rekomendacja), wpis w „Czeka na szefa”, powiadomienie push (PushNotification), dziennik. Ta część
  czeka, reszta idzie dalej. Odpowiedź szefa z telefonu przyjdzie zwykłą wiadomością.
- **Nic nieodwracalnego ani widocznego na zewnątrz:** bez scalania do `main`, bez push, bez nowych repo, bez
  usuwania gałęzi i plików spoza `_robocze/`, bez wiadomości do innych ludzi.
- Pętla kontroli: uruchom skill `loop` z argumentem `45m kontrola trybu autonomicznego: budżet, wyko, pytania` (co 30–60 min).
  Przy tyknięciu bez zmian odpowiedz jednym zdaniem, bez czytania plików.

## Koniec (praca skończona, wszystko zablokowane albo budżet minął)
1. Wyko kończą krok i commitują; zatrzymaj ich sesje (`claude stop`).
2. Podsumowanie (co zrobione, gdzie, co czeka na szefa, zużycie) w `Stan.md`, w czacie i jako push.
3. Usuń pętlę (CronList → CronDelete). Odśwież dziennik. Dalej czekasz bez pracy aż do `/hejo`.
