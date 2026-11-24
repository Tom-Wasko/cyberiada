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

### Wynik: wątek zrobiony (wyko, 24.11)
**Dowody**
- `python -X utf8 -m unittest discover -s narzedzia/dziennik/testy` → `Ran 63 tests in 8.754s` / `OK` (w tym nowy `test_tempo.py`, 21 testów).
- `analiza.py --od 2026-11-01` → raport 45 linii w `_robocze/06-tempo/analiza.md` (prawdziwe logi, 14 s).
- `echo '{...limit 40%...}' | statusline.py` → `Sonnet · limit 5h 40% · do resetu 2:59`, plik `~/.claude/cyberiada-limit.json` zapisany; `tempo.py --tempo zolw` → `minęło 40% czasu ... zużyto 40% limitu ... Rada (żółw): tempo dobre.`
- `wyko.py <plik wątku> --tempo zolw --pokaz` → `Tempo: zolw (model sonnet, effort medium, autocompact 120k)`, w poleceniu `--effort medium --autocompact 120k`.
- `instaluj.py --sprawdz` → `✓ statusLine → statusline.py cyberiady`.
- Zrzuty (komputer, fałszywa baza): `_robocze/06-tempo/zrzut-projekt.png` (🐢 w nawigacji, klocku i nagłówku), `zrzut-przeglad.png` (okno 5 h z „Limit 5 h: zużyto 41%”). Konsola czysta.

**Najważniejsze liczby z logów (od 1.11, ważone; 18,9 tys. wpisów)**
- Udział: agenci 26,5%, Archi 10,1%, wyko 8,6%, inne sesje 54,9% (nazwy sesji spoza archi-/wyko-; sesje zwykłych rozmów z Opusem high dominują).
- Przerwy: 410 tur po przerwie >5 min zjadło 7,0% całości na ponowny zapis cache (średnio 95 tys. na turę wobec 12,8 tys. zwykłego zapisu); 70 tur po >1 h: 4,8% całości (średnio 377 tys.).
- /compact: 283, kontekst 160k → 22k; pierwsza tura po nim średnio 158 tys. (zapis cache).
- Wyko (43 sesje): start (do 1. zmiany pliku, mediana 15 tur) = 22,6% kosztu sesji; sesja średnio 1,11 mln, 4,6 commita, 254 tys. na commit. Koszt na turę praktycznie stały (13,4–13,9 tys.), więc koszt rośnie z liczbą tur, nie z długością czasu.
- Archi: koszt tury 54 tys. (50–100k kontekstu), 32 tys. (100–200k), 37 tys. (>200k), brak prostej zależności (tury o małym kontekście częściej płacą za zapis cache).
- Model/effort na turę: Opus high ~35,7 tys., Sonnet medium ~13,7 tys., Haiku low ~0,8 tys., Fable ~92 tys.

**Zmiany:** nowe `narzedzia/{analiza,statusline,tempo}.py`, `narzedzia/dziennik/testy/test_tempo.py`; zmienione `wyko.py` (`--tempo`, `--effort`), `instaluj.py` (`statusLine`, nowa flaga `--statusline`), `dziennik/generuj.py` (`tempo`, `koszty.limit`), `strona.html`, `watek-generator.md`, `test_generuj.py` (schemat o 2 klucze).

**Uwagi / odstępstwa**
- Instalację uruchomiłem tylko krokiem `instaluj.py --statusline`, nie pełną: z worktree pełna zmieniłaby dowiązania `~/.claude/rules|agents|skills` na worktree. Polecenie w settings wskazuje repo główne (`C:/Users/PC/cyberiada/narzedzia/statusline.py`), więc zadziała dopiero po scaleniu (do tego czasu statusline w nowych sesjach pokaże błąd Pythona/pustą linię). Kopia settings.json: `settings.json.kopia-*`.
- Limit w dzienniku to osobny klucz `koszty.limit` (obok `okno5h`), nie nowa sekcja; `tempo` zapisuję bez ogonków (`zolw|zwykly|krolik`).
- Plik `~/.claude/cyberiada-limit.json` zawiera teraz liczby testowe (40%); nadpisze go pierwszy prawdziwy statusline. Nie mogłem go usunąć (`rm` zablokowane).
- Sprzątanie `_robocze/06-tempo/` (podkatalogi `tmp`, `fake`, plik `zrzut.png`, `podglad.html`, `budujpodglad.py`) zablokowane: `rm` odmówiony; folder jest poza gitem.
- Okno >5 h `analiza.py`: „tura” = wywołanie modelu; koszt /compact = pierwsza tura po granicy (sam wpis podsumowania nie ma własnego usage w logu).

**Propozycje (nie wdrażałem)**
- Po scaleniu: `Tempo: żółw` do `Stan.md` cyberiady i krótkie sprawdzenie `tempo.py` z prawdziwym limitem.
- Duży wniosek z liczb: przerwy >5 min kosztują ~7% zużycia, więc w żółwiu warto kończyć serie tur bez pauz zamiast „odpoczywać”.
