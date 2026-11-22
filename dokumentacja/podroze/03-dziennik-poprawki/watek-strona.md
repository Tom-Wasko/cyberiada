# Wątek: strona (podróż 03)

## Brief
- **Cel:** poprawić generator danych dziennika i stronę dziennika według listy szefa z 22.11 (Z4).
  Szef ogląda stronę na telefonie i komputerze: ma być czytelna, kolorowa, „po prostu działa”.
- **Ustalone (nie sprawdzaj ponownie):**
  - Generator `narzedzia/dziennik/generuj.py` składa JSON projektu z `dokumentacja/` projektu, logów sesji
    (`narzedzia/zuzycie.py`, funkcja `wpisy`, każdy wpis ma pole `model`) i gita. Strona `narzedzia/dziennik/strona.html`
    czyta bazę `db` (kolekcja `projekty`, `onSnapshot`, więc zmiany w bazie widać od razu). Testy:
    `narzedzia/dziennik/testy/test_generuj.py` (unittest, dane w `testy/dane/`). Schemat JSON:
    `dokumentacja/podroze/01-dziennik/watek-generator.md`; zmiany schematu dopisz tam.
  - Prawdziwe dane do sprawdzenia: `python -X utf8 narzedzia/dziennik/generuj.py --projekt lukrum` (i `cyberiada`),
    wynik w `C:/Users/PC/cyberiada/_robocze/dziennik/<nazwa>.json`. Projekt lukrum: `C:/Users/PC/Pulpit/lukrum`
    (tylko czytasz, nic tam nie zmieniasz).
  - Błąd wykresu „Wątki”: `czytaj_plan` i `czytaj_stan` biorą kolumny tabel po numerze. Plan lukrum
    (`Pulpit/lukrum/dokumentacja/podroze/02-poprawki-po-grze/plan.md`) ma kolumny `Wątek | Kto | Zakres | Pliki | Stan`,
    więc „stan” dostaje listę plików, gałąź jest pusta, a start to sama data (słupki bez długości).
  - Zadania: generator bierze do „W toku” tylko sekcję `## W toku`. Nagłówek planu bieżącej podróży ma linię
    `Zadania: Z29, Z30, Z1` (u lukrum w tej samej linii co Start: `Start: … · tryb nadzorowany · … · Zadania: Z29, …`).
    Podpunkty `### Ważne` w `Zadania.md` doklejają się dziś do treści poprzedniego zadania.
  - `tryb`: regex szuka `tryb:`, a lukrum pisze `tryb nadzorowany`.
  - Paleta: walidator `node "C:/Users/PC/AppData/Local/Temp/claude/bundled-skills/2.1.330/3bd9fc86e4af6973545a85dc779eb0ad/dataviz/scripts/validate_palette.js" "<hex,...>" --mode light` (i `--mode dark`).
- **Decyzje szefa** (`dokumentacja/Decyzje.md`, 22.11, Z4):
  1. Wygląd: **kolor projektu**: każdy projekt ma swój kolor; pasek i tło nagłówka karty projektu, kolorowe kafle
     przeglądu, kolorowe etykiety stanów wątków (w toku, scalone, czeka). Tło strony dalej jasne i czytelne,
     ciemny tryb też ma działać. Nie czarno-biało.
  2. „Czeka na Ciebie”: sekcja **zwinięta na start** (nagłówek z licznikiem, klik rozwija/zwija). Rozwija się sama
     **tylko gdy pojawi się coś nowego**: strona pamięta widziane sprawy (localStorage, klucz po projekcie + id albo
     treści; owinięte try/catch), nowe sprawy oznacza „nowe”. Po rozwinięciu i obejrzeniu stają się widziane.
  3. Bez formularza odpowiedzi: usuń przyciski Kopiuj, pole ręczne i klikane opcje. Zostaje lista pytań, opcje
     jako zwykły tekst pod pytaniem, rekomendowana wyróżniona.
  4. Na stronie rola „Pomocnik” nazywa się **„pomo”** (też w generatorze).
  5. **Fable osobno**: w „Kto zużywa” osobna rola `Fable` dla wpisów z modelem zawierającym `fable` (przed
     podziałem na Archi/wyko/agenci/pomo; dotyczy też agentów na Fable). Dostaje własny kolor.
  6. Zadania podróży (z linii `Zadania:` planu bieżącej podróży) pokazuj w „W toku” i usuń z „Zaplanowane”.
  7. Postęp na żywo: Archi dodaje hook, który po każdym commicie wyko/Archiego zapisuje do bazy dokument w
     kolekcji `postep` (doc_id = nazwa sesji, np. `wyko-lukrum-02-sklepy`) o polach:
     `{projekt, watek (np. "02/sklepy" albo null), rola ("wyko"|"Archi"), krok (temat ostatniego commita),
     commity (liczba commitów gałęzi od startu), galaz, czas (ISO)}`. Strona subskrybuje też `postep`
     (`onSnapshot`, osobno od `projekty`, brak kolekcji = brak postępu) i przy wątku pokazuje „ostatnio: <krok> · 5 min temu”
     (wątek dopasowany po projekcie i nazwie albo gałęzi); wątek w toku bez postępu dłużej niż 1 h oznaczony „cisza”.
     Postęp Archiego (watek null) przy nagłówku projektu. Tekst z bazy wstawiaj przez textContent.
- **Pliki do zmiany / utworzenia:** `narzedzia/dziennik/generuj.py`, `narzedzia/dziennik/strona.html`,
  `narzedzia/dziennik/testy/*`, `dokumentacja/podroze/01-dziennik/watek-generator.md` (schemat).
  **Nie ruszaj:** `narzedzia/wyko.py`, `narzedzia/archi.py`, `role/`, `skille/`, README dziennika, nic w `Pulpit/lukrum`.
  Strony nie publikujesz (robi to Archi).
- **Do zrobienia w generatorze:**
  - tabele po nazwach kolumn z nagłówka (Wątek, Kto, Plik, Gałąź, Stan; brak kolumny → None);
  - gałąź domyślna `worktree-podroz-NN-<nazwa po ukośniku>`, gdy Stan.md jej nie podaje;
  - start wątku z godziną: pierwszy commit gałęzi (`git log main..<gałąź> --reverse`) albo dodanie pliku wątku,
    na końcu start podróży; `scalono` z commita scalenia, a gdy go brak i stan zaczyna się od „scalone”, data z gita
    ostatniego commita gałęzi albo null;
  - `tryb` z `tryb:` i `tryb `; punkty listy kończą się na nagłówku `#`;
  - rola Fable, „pomo”; zadania podróży do „W toku”.
- **Gotowe, gdy:**
  - testy: `python -X utf8 -m unittest discover -s narzedzia/dziennik/testy` → `OK` (nowe testy: dodatkowa kolumna
    tabeli, `###` w zadaniach, `Zadania:` w nagłówku, Fable, tryb bez dwukropka);
  - JSON lukrum: 4 wątki z poprawnym stanem i gałęzią, Z29/Z30/Z1/Z31/Z34 w `w_toku`, żadne zadanie nie zawiera `###`,
    w `koszty.role` jest `Fable`, brak `Pomocnik` (`grep -c Pomocnik` w JSON i stronie → 0);
  - walidator palety: PASS dla jasnego i ciemnego (wynik w raporcie);
  - podgląd: zrób `_robocze/03-strona/podglad.html`, który podstawia sztuczne `window.claude.use("db")` z danymi z
    obu JSON i przykładowym `postep`, i zrób zrzuty (np. `msedge --headless --screenshot`, szerokość 1280 i 390)
    do `_robocze/03-strona/`. Jeśli zrzut się nie uda, napisz w raporcie, Archi sprawdzi w przeglądarce.
- **Zrzuty ekranu:** tak, 2–4 (komputer i telefon, sekcja zwinięta i rozwinięta) do `_robocze/03-strona/`, poza gitem.
- **Dokumenty do poprawienia:** `watek-generator.md` (schemat: `postep`, rola Fable/pomo).
- **Archi:** archi-cyberiada
