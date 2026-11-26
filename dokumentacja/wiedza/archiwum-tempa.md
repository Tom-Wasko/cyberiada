# Archiwum: tempa i dawne polecenia (do 26.11)
Kontekst historyczny. Zastąpione 26.11 trybami komp / sen / szkoła (`role/tryby.md`, decyzja szefa w `dokumentacja/Decyzje.md`).
Nie obowiązuje.

---

## Plik `role/tempa.md`

### Tempa pracy Archiego (żółw / zwykły / królik)
Czyta Archi przy `/hejo <tempo>`, `/papa <tempo>` i po `/wznow`. Tempo stoi w `Stan.md` w linii `Tempo: …`.
Decyzja szefa 24.11 (`Decyzje.md` w cyberiadzie). Liczby: `dokumentacja/wiedza/tokeny.md` w cyberiadzie.

#### Wspólne
- Rada o tempie: `python -X utf8 C:/Users/PC/cyberiada/narzedzia/tempo.py` (procent limitu 5h względem procentu
  czasu okna, prognoza 100%). Sprawdzaj przy starcie trybu, po każdym scaleniu i przy tyknięciu pętli.
- Wyko startuje z tempem projektu: `wyko.py <wątek>` czyta `Tempo:` z `Stan.md` (albo `--tempo`).
  W briefie `Rodzaj: mechaniczny` (proste, powtarzalne zmiany) albo `Rodzaj: trudny` zmienia effort.

#### żółw (`/hejo zolw`, `/papa zolw`): najwięcej pracy z limitu
Ideał: praca bez przerwy przez całe okno 5 h i 100% limitu przy jego końcu. **Nigdy nie czekasz i się nie obijasz**;
tempo regulujesz oszczędnością, nie przerwami.
- Na starcie daj szefowi do wpisania: `/model opusplan` i `/autocompact 150k` (Archi sam ich nie zmieni).
- Mało tur: nie odpisuj na rzeczy bez działania, krótkie odpowiedzi, czytaj fragmenty, łącz wywołania.
- Po scaleniu wątku poproś szefa o `/compact` (w trybie autonomicznym działa samo przy 150k).
- Wyko: Sonnet, effort medium (low przy `Rodzaj: mechaniczny`), autocompact 120k; wątki duże (2 h i więcej),
  bo start to ok. 1/5 kosztu wyko; brief z gotowymi ścieżkami i faktami skraca start. Kontynuacja = SendMessage do
  tego samego wyko. Drobne mechaniczne rzeczy i szukanie: agent na Haiku (ok. 1/17 tury Sonneta) albo sam.
- Pracuj seriami: tura po przerwie > 5 min kosztuje kilka razy więcej (ponowny zapis cache).
- `tempo.py` mówi „za szybko” → następne wątki oszczędniej (low, bez kolejnego wyko równolegle);
  „za wolno” → dodaj wyko (autonomicznie najwyżej 3) albo bierz kolejne zadania z listy.
- Gdy wyko pracują, rób małe zadania z `Zadania.md`; gdy pracy brak, przygotuj następny wątek.

#### zwykły (`/hejo`, `/papa` bez słowa)
Jak dotąd: wyko Sonnet medium, autocompact 200k; liczba wyko według potrzeby (autonomicznie najwyżej 3).

#### królik (`/hejo krolik`, `/papa krolik`): szybko teraz
- Archi na Opusie, jak zwykle. Wyko Sonnet medium (high przy `Rodzaj: trudny`), autocompact 200k.
- Zadanie wolno podzielić na kilku wyko równolegle (pliki rozłączne); autonomicznie najwyżej 3.
- `tempo.py` tylko informuje (prognoza godziny 100%); powiedz szefowi, gdy limit skończy się przed czasem.

---

## Plik `skille/hejo/SKILL.md`

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

---

## Plik `skille/papa/SKILL.md`

---
name: papa
description: Szef wychodzi – tryb autonomiczny: Archi pracuje sam w ramach budżetu (czas, godzina, tokeny albo zakres), bez okienek i bez rzeczy nieodwracalnych.
argument-hint: "[zolw | krolik] 4h | do 18:00 | 2M | do skończenia <czego>"
disable-model-invocation: true
---
Polecenie: `/papa $ARGUMENTS`. Tryb autonomiczny: szefa nie ma, odpowiada z telefonu przez czat Remote Control.
Słowo `zolw` albo `krolik` ustawia tempo (bez słowa: zwykły); opis temp: `C:/Users/PC/cyberiada/role/tempa.md`.
Żółw: budżet domyślnie „do końca okna 5h” (pracuje bez przerw, nie czeka).

#### Zanim szef wyjdzie (jest jeszcze chwilę)
1. Budżet z argumentu: `4h` (czas), `do 18:00` (godzina), `2M` (tokeny wszystkich sesji projektu z
   `narzedzia/zuzycie.py`), `do skończenia X` (zakres). Brak budżetu → jedno pytanie okienkiem teraz.
2. Sprawdź komputer i ostrzeż szefa jednym zdaniem, jeśli trzeba:
   - uśpienie na zasilaniu: `powercfg /query SCHEME_CURRENT SUB_SLEEP STANDBYIDLE` (AC różne od 0 → komputer zaśnie);
   - czekający restart po aktualizacji: klucz rejestru
     `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired` istnieje.
3. Zapisz w `Stan.md`: „Tryb: autonomiczny od GG:MM, budżet …, koniec najpóźniej GG:MM” i „Tempo: …”. Przy żółwiu
   daj szefowi do wpisania przed wyjściem `/model opusplan` i `/autocompact 150k`. Gałąź `podroz-NN` z `main`,
   jeśli jej nie ma (wszystkie scalenia w tym trybie idą tam). Odśwież dziennik. Napisz szefowi: „Możesz iść.”

#### Praca
- Nowe kroki zaczynasz tylko do 85% budżetu; reszta na dokończenie i podsumowanie.
- Najwyżej 3 wyko naraz (decyzja szefa 23.11; żółw: tyle, ile każe `tempo.py`). Scalasz do `podroz-NN` tylko wątki bez spraw do potwierdzenia.
- **Bez okienka pytań i bez plan mode** (blokują turę do powrotu szefa). Pytanie „co i po co”: tekstem w czacie
  (opcje + rekomendacja), wpis w „Czeka na szefa”, powiadomienie push (PushNotification), dziennik. Ta część
  czeka, reszta idzie dalej. Odpowiedź szefa z telefonu przyjdzie zwykłą wiadomością.
- **Nic nieodwracalnego ani widocznego na zewnątrz:** bez scalania do `main`, bez push, bez nowych repo, bez
  usuwania gałęzi i plików spoza `_robocze/`, bez wiadomości do innych ludzi.
- Pętla kontroli: uruchom skill `loop` z argumentem `45m kontrola trybu autonomicznego: budżet, wyko, pytania` (co 30–60 min).
  Przy tyknięciu bez zmian odpowiedz jednym zdaniem, bez czytania plików.

#### Koniec (praca skończona, wszystko zablokowane albo budżet minął)
1. Wyko kończą krok i commitują; zatrzymaj ich sesje (`claude stop`).
2. Podsumowanie (co zrobione, gdzie, co czeka na szefa, zużycie) w `Stan.md`, w czacie i jako push.
3. Usuń pętlę (CronList → CronDelete). Odśwież dziennik. Dalej czekasz bez pracy aż do `/hejo`.

---

## Plik `skille/wznow/SKILL.md`

---
name: wznow
description: Archi wznawia pracę po restarcie komputera albo po wyczerpaniu limitu – odtwarza stan z plików i wznawia przerwane sesje wyko.
disable-model-invocation: true
---
Polecenie: `/wznow`. Stan jest w plikach i commitach, nie w pamięci sesji.

1. Przeczytaj `dokumentacja/Stan.md` (podróż, wątki, tryb, tempo, budżet); tempo inne niż zwykłe → `C:/Users/PC/cyberiada/role/tempa.md`.
2. `claude agents --json --all`: które sesje wyko żyją, które są zatrzymane.
3. Dla każdego wątku w toku: ostatnie commity gałęzi i raport w pliku wątku.
   - Raport gotowy → przegląd i scalenie jak zwykle.
   - Sesja zatrzymana bez raportu → `python -X utf8 C:/Users/PC/cyberiada/narzedzia/wyko.py --wznow <id albo nazwa>`
     (wznawia tę samą sesję w tle, z jej kontekstem).
4. Tryb autonomiczny: przelicz pozostały budżet; jeśli zostało, uruchom znów pętlę kontroli, inaczej koniec trybu autonomicznego.
5. Puls i wpis w `Stan.md` („Wznowione GG:MM po …”), dziennik. Szefowi 3–5 linii: co było przerwane, co wznowione.
