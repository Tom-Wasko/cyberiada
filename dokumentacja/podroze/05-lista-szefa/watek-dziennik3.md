# Wątek: dziennik3 (podróż 05, kontynuacja 05/dziennik2)

## Brief
- **Cel:** na osi czasu pracowników nie ma dużych pustych dziur, a na start oś pokazuje bieżącą podróż, w całości.
- **Ustalone (nie sprawdzaj ponownie):**
  - Pliki: `narzedzia/dziennik/strona.html`, `generuj.py`, testy w `narzedzia/dziennik/testy/`.
  - Stan obecny (scalone 26be214):
    - okno 6 h przesuwane myszą i palcem;
    - rzędy „naraz” pakowane w JS (`ukladRzedow`);
    - podpis rzędu to sesja przy lewej krawędzi okna;
    - Archi jest w pierwszym rzędzie.
  - JSON projektu ma `podroz` (bez podróży w toku `null`; tak jest teraz w lukrum) i `aktywnosc` z ostatnich 7 dni.
  - Podgląd i zrzuty: zrób jak w 05/dziennik2 (fałszywe `claude.use("db")` z `_robocze/dziennik/*.json`; telefon emulacją CDP 390 px), w `_robocze/05-dziennik3/`.
- **Decyzje szefa (23.11):**
  1. **Dziury zwężone:**
     - Przerwę dłuższą niż 1 h, w której nikt (żaden rząd) nie pracował, pokazuj jako stałą wąską kolumnę, np. 24–32 px, z ukośnym kreskowaniem i podpisem w rodzaju „przerwa 9 h”. Dla nocy możesz dopisać „noc”.
     - Godziny po obu stronach przerwy zostają prawdziwe. Podziałka godzinowa nie przechodzi przez przerwę.
     - Przy zmianie dnia za przerwą pokaż datę.
     - Dymek nad przerwą: od–do.
  2. **Zakres na start: bieżąca podróż, cała na ekranie.**
     - Oś obejmuje czas od startu bieżącej podróży do teraz i mieści się w szerokości bez przesuwania; wtedy przeciąganie jest wyłączone.
     - Jeśli po zwężeniu przerw nadal jest bardzo gęsto (mniej niż ok. 40 px na godzinę), włącz przesuwanie myszą i palcem, z oknem dopasowanym do tej gęstości.
     - Przełącznik „Ta podróż / Wszystko (7 dni)”: „Wszystko” pokazuje pełny zakres z tymi samymi zwężonymi przerwami i przesuwaniem.
     - Bez podróży w toku: ostatnia zakończona podróż projektu. Generator musi ją podać, np. `ostatnia_podroz: {nazwa, od, do}` z folderów `dokumentacja/podroze/` i `plan.md` (data startu w nagłówku, data końca z podsumowania albo z ostatniego commita w folderze).
     - Napis nad osią: „Podróż 03 (zakończona)” albo „Podróż 05: od 23.11”.
     - Jeśli nie ma żadnej podróży, domyślnie „Wszystko”.
  3. **Kto należy do podróży: po czasie.** Każda praca od startu podróży (dla zakończonej: do jej końca) należy do podróży: Archi, pomo i wyko.
  4. Rzędy w widoku podróży liczone tylko z sesji w tym zakresie, więc może ich być mniej. Podpis przy lewej krawędzi i reszta zasad z 05/dziennik2 zostają.
- **Pliki do zmiany:** `strona.html`, `generuj.py` (`ostatnia_podroz`, zwykłe czytanie dat startu i końca), testy; schemat w `dokumentacja/podroze/01-dziennik/watek-generator.md`.

  **Nie ruszaj:**
  - `zuzycie.py`, `hook_commit.py`, `pracownicy.py`;
  - `role/`, `skille/`, `szablony/`;
  - inne pliki dokumentacji.

  Strony nie publikujesz.
- **Gotowe, gdy:**
  - `python -X utf8 -m unittest discover -s narzedzia/dziennik/testy` daje OK, w tym nowy test `ostatnia_podroz` na danych testowych;
  - JSON lukrum ma `ostatnia_podroz` z podróżą 03 i jej datami;
  - zrzuty pokazują, że oś mieści podróż na ekranie bez pustych dziur;
  - telefon: `scrollWidth <= 390`.
- **Zrzuty ekranu:** do `_robocze/05-dziennik3/`:
  - komputer: lukrum „Ta podróż”;
  - komputer: lukrum „Wszystko”;
  - cyberiada „Ta podróż”;
  - telefon 390 px.
- **Archi:** archi-cyberiada

## Raport
<!-- Pisze wyko na końcu. -->
