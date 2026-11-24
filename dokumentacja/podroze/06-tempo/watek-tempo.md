# Wątek: tempo (podróż 06)

## Brief
- **Cel:** narzędzia do trzech temp pracy (żółw / zwykły / królik): badanie kosztów z logów, odczyt limitu 5h, rada o tempie, start wyko według tempa, tempo widoczne w dzienniku.
- **Ustalone (nie sprawdzaj ponownie):**
  - Logi sesji: `~/.claude/projects/*/*.jsonl`. Czytanie wpisów i wagi są w `narzedzia/zuzycie.py` (`wpisy`, `wazone`, `odczyt_cache`, `mnoznik`): użyj ich (import), nie kopiuj. Wiedza o cenach: `dokumentacja/wiedza/tokeny.md`.
  - Nazwy sesji: `archi-<projekt>`, `wyko-<projekt>-NN-<wątek>`; agenci liczą się do sesji, która ich wywołała (tak jak w `zuzycie.py`).
  - Statusline Claude Code dostaje JSON na stdin; pola `rate_limits.five_hour.used_percentage` (0–100) i `.resets_at` (epoch s), też `seven_day.*`, `context_window.used_percentage`, `model.display_name`. Pola mogą nie istnieć (wtedy nic nie zapisuj o limicie). Konfiguracja: `"statusLine": {"type": "command", "command": "..."}` w `~/.claude/settings.json`. Źródło: https://code.claude.com/docs/en/statusline
  - `--autocompact` minimum 100k. `--effort low|medium|high|xhigh|max`. Model `opusplan` istnieje (Opus w plan mode, Sonnet poza nim).
  - Okno 5h liczy się od pierwszej wiadomości; koniec okna = `resets_at`, start = `resets_at − 5 h`.
  - Testy: `unittest` (pytest nie ma). Wszystkie testy (też `test_zuzycie.py`) są w `narzedzia/dziennik/testy/`; tam dodaj nowe.
- **Decyzje szefa (24.11):**
  - Żółw: najwięcej pracy z tokenów; ideał = praca bez przestojów przez całe 5 h i 100% limitu przy końcu okna. **Nie zatrzymuje się i nie czeka** — tempo reguluje oszczędnością (effort, model, liczba wyko), nie przerwami.
  - Królik: szybko teraz, mniej oszczędnie, ale dobrze. Zwykły: jak dziś (bez słowa przy `/hejo`, `/papa`).
  - Archi w żółwiu: `opusplan` + oszczędne zachowanie.
  - Zgoda na dopisanie `statusLine` do `~/.claude/settings.json` na tym komputerze (przez `instaluj.py`).
- **Do zrobienia:**
  1. **`narzedzia/analiza.py`** (badanie z logów, wszystkie projekty, opcja `--od`): wypisz krótki raport (Markdown, do 60 linii) i `--json`:
     - udział Archiego, wyko, agentów (ważone);
     - Archi: koszt tury w funkcji wielkości kontekstu (przedziały np. <50k, 50–100k, 100–200k, >200k: średnie ważone na turę, liczba tur);
     - przerwy: tury po przerwie > 5 min i > 1 h, ile ważonych zjadł ponowny zapis cache (suma i średnia), ile to % całości;
     - wyko: koszt startu (pierwsze N tur do pierwszej zmiany pliku albo pierwsze 3 tury), koszt całej sesji, liczba commitów w gałęzi/worktree jeśli da się ustalić z logów (np. wywołania `git commit` w narzędziach), koszt na commit; zależność od długości wątku (czas trwania);
     - `/compact` (wpisy podsumowania): ile ich i średni koszt;
     - jeśli w logach jest effort albo model: rozbicie według nich.
     Uruchom na prawdziwych logach i zapisz wynik do `_robocze/06-tempo/analiza.md` (do raportu wątku wpisz najważniejsze liczby).
  2. **`narzedzia/statusline.py`:** czyta JSON ze stdin, wypisuje jedną krótką linię (model · kontekst % · limit 5h % · do resetu GG:MM) i zapisuje `~/.claude/cyberiada-limit.json` `{five_hour: {used, resets_at}, seven_day: {...}, czas: <teraz ISO>}` (zapis atomowy, błędy cicho; bez pól limitu nie nadpisuj pliku).
  3. **`narzedzia/tempo.py`:** czyta plik limitu (ostrzega, gdy starszy niż 15 min), liczy: % czasu okna, % limitu, różnicę, prognozę godziny 100% przy obecnym tempie, i radę dla tempa z `--tempo` (domyślnie z `dokumentacja/Stan.md` bieżącego folderu, linia `Tempo: ...`):
     - żółw: za szybko (limit > czas + 10 pp) → „oszczędniej: effort low, bez nowego wyko równolegle, Haiku do drobnych”; za wolno (limit < czas − 10 pp) → „dodaj wyko / wyższy effort”; inaczej „tempo dobre”. Nigdy „czekaj”.
     - królik i zwykły: tylko liczby i prognoza.
     Wynik po polsku, 3–5 linii; `--json` też.
  4. **`wyko.py --tempo zolw|zwykly|krolik`** (domyślnie z `Tempo:` w `Stan.md` projektu, a bez tego `zwykly`): żółw → `--model sonnet --effort low` gdy w briefie jest `Rodzaj: mechaniczny`, inaczej `medium`, `--autocompact 120k`; zwykły → jak dziś (`sonnet`, `medium`, `200k`); królik → `sonnet`, `medium` (`high` gdy w briefie `Rodzaj: trudny`), `200k`. `--model` i nowe `--effort` z linii poleceń wygrywają. Wypisz wybrane tempo przy starcie i w `--pokaz`.
  5. **`instaluj.py`:** dopisuje `statusLine` (polecenie `python -X utf8 <ścieżka>/narzedzia/statusline.py`) do `~/.claude/settings.json`, gdy go nie ma (nie nadpisuje innego statusline; wtedy tylko ostrzeżenie); `--sprawdz` pokazuje stan. Zrób kopię settings.json przed zapisem. Uruchom instalację.
  6. **Dziennik:** `generuj.py` czyta z `Stan.md` linię `Tempo: żółw|zwykły|królik` (wstęp pliku, jak „Archi żył”) → klucz `tempo` (brak = `null`); `strona.html` pokazuje tempo przy nazwie projektu (klocek i nagłówek panelu: 🐢 / 🐇, zwykły bez znaczka) oraz limit 5h, jeśli generator go poda (`limit`: z pliku limitu, w danych wspólnych, nie per projekt — sprawdź, gdzie generator trzyma dane wspólne, i dodaj tam). Schemat dopisz w `dokumentacja/podroze/01-dziennik/watek-generator.md`.
  7. Testy do 1–6 (dane testowe, bez prawdziwych logów).
- **Pliki do zmiany / utworzenia:** `narzedzia/{analiza,statusline,tempo}.py` (nowe), `narzedzia/wyko.py`, `narzedzia/instaluj.py`, `narzedzia/dziennik/{generuj.py,strona.html}`, testy w `narzedzia/dziennik/testy/`, `dokumentacja/podroze/01-dziennik/watek-generator.md`.
  **Nie ruszaj:** `zuzycie.py` (tylko import), `hook_commit.py`, `pracownicy.py`, `role/`, `skille/`, `szablony/`, `zasady/`, reszta dokumentacji. Strony nie publikujesz.
- **Gotowe, gdy:**
  - `python -X utf8 -m unittest discover -s narzedzia/dziennik/testy` → OK;
  - `analiza.py` daje raport na prawdziwych logach (`_robocze/06-tempo/analiza.md`);
  - `echo '<json z limitem 40%>' | python -X utf8 narzedzia/statusline.py` zapisuje plik, `tempo.py --tempo zolw` daje radę zgodną z liczbami;
  - `wyko.py <ten plik> --tempo zolw --pokaz` pokazuje `--effort medium --autocompact 120k`;
  - `instaluj.py --sprawdz` pokazuje statusline.
- **Zrzuty ekranu:** jeden: klocek projektu z żółwiem i limitem (komputer), do `_robocze/06-tempo/` (podgląd z fałszywą bazą jak w `_robocze/05-dziennik3/`).
- **Dokumenty do poprawienia:** schemat w `watek-generator.md`. README/ściągawkę robi Archi.
- **Archi:** archi-cyberiada

## Raport
<!-- Pisze wyko na końcu. -->
