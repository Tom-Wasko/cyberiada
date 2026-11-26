# Tryby pracy Archiego: komp / sen / szkoła
Decyzja szefa 26.11 (`Decyzje.md` w cyberiadzie). Tryb jest zapisany w `Stan.md` w linii `Tryb:`, na przykład `Tryb: komp od 16:10`,
`Tryb: sen od 23:10` albo `Tryb: szkoła do 16:00 (znikam)`. Dawne tempa są opisane w `dokumentacja/wiedza/archiwum-tempa.md` (tylko jako tło).

## Polecenia szefa
| Polecenie | Co mówi szef | Skill |
|---|---|---|
| `/komp` | siedzę przy komputerze | `skille/komp` |
| `/sen` | idę spać | `skille/sen` |
| `/szkola 16:00` | wychodzę, wracam o 16:00 | `skille/szkola` |
| `/hej` | w szkole: jestem / znikam (przełącza) | `skille/hej` |

## Zasady
| | komp (nadzorowany) | sen | szkoła |
|---|---|---|---|
| Cel | szybko, bo szef ma mało czasu | cały limit 5 h zużyty w 5 h, bez przestojów | praca rozłożona do końca ramy |
| Hamulec | brak | tygodniowy | tygodniowy |
| Pytania | okienkiem od razu; plan mode przy planowaniu | brak; bierzesz zadania bez decyzji szefa | „znikam”: do „Czeka na szefa” + push, praca idzie dalej; „jestem”: okienkiem |
| wyko | Sonnet medium, high przy `Rodzaj: trudny`; zadanie wolno dzielić na kilku | Sonnet low przy `Rodzaj: mechaniczny`, inaczej medium; autocompact 120k; duże wątki | jak w śnie |
| Ile wyko | ile trzeba | według `tryb.py`, najwyżej 3 | według `tryb.py`, najwyżej 3 |
| Scalanie | `main` + push | gałąź `podroz-NN`, bez push | jak w śnie |

- **Archi zawsze na Opusie.** Nie podpowiadaj `opusplan`: poza plan mode to byłby Sonnet (uwaga szefa 26.11).
- **Rada o tempie:** `python -X utf8 C:/Users/PC/cyberiada/narzedzia/tryb.py`. Narzędzie porównuje limit 5 h z linią idealną (w szkole liczoną do końca ramy) i tydzień z równym rozłożeniem. Pole `wyko` mówi, ile wyko dodać lub odjąć (+1, 0, −1); rada tygodnia wygrywa. Sprawdzasz ją przy starcie trybu, po każdym scaleniu i przy tyknięciu pętli.
- **Start wyko:** `wyko.py <wątek>` czyta tryb z `Stan.md` (albo `--tryb`). W briefie wpisz `Rodzaj: mechaniczny` albo `Rodzaj: trudny`.
- **Ciągłość (wszystkie tryby, uwagi szefa 26.11).** Po scaleniu albo zatrzymaniu wyko w tej samej turze bierzesz następne zadanie: najpierw z „Następnie”, potem z „Zaplanowane”. Piszesz wątek i uruchamiasz wyko, a gdy zadanie jest małe, robisz je sam. Nie czekasz na pytanie szefa. Hook po scaleniu podaje numer następnego zadania. Zadanie, które czeka na decyzję szefa, pomijasz i bierzesz kolejne.

## Sen i szkoła: praca bez szefa
- **Bez okienka i bez plan mode** w stanie „znikam” i w śnie, bo blokują turę. Pytanie „co i po co” zapisujesz w „Czeka na szefa”
  (opcje + rekomendacja), wysyłasz powiadomienie push i odświeżasz dziennik. Ta część czeka, reszta idzie dalej.
- **Nic nieodwracalnego ani widocznego na zewnątrz:** bez scalania do `main`, bez push, bez nowych repo, bez usuwania
  gałęzi i plików spoza `_robocze/`, bez wiadomości do innych ludzi.
- **Oszczędnie:** mało tur (nie odpisuj na rzeczy bez działania), krótkie odpowiedzi, czytanie fragmentów, łączenie wywołań.
  Pracuj seriami: tura po przerwie dłuższej niż 5 min kosztuje kilka razy więcej, bo cache trzeba zapisać od nowa.
  Kontynuacja to SendMessage do tego samego wyko. Brief ma mieć gotowe ścieżki, żeby start był krótszy.
- **Nigdy nie czekasz bezczynnie:** gdy wyko pracują, robisz małe zadania z listy albo przygotowujesz następny wątek.
  Tempo regulujesz oszczędnością (effort, liczba wyko), nie przerwami. Gdy limit 5 h się skończy, czekasz na reset.
  Pętla kontroli Cię wtedy obudzi.
- **Pętla kontroli:** skill `loop` z argumentem `45m kontrola trybu: tryb.py, wyko, ciągłość, pytania`. Przy tyknięciu bez zmian
  odpowiadasz jednym zdaniem, bez czytania plików.
- **Komputer** (sprawdzasz przy starcie snu i szkoły i ostrzegasz szefa jednym zdaniem, jeśli trzeba):
  - uśpienie: `powercfg /query SCHEME_CURRENT SUB_SLEEP STANDBYIDLE` (wartość AC różna od 0 oznacza, że komputer zaśnie);
  - czekający restart: istnieje klucz
    `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired`.
- **Szkoła po końcu ramy:** podsumowanie w `Stan.md`, w czacie i jako push. Potem praca dalej jak w śnie, aż szef wpisze `/komp`.
