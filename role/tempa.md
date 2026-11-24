# Tempa pracy Archiego (żółw / zwykły / królik)
Czyta Archi przy `/hejo <tempo>`, `/papa <tempo>` i po `/wznow`. Tempo stoi w `Stan.md` w linii `Tempo: …`.
Decyzja szefa 24.11 (`Decyzje.md` w cyberiadzie). Liczby: `dokumentacja/wiedza/tokeny.md` w cyberiadzie.

## Wspólne
- Rada o tempie: `python -X utf8 C:/Users/PC/cyberiada/narzedzia/tempo.py` (procent limitu 5h względem procentu
  czasu okna, prognoza 100%). Sprawdzaj przy starcie trybu, po każdym scaleniu i przy tyknięciu pętli.
- Wyko startuje z tempem projektu: `wyko.py <wątek>` czyta `Tempo:` z `Stan.md` (albo `--tempo`).
  W briefie `Rodzaj: mechaniczny` (proste, powtarzalne zmiany) albo `Rodzaj: trudny` zmienia effort.

## żółw (`/hejo zolw`, `/papa zolw`): najwięcej pracy z limitu
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

## zwykły (`/hejo`, `/papa` bez słowa)
Jak dotąd: wyko Sonnet medium, autocompact 200k; liczba wyko według potrzeby (autonomicznie najwyżej 3).

## królik (`/hejo krolik`, `/papa krolik`): szybko teraz
- Archi na Opusie, jak zwykle. Wyko Sonnet medium (high przy `Rodzaj: trudny`), autocompact 200k.
- Zadanie wolno podzielić na kilku wyko równolegle (pliki rozłączne); autonomicznie najwyżej 3.
- `tempo.py` tylko informuje (prognoza godziny 100%); powiedz szefowi, gdy limit skończy się przed czasem.
