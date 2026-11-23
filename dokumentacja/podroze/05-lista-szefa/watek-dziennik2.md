# Wątek: dziennik2 (podróż 05, kontynuacja 05/dziennik)

## Brief
- **Cel:** poprawić układ strony dziennika i oś czasu pracowników według uwag szefa po obejrzeniu wersji z wątku 05/dziennik (scalonej do `main`, commit ee0fe12).
- **Ustalone (nie sprawdzaj ponownie):**
  - Pliki: strona `narzedzia/dziennik/strona.html`, generator `narzedzia/dziennik/generuj.py`, testy w `narzedzia/dziennik/testy/`.
  - Generator daje `aktywnosc`, czyli listę `{nazwa, rola, watek, odcinki: [[start, koniec], ...]}`. Przerwa ponad 30 minut zaczyna nowy odcinek. Archi jest pierwszy.
  - Podgląd i zrzuty z wątku 05/dziennik leżały w worktree, który jest już usunięty. Zrób nowe w `_robocze/05-dziennik2/`, z fałszywym `window.claude.use("db")` z danymi z `_robocze/dziennik/{cyberiada,lukrum}.json`.
  - Telefon sprawdzaj emulacją CDP przy 390 px, bo headless Edge ma najmniej około 481 px. Warunek: `document.documentElement.scrollWidth <= 390`.
  - Lukrum ma teraz zamkniętą podróż, więc ma 0 wątków. `aktywnosc` z ostatnich 7 dni zostaje i wystarcza do testu osi.
- **Decyzje szefa (23.11, po obejrzeniu):**
  1. **Układ:**
     - Boczny pasek przycisków po lewej zostaje.
     - **Wszystko da się zobaczyć, przewijając w dół**, w tej samej kolejności co przed podróżą 05: Czeka na Ciebie → Pracownicy → Przegląd → Projekty. Przyciski w pasku przewijają do sekcji, a nie przełączają paneli.
     - W sekcji Projekty nazwy projektów są **klockami obok siebie** (w kolorze projektu). Kliknięcie klocka otwiera **pod klockami** panel tego projektu. Naraz otwarty jest jeden projekt, domyślnie pierwszy albo ostatnio wybrany (localStorage w try/catch). Przycisk projektu w pasku bocznym przewija do Projektów i otwiera ten projekt.
     - Na telefonie pasek jest u góry, jak teraz, i bez poziomego przewijania strony.
  2. **Oś czasu pracowników:**
     - **Okno ma 6 h** (podziałka godzinowa), na start kończy się na „teraz”.
     - **Bez strzałek** ◀ Dziś ▶. Oś przesuwa się myszą (przeciąganie) i palcem, płynnie, najdalej o 7 dni wstecz. Dotyk nie blokuje przewijania strony w pionie.
     - **Rzędów jest tyle, ilu pracowników działało naraz**, a nie jeden na sesję:
       - Archi ma zawsze pierwszy rząd, tylko dla siebie.
       - Wyko i pomo są pakowane w rzędy: kolejna sesja trafia do najniższego rzędu, który jest wolny w jej czasie (od pierwszego do ostatniego odcinka sesji, z małym zapasem). W jednym rzędzie może więc być kilku wyko po kolei.
       - Liczba rzędów to maksimum pracujących naraz w całym zakresie danych. Układ jest stały i nie zmienia się przy przesuwaniu.
     - **Podpis po lewej** to nazwa (wątek, np. `03/paragon`) sesji, która w tym rzędzie pracowała **najbliżej lewej krawędzi widocznego okna**:
       - sesja obejmująca lewą krawędź;
       - jeśli takiej nie ma, pierwsza na prawo od krawędzi;
       - jeśli w oknie nic nie ma, ostatnia przed krawędzią, wyszarzona.
       Podpis zmienia się na bieżąco przy przesuwaniu; przy przewijaniu do starszych pokazuje tego, kto był tam wcześniej.
     - Kolor paska zależy od roli. Kropka scalenia zostaje. Dymek i tabela pod wykresem zostają.
- **Pliki do zmiany:** `narzedzia/dziennik/strona.html`; `generuj.py` i testy tylko wtedy, gdy pakowanie w rzędy liczysz w generatorze.

  **Nie ruszaj:**
  - `zuzycie.py`, `hook_commit.py`, `pracownicy.py`;
  - `role/`, `skille/`, `szablony/`;
  - nic poza `narzedzia/dziennik/` i `_robocze/`.

  Strony nie publikujesz.
- **Gotowe, gdy:**
  - `python -X utf8 -m unittest discover -s narzedzia/dziennik/testy` daje OK. Jeśli pakowanie jest w generatorze, dodaj test: 3 nakładające się sesje dają 2 rzędy wyko.
  - Przy danych lukrum oś ma najwyżej tylu wyko w rzędach, ilu pracowało naraz. Podaj tę liczbę w raporcie.
  - Telefon: `scrollWidth <= 390`.
- **Zrzuty ekranu:** do `_robocze/05-dziennik2/`:
  - komputer 1280 px: cała strona przewinięta w dół, klocki projektów, otwarty lukrum;
  - oś teraz i oś przesunięta o kilka godzin wstecz, z innymi podpisami;
  - telefon 390 px.
- **Dokumenty do poprawienia:** `watek-generator.md`, tylko jeśli zmienia się schemat.
- **Archi:** archi-cyberiada

## Raport
<!-- Pisze wyko na końcu. -->
**Zrobione (wyko, 23.11):** wszystko w `narzedzia/dziennik/strona.html`; generator i testy bez zmian, bo pakowanie w rzędy liczę w JS (`ukladRzedow`), schemat `aktywnosc` się nie zmienił (`watek-generator.md` bez poprawek).
- **Układ:** wszystkie sekcje pod sobą: Czeka → Pracownicy → Przegląd → Projekty. Pasek (u góry na telefonie) przewija do sekcji i podświetla bieżącą. W Projektach klocki w kolorze projektu, pod nimi panel jednego projektu (domyślnie pierwszy albo ostatnio wybrany, localStorage `dziennik.projekt` w try/catch). Przycisk projektu w pasku przewija i otwiera projekt. „Czeka” liczy się jako obejrzane, gdy sekcja jest widoczna (IntersectionObserver).
- **Oś:** okno 6 h, bez strzałek, przeciąganie myszą i palcem do 7 dni wstecz (`touch-action:pan-y`). Rząd 1 = Archi; wyko i pomo pakowane zachłannie (rozpiętość sesji ± 3 min). Podpis rzędu według zasady lewej krawędzi (obejmująca → pierwsza na prawo → ostatnia przed, szara).
- Przy okazji: z sekcji Pracownicy znikło wypisywane „null” (stara usterka `replaceChildren(null)`).
- **Dowód:**
  - `python -X utf8 -m unittest discover -s narzedzia/dziennik/testy` → `Ran 39 tests ... OK`.
  - Lukrum: 6 rzędów wyko; liczone osobno z danych, najwięcej wyko naraz = 6.
  - Telefon (emulacja urządzenia, 390 px, Edge): `scrollWidth` = 390 (przy starcie, po przejściu do lukrum, na końcu). Błędów JS brak.
  - Podpisy zmieniają się przy przesunięciu: teraz `03/zestawy, 03/przewodnik…`, −5 h `03/ukryte, 03/kartki…`, −1 dzień `02/sklepy, 02/mapa, 02/drobne…`.
- **Test jednostkowy „3 sesje → 2 rzędy”:** nie dodany, bo pakowanie jest w JS (brief wymagał go tylko dla generatora). Sprawdziłem tylko na danych lukrum, bez testu automatycznego.
- **Zrzuty:** `_robocze/05-dziennik2/`: `komputer-cala.png`, `komputer-lukrum-cala.png`, `os-teraz.png`, `os-wstecz.png`, `os-daleko.png`, `telefon-gora.png`, `telefon-projekty.png`, `telefon-os.png`, `telefon-cala.png`. Skrypt: `zrzuty.py`, podgląd z fałszywą bazą: `podglad.html`.
- **Propozycje:** inercja po puszczeniu osi; przycisk „wróć do teraz”, gdy oś jest przesunięta (szef kazał bez strzałek, więc nie dodawałem).
