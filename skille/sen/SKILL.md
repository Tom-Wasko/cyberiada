---
name: sen
description: Szef idzie spać – tryb sen: krótki plan nocy z szefem, potem Archi pracuje całkiem sam, cały limit 5 h w 5 h, z hamulcem tygodniowym.
disable-model-invocation: true
---
Polecenie: `/sen`. Tryb sen (opis: `C:/Users/PC/cyberiada/role/tryby.md`, część „Sen i szkoła”).

## Zanim szef zaśnie (jest jeszcze chwilę)
1. **Plan nocy:** lista zadań w kolejności, z bieżącej podróży i `Zadania.md`. Po niej bierzesz zadania, które nie
   wymagają decyzji szefa. Gdy coś jest niejasne, zadaj jedno okienko (do 4 pytań, rekomendacja pierwsza).
   Plan zapisz w `Stan.md` („Plan nocy: Z…, Z…”).
2. Sprawdź komputer (uśpienie, czekający restart) i ostrzeż szefa jednym zdaniem, jeśli trzeba.
3. W `Stan.md` wpisz „Tryb: sen od GG:MM”. Gałąź `podroz-NN` z `main`, jeśli jej nie ma (wszystkie scalenia idą tam).
   Odśwież dziennik. Napisz: „Dobranoc.”

## Noc
- Pracujesz według planu nocy i ciągłości: wyko według `tryb.py` (najwyżej 3), bez okienek, bez plan mode,
  bez push i bez `main`.
- Uruchom pętlę kontroli (skill `loop`, `45m kontrola trybu: tryb.py, wyko, ciągłość, pytania`).
- Gdy limit 5 h się skończy, czekasz na reset. Gdy hamulec tygodniowy każe zwolnić, zwalniasz oszczędnością.
- Gdy zadania się skończą albo wszystko jest zablokowane: wyko kończą krok i commitują. Podsumowanie (co zrobione,
  gdzie, co czeka na szefa, zużycie) zapisz w `Stan.md` i wyślij jako push. Usuń pętlę i odśwież dziennik.
- Rano szef wpisze `/komp` albo `/szkola`: podsumowanie dla szefa robi tamto polecenie.
