---
name: szkola
description: Szef wychodzi do szkoły do danej godziny – tryb szkoła: tempo do końca ramy, pytania zbierane bez przerywania pracy, /hej przełącza jestem / znikam.
argument-hint: "16:00"
disable-model-invocation: true
---
Polecenie: `/szkola $ARGUMENTS`. Tryb szkoła (opis: `C:/Users/PC/cyberiada/role/tryby.md`, część „Sen i szkoła”).

## Zanim szef wyjdzie (jest jeszcze chwilę)
1. Koniec ramy z argumentu (`16:00`). Bez godziny zadaj jedno okienko teraz.
2. **Plan ramy:** zadania w kolejności (z podróży i `Zadania.md`) dopasowane do czasu do końca ramy. Jedno okienko
   (do 4 pytań), jeśli coś jest niejasne. Plan zapisz w `Stan.md`.
3. Sprawdź komputer (uśpienie, czekający restart) i ostrzeż szefa jednym zdaniem, jeśli trzeba.
4. W `Stan.md` wpisz „Tryb: szkoła do GG:MM (znikam)”. Gałąź `podroz-NN` z `main`, jeśli jej nie ma. Odśwież dziennik.
   Napisz: „Miłego dnia. Gdy będziesz mieć chwilę na telefonie, wpisz /hej.”

## Rama
- Pracujesz według planu i ciągłości. Tempo dobierasz według `tryb.py` (linia idealna do końca ramy, hamulec tygodniowy),
  wyko najwyżej 3. Bez push i bez `main`.
- W stanie „znikam” pytania idą do „Czeka na szefa” + push. Nie przerywają pracy. W stanie „jestem” (`/hej`) zadajesz je okienkiem.
- Uruchom pętlę kontroli (skill `loop`, `45m kontrola trybu: tryb.py, wyko, ciągłość, pytania`).
- Po końcu ramy zrób podsumowanie (co zrobione, gdzie, co czeka, zużycie) w `Stan.md`, w czacie i jako push.
  Potem pracujesz dalej jak w śnie, aż szef wpisze `/komp`.
