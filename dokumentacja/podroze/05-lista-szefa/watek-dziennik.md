# Wątek: dziennik (podróż 05)

## Brief
- **Cel:** wdrożyć w generatorze i na stronie dziennika poprawki szefa z 23.11 (Z7):
  - zadania z kolumną „Zrobione w tej podróży”;
  - stany wątków bez „?”;
  - oś czasu pracowników zamiast wykresu „Wątki”;
  - pasek przycisków po lewej i panele zamiast rozwijanych kart projektów.

  Szef ogląda stronę na telefonie i na komputerze. Ma być czytelna i „po prostu działać”.
- **Ustalone (nie sprawdzaj ponownie):**
  - **Generator** to `narzedzia/dziennik/generuj.py`. Składa JSON projektu z:
    - `dokumentacja/` projektu;
    - logów sesji, przez `narzedzia/zuzycie.py`: `wpisy(projekt, katalog)` daje pola sesja, agent, model, czas UTC i tokeny; `folder_projektu(nazwa)` zwraca folder projektu;
    - gita.
  - **Strona** to `narzedzia/dziennik/strona.html`. Czyta bazę `db` przez `onSnapshot`, z kolekcji:
    - `projekty`;
    - `postep`;
    - `pracownicy/lista`, gdzie każdy pracownik ma pola nazwa, rola, projekt, watek („03/paragon”), stan (pracuje / czeka / zakończony), krok, tokeny i model (to plik z `pracownicy.py`);
    - `uklad`.
  - **Testy:** `narzedzia/dziennik/testy/` (unittest, dane w `testy/dane/`). Schemat JSON jest opisany w `dokumentacja/podroze/01-dziennik/watek-generator.md`; dopisz tam zmiany.
  - **Dane do sprawdzenia:**
    - polecenie: `python -X utf8 narzedzia/dziennik/generuj.py --projekt lukrum` (i `--projekt cyberiada`);
    - wynik trafia do `C:/Users/PC/cyberiada/_robocze/dziennik/<nazwa>.json`;
    - lukrum leży w `C:/Users/PC/Pulpit/lukrum`. Tylko czytasz, nic tam nie zmieniasz.
  - **Błąd „?” przy wątkach:**
    - `czytaj_stan` czyta tabelę wątków tylko z sekcji `## Wątki`. W lukrum `Stan.md` ma tę tabelę pod `## Podróż`, z kolumnami `Wątek | Zadania | Stan`. Ma tam ponad 20 wątków, a plan tylko 7.
    - Tabela w planie lukrum nie ma kolumny „Kto”, więc kto i stan wychodzą None, a strona pokazuje „?”.
  - **Zadania:**
    - `czytaj_zadania(..., w_podrozy)` dziś przenosi wszystkie zadania z linii `Zadania:` planu do „W toku”.
    - Szef chce czego innego. „W toku” to tylko zadania, nad którymi ktoś teraz pracuje. „Następnie” to zadania rozplanowane. Nowa sekcja `## Zrobione w tej podróży` w `Zadania.md` zawiera zadania już zrobione w bieżącej podróży.
    - Zadania między sekcjami przesuwa Archi w `Zadania.md`. Generator ma tylko odczytać sekcje, nic sam nie przesuwa.
  - **Paleta:** walidator jest w `node "C:/Users/PC/AppData/Local/Temp/claude/bundled-skills/2.1.330/3bd9fc86e4af6973545a85dc779eb0ad/dataviz/scripts/validate_palette.js" "<hex,...>" --mode light` (i `--mode dark`). Użyj go, jeśli dodajesz kolory.
  - **Podgląd z fałszywą bazą** był w podróży 03: `_robocze/03-strona/podglad.html` (może już nie istnieć). Zrób nowy w `_robocze/05-dziennik/`.
- **Decyzje szefa** (`dokumentacja/Decyzje.md`, 23.11):
  1. **Zadania:**
     - Generator czyta sekcję `## Zrobione w tej podróży` jako klucz `zrobione`.
     - Usuń automatyczne przenoszenie zadań podróży do `w_toku` (parametr `w_podrozy` i to, co go woła).
     - Strona ma kolumnę „Zrobione w tej podróży” obok W toku / Następnie / Zaplanowane.
     - `przenies.py` obsługuje cel `zrobione`. Ta sama zasada dotyczy przeciągania na stronie: brakująca sekcja powstaje we właściwym miejscu, czyli po „Zaplanowane”, a przed „Odłożone”.
  2. **Stany wątków:**
     - Tabelę wątków z `Stan.md` czytaj z każdej sekcji, która ma kolumnę „Wątek” (nagłówki tabel już są czytane po nazwach przez `tabela()`).
     - Wszystkie wątki ze `Stan.md` trafiają na listę, nie tylko te z planu.
     - „Kto”:
       - kolumna „Kto”, jeśli jest;
       - inaczej `wyko`, gdy w logach jest sesja `wyko-<projekt>-NN-<krótka nazwa>`;
       - `Archi` dla wiersza „Archi”.
     - Przy wątku pokazuj stan pracownika z `pracownicy/lista`: pracuje / czeka / zakończony, dopasowany po projekcie i polu watek. Pokazuj też stan ze `Stan.md`.
     - Nigdy samo „?”. Brak danych to „nie wiadomo”.
  3. **Oś czasu pracowników** zamiast wykresu „Wątki” (`watkiRysuj`, `wykresWatki`):
     - Generator dodaje do JSON-a projektu `aktywnosc`, listę `{nazwa, rola, watek, odcinki: [[start, koniec], ...]}`:
       - dla każdej sesji projektu z ostatnich 7 dni;
       - czasy ISO z odpowiedzi w logach;
       - nowy odcinek zaczyna się po przerwie dłuższej niż 30 minut;
       - wpisy agentów (`agent: True`) liczą się do sesji, która ich wywołała;
       - rola: Archi / wyko / pomo, jak w `rola()`;
       - watek: `NN/nazwa` z nazwy sesji wyko.
     - Strona pokazuje domyślnie ostatnie 24 h, aż do „teraz”:
       - Oś da się przesuwać w lewo, do wcześniejszych dni: przeciąganiem myszą, palcem i przyciskami ◀ Dziś ▶. Najdalej o 7 dni.
       - Wiersze to sesje, które pracowały w widocznym okresie, więc przy przesuwaniu podpisy zmieniają się na wcześniejszych pracowników.
       - **Archi jest zawsze w pierwszym wierszu**, także gdy w danym okresie nie pracował. Jego linia ma przerwy tam, gdzie nie było aktywności (komputer wyłączony albo Archi zamknięty).
       - Podpis wiersza wyko to wątek (`03/paragon`). Kolor wiersza zależy od roli (`rolaKolor`).
       - Chwila scalenia wątku (`scalono` z podróży) jest zaznaczona kropką na końcu wiersza.
       - Dymek pokazuje: nazwę i wątek, stan, odcinek od–do i scalenie.
       - Pod wykresem jest tabela danych (wzorem innych wykresów, `tabelka`).
     - Wykres działa przy 390 px i w ciemnym trybie. Dotyk nie może blokować przewijania strony w pionie, czyli przesuwanie działa tylko w poziomie.
  4. **Układ strony:**
     - Szybki pasek (`#skok`) staje się stałą kolumną przycisków po lewej stronie ekranu. Na telefonie (poniżej 720 px) zostaje u góry jako poziomy pasek z przewijaniem.
     - Zamiast rozwijanych kart projektów (`details.karta`) są panele. Przycisk pokazuje jeden panel naraz: Przegląd, Czeka na Ciebie, Pracownicy albo jeden z projektów.
     - Wybrany przycisk jest wyróżniony (kolor projektu). Wybór jest pamiętany w localStorage, wszystko owinięte try/catch. Domyślnie pokazuje się Przegląd.
     - Przy „Czeka” zostaje licznik. Gdy jest coś nowego (już istniejące „nowe” z localStorage), przycisk ma znaczek „nowe”.
     - Kafle przeglądu, które dziś przewijają do karty, przełączają teraz na panel projektu.
- **Pliki do zmiany / utworzenia:**
  - `narzedzia/dziennik/generuj.py`, `narzedzia/dziennik/strona.html`, `narzedzia/dziennik/przenies.py`;
  - `narzedzia/dziennik/testy/test_generuj.py`, `test_przenies.py`, `testy/dane/*`;
  - `dokumentacja/podroze/01-dziennik/watek-generator.md` (schemat).

  **Nie ruszaj:**
  - `narzedzia/zuzycie.py`, `narzedzia/dziennik/hook_commit.py`, `pracownicy.py`, `wyko.py`, `archi.py`;
  - `role/`, `skille/`, `szablony/`;
  - nic w `Pulpit/lukrum`.

  Strony nie publikujesz, robi to Archi.
- **Gotowe, gdy:**
  - `python -X utf8 -m unittest discover -s narzedzia/dziennik/testy` daje `OK`. Nowe testy: sekcja „Zrobione w tej podróży”, tabela wątków pod innym nagłówkiem niż `## Wątki`, brak przenoszenia zadań przez `Zadania:`, odcinki `aktywnosc` z przerwą ponad 30 minut, agent liczony do sesji, `przenies.py ... Z1=zrobione`.
  - JSON lukrum ma wszystkie wątki ze `Stan.md` (ponad 20), każdy z niepustym `stan` i `kto`, oraz `aktywnosc` z wierszem archi-lukrum.
  - `grep -c '"?"' strona.html` nie znajduje „?” użytego jako stan albo kto.
  - Podgląd `_robocze/05-dziennik/podglad.html` z fałszywym `window.claude.use("db")` korzysta z danych z obu JSON-ów i z przykładowych `pracownicy` i `postep`.
- **Zrzuty ekranu:** tak, do `_robocze/05-dziennik/`, poza gitem, na przykład przez `msedge --headless --screenshot`. Potrzebne:
  - komputer 1280 px: Przegląd i panel lukrum z osią czasu;
  - telefon 390 px: panel lukrum;
  - oś przesunięta w lewo o dzień, z innymi podpisami wierszy.

  Jeśli zrzut się nie uda, napisz to w raporcie.
- **Dokumenty do poprawienia:** `watek-generator.md` (schemat: `zrobione`, `aktywnosc`, czytanie wątków ze `Stan.md`).
- **Archi:** archi-cyberiada

## Raport
<!-- Pisze wyko na końcu. -->
