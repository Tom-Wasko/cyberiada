# Wątek: tryby (podróż 07)

## Brief
- **Cel:** narzędzia dla nowych trybów pracy (komp / sen / szkoła) zamiast temp (żółw / zwykły / królik): rada o tempie z limitu 5 h i tygodnia, start wyko według trybu, hook ciągłości po scaleniu, tryb w dzienniku, start czatu Archiego bez poleceń.
- **Rodzaj:** trudny
- **Ustalone (nie sprawdzaj ponownie):**
  - Tryby i linia w `dokumentacja/Stan.md` projektu (zastępuje dawne `Tryb:` + `Tempo:`):
    - `Tryb: komp od 16:10` — nadzorowany, szef przy komputerze, szybko.
    - `Tryb: sen od 23:10` — noc, Archi całkiem sam; cel: cały limit 5 h zużyty w 5 h; hamulec tygodniowy.
    - `Tryb: szkoła do 16:00 (znikam)` albo `(jestem)` — rama czasowa; tempo rozłożone do końca ramy; hamulec tygodniowy.
    - Parser ma przyjmować też ogonki/bez ogonków (`szkoła`/`szkola`) i stary zapis: `nadzorowany` → komp, `autonomiczny` → sen (lukrum ma jeszcze stary `Stan.md`; plików lukrum nie zmieniasz). Brak linii → komp.
  - Plik limitu `~/.claude/cyberiada-limit.json` (pisze `narzedzia/statusline.py`, bez zmian): `{"five_hour": {"used": %, "resets_at": epoch}, "seven_day": {"used": %, "resets_at": epoch}, "czas": ISO}`. Okno 5 h: start = `resets_at − 5 h`. Tydzień: start = `seven_day.resets_at − 7 dni`.
  - Obecny `narzedzia/tempo.py` (119 linii) ma już: odczyt pliku limitu, ostrzeżenie o starych danych, procent czasu okna, różnicę, prognozę 100%, radę żółwia; `tempo_nazwa`, `tempo_ze_stanu` importuje `wyko.py`. Testy: `narzedzia/dziennik/testy/test_tempo.py`. Wszystkie testy `unittest` w `narzedzia/dziennik/testy/` (pytest nie ma).
  - Skille instaluje `narzedzia/instaluj.py` jako dowiązania `~/.claude/skills/<nazwa>` → `cyberiada/skille/<nazwa>` (funkcja `dowiazania`). Archi w osobnym wątku usuwa foldery `skille/{hejo,papa,podroz,wznow}` i dodaje `skille/{komp,sen,szkola,hej}` (w Twoim worktree ich jeszcze nie ma: testuj na folderach tymczasowych).
  - `narzedzia/archi.py`: `TRYBY = {"hejo","papa","wznow","podroz"}`; bez argumentu po nazwie projektu nie wysyła promptu.
  - `narzedzia/dziennik/hook_commit.py`: po commicie Archiego ze scaleniem (`len(rodzice) > 2` albo krok zaczyna się od „scalenie”) dopisuje przypomnienie (linie ok. 59–62).
- **Decyzje szefa (26.11, `dokumentacja/Decyzje.md`):** nowe tryby jak wyżej; Archi zawsze na Opusie (`opusplan` odpada: nie podpowiadaj go nigdzie); hamulec tygodniowy w śnie (i w szkole); po scaleniu Archi sam bierze następne zadanie (szef: „nie podoba mi się, że archi nie otwiera nowych wyko po zamknięciu starych”); bez poleceń `/podroz`, `/wznow`: nowy czat Archiego sam pyta o podróż.
- **Do zrobienia:**
  1. **`git mv narzedzia/tempo.py narzedzia/tryb.py`** (i test → `test_tryb.py`), przerób:
     - `tryb_ze_stanu(folder)` → `{"tryb": "komp"|"sen"|"szkola", "od": "GG:MM"|None, "do": "GG:MM"|None, "stan": "jestem"|"znikam"|None}`; `tryb_nazwa(tekst)` normalizuje.
     - **sen:** linia idealna okna 5 h (limit % ≈ czas % okna). Rada: limit > czas + 10 pp → „oszczędniej: effort low, bez nowego wyko”; limit < czas − 10 pp → „dodaj wyko albo wyższy effort”; inaczej „tempo dobre”. Nigdy „czekaj”.
     - **szkoła:** cel = 100% limitu w chwili `T = min(reset okna, koniec ramy)` (jeśli rama kończy się po resecie, liczy się bieżące okno). Linia idealna od startu okna do `T`; rada jak w śnie. Po końcu ramy: wynik ma `"po_ramie": true` i radę „rama minęła: podsumowanie dla szefa, dalej jak w śnie”.
     - **hamulec tygodniowy (sen, szkoła):** czas % tygodnia vs `seven_day.used`; tydzień > czas + 5 pp → rada tygodnia „tydzień przed linią o X pp: oszczędniej, bez nowego wyko” i ta rada wygrywa z „dodaj wyko”. Flaga `--bez-hamulca` (testy Z10 celowo zużywają resztę tygodnia).
     - **komp:** tylko liczby (okno, tydzień, prognoza), bez rady.
     - Wynik: pole `wyko` z radą liczbową `+1` / `0` / `-1` (dla Archiego: ile wyko dodać/odjąć), 3–6 linii po polsku, `--json`, `--plik`, `--tryb`, `--do GG:MM` (nadpisuje rama z `Stan.md`), `--teraz` (ISO, do testów).
  2. **`wyko.py --tryb komp|sen|szkola`** (zamiast `--tempo`; domyślnie z `Stan.md` projektu, brak → komp): komp → `sonnet`, `medium` (`high` gdy w briefie `Rodzaj: trudny`), autocompact `200k`; sen i szkoła → `sonnet`, `low` gdy `Rodzaj: mechaniczny`, inaczej `medium`, autocompact `120k`. `--model`/`--effort` z linii poleceń wygrywają. Wypisz tryb przy starcie i w `--pokaz`. Podpis `wspolne_flagi(model, effort, autocompact)` zostaw bez zmian (importuje go wątek 07/eksperyment).
  3. **`hook_commit.py` — ciągłość:** w przypomnieniu po scaleniu (Archi) dopisz: następne zadanie z `dokumentacja/Zadania.md` projektu (pierwsza linia `- Z<n> · …` z sekcji „Następnie”, a gdy pusta — z „Zaplanowane”; obetnij do ok. 120 znaków) i polecenie: „Ciągłość: jeśli nie czeka na decyzję szefa, w tej samej turze napisz wątek i uruchom wyko (albo zrób sam, gdy małe).” Gdy obie sekcje puste: „Lista pusta: w trybie komp zaproponuj szefowi nowy plan okienkiem; w śnie i szkole zapisz to w Stan.md i weź coś z Odłożone bez decyzji szefa albo zakończ.” Brak pliku → nic.
  4. **Dziennik:** `generuj.py` czyta linię `Tryb:` przez `tryb_ze_stanu` (zamiast `Tempo:`) → klucz `tryb` (obiekt jak wyżej albo `null`); usuń `tempo`. `strona.html`: znaczek trybu przy nazwie projektu (klocek i nagłówek panelu): komp 💻, sen 🌙, szkoła 🎒 z „do 16:00” i stanem (jestem/znikam). Zamiast 🐢/🐇. Schemat w `dokumentacja/podroze/01-dziennik/watek-generator.md`. Strony nie publikujesz (zrobi to Archi). Pliki strony i generatora mają końce linii CRLF: zachowaj je.
  5. **`instaluj.py`:** przy instalacji usuwa z `~/.claude/skills` dowiązania wskazujące do `cyberiada/skille/<nazwa>`, których folder już nie istnieje (tylko dowiązania do cyberiady; nic innego nie usuwa); `--sprawdz` pokazuje je jako „stare”. Nie uruchamiaj instalacji na prawdziwym `~/.claude` (zrobi to Archi po scaleniu); testuj na folderze tymczasowym.
  6. **`archi.py`:** `TRYBY = {"komp","sen","szkola","hej"}`. Gdy po nazwie projektu nic nie ma, wysyła prompt startowy `start` (też przy `--resume`). Gdy jest słowo trybu, wysyła `/komp` itd. jak dziś. Pomoc bez argumentów: `archi <projekt> [komp | sen | szkola 16:00]`. Dodaj `--pokaz` (wypisz polecenie, nie uruchamiaj).
  7. Testy do 1–6 (dane testowe; czas przez `--teraz`/parametr, nie zegar).
- **Pliki do zmiany / utworzenia:** `narzedzia/tryb.py` (z `tempo.py`), `narzedzia/wyko.py`, `narzedzia/archi.py`, `narzedzia/instaluj.py`, `narzedzia/dziennik/{hook_commit.py,generuj.py,strona.html}`, testy w `narzedzia/dziennik/testy/`, `dokumentacja/podroze/01-dziennik/watek-generator.md`.
  **Nie ruszaj:** `statusline.py`, `zuzycie.py`, `narzedzia/eksperyment/` (inny wątek), `role/`, `skille/`, `szablony/`, `zasady/`, `README.md`, reszta dokumentacji, pliki lukrum.
- **Gotowe, gdy:**
  - `python -X utf8 -m unittest discover -s narzedzia/dziennik/testy` → OK;
  - `python -X utf8 narzedzia/tryb.py --tryb sen --plik <próbny> --teraz <…>` i `--tryb szkola --do 16:00` dają radę zgodną z liczbami (w raporcie po jednym przykładzie: za szybko, za wolno, tydzień przed linią);
  - `python -X utf8 narzedzia/wyko.py dokumentacja/podroze/07-tryby/watek-tryby.md --tryb sen --pokaz` → `--effort medium`, `--autocompact 120k`;
  - `python -X utf8 narzedzia/archi.py cyberiada --pokaz` → polecenie kończy się promptem `start`.
- **Zrzuty ekranu:** nie.
- **Dokumenty do poprawienia:** tylko schemat w `watek-generator.md` (README zrobi Archi).
- **Archi:** archi-cyberiada

## Raport
<!-- Pisze wyko na końcu. -->

### Raport wyko (26.11)
Zrobione kroki 1–7. Gałąź `worktree-podroz-07-tryby`.
- **tryb.py** (z tempo.py): `tryb_ze_stanu`, `tryb_z_tekstu`, `tryb_nazwa`, `licz`; flagi `--tryb --do --json --plik --bez-hamulca --teraz`. Poza briefem: `tryb_z_tekstu` zwraca `null` bez linii (dla generuj), `tryb_ze_stanu` daje komp.
- **wyko.py** `--tryb` (`ustawienia_trybu`), **archi.py** (`start`, `--pokaz`, nowe TRYBY), **hook_commit.py** (`nastepne_zadanie` + ciągłość), **generuj.py/strona.html** (klucz `tryb`, 💻🌙🎒; CRLF zachowane), **instaluj.py** (`stare_skille`, `usun_dowiazanie`, „stare” w `--sprawdz`; CRLF zachowane), schemat w `watek-generator.md`.
- Dowody:
  - `python -X utf8 -m unittest discover -s narzedzia/dziennik/testy` → `Ran 80 tests ... OK`
  - sen, za szybko (okno 50% czasu, 75% limitu): `Rada: oszczędniej: effort low, bez nowego wyko. Wyko: -1.`
  - sen, za wolno (25%): `Rada: dodaj wyko albo wyższy effort. Wyko: +1.`
  - sen, tydzień przed linią (tydzień 50% czasu, 60% limitu, okno wolno): `Rada: tydzień przed linią o 10 pp: oszczędniej, bez nowego wyko. Wyko: -1.`
  - szkoła `--do 13:00` (teraz 12:00, okno 9:30–14:30): `minęło 71% czasu do celu (... cel 100% o 13:00), zużyto 25% ... Wyko: +1.`
  - `wyko.py ... --tryb sen --pokaz` → `Tryb: sen (model sonnet, effort medium, autocompact 120k)`
  - `archi.py cyberiada --pokaz` → polecenie kończy się `...role\archi.md start`
- Uwagi: `instaluj.py` na prawdziwym `~/.claude` nie uruchamiany (tylko `--sprawdz` i test na junctionach w folderze tymczasowym). Test instalatora używa `mklink /J` (Windows). Strona nie publikowana. Stare `tempo` w `Stan.md` (np. lukrum) jest ignorowane → `tryb: null`.
- Propozycje: brak.
