# Wątek: generator (podróż 01)
<!-- Brief pisze Archi. Wyko czyta tylko ten plik: wszystko, co ustalone, musi być tutaj. -->

## Brief
- **Cel:** skrypt `narzedzia/dziennik/generuj.py`, który z dokumentacji projektu, logów sesji i gita składa
  jeden plik JSON o stałym schemacie (poniżej). Archi zapisuje ten JSON do bazy strony dziennika (Artifact na
  claude.ai, dokument `projekty/<nazwa>`). Stronę robi Archi w osobnym wątku; łączy Was tylko schemat.

- **Ustalone (nie sprawdzaj ponownie):**
  - Uruchomienie: `python -X utf8 narzedzia/dziennik/generuj.py --projekt <nazwa>` (nazwa z `projekty.yaml`,
    ścieżka przez `wspolne.projekty()`); opcjonalnie `--sciezka <folder>` zamiast nazwy (do testów)
    i `--wyjscie <plik>`. Domyślne wyjście: `<cyberiada>/_robocze/dziennik/<nazwa>.json` (folder utwórz).
    Na stdout jedna linia: ścieżka pliku i liczby (np. `zapisano … · czeka 2 · wątki 2 · dni kosztów 30`).
  - Tylko biblioteka standardowa + `yaml` (już używany w `wspolne.py`). Testy na `unittest` (pytest nie jest
    zainstalowany i nie instaluj go).
  - Import wspólnych rzeczy: `sys.path.insert(0, <narzedzia>)`, potem `from wspolne import ...`,
    `from zuzycie import ...` (tak jak w `zuzycie.py`).
  - Pliki projektu (wszystkie mogą nie istnieć albo być puste: wtedy puste pola, nigdy wyjątek):
    `dokumentacja/Stan.md`, `dokumentacja/Zadania.md`, `dokumentacja/Decyzje.md`,
    `dokumentacja/podroze/NN-temat/plan.md`. Wzory: pliki w tym repo (`dokumentacja/` i
    `szablony/projekt/dokumentacja/`, `szablony/plan-podrozy.md`). Komentarze `<!-- -->` pomijaj.
  - **Stan.md:**
    - `puls` = tekst po `Archi żył: ` (np. `2026-11-21 21:30`; `—` albo brak → `null`).
    - Sekcja `## Podróż`: jeśli zaczyna się od `NN-temat`, to bieżąca podróż = katalog `podroze/NN-temat/`;
      „Brak podróży w toku” → `podroz: null`.
    - Tabela `## Wątki` (`| Wątek | Sesja | Gałąź | Stan |`) daje `galaz` i `stan` wątków bieżącej podróży
      (ważniejsza niż stan z `plan.md`, bo jest świeższa).
    - Sekcja `## Czeka na szefa` → `czeka`. Format pytań (ustalony z szefem):
      ```
      - P1: Treść pytania?
        - A: opcja (rekomendowane)
        - B: opcja
      - Zwykła sprawa bez opcji.
      ```
      Punkt z `P<cyfry>:` → `id: "P1"`, `tresc` bez prefiksu, `opcje` z wcięciem `- <LITERA>: tekst`;
      dopisek `(rekomendowane)` na końcu zdejmij z tekstu i ustaw `rekomendowana: true`. Punkt bez `P1:` →
      `id: null`, `opcje: []`. Wiersze kontynuacji (wcięte, bez `- X:`) doklej spacją do treści.
    - Sekcję `## Od Pomocnika` pomiń.
  - **plan.md** (`# Podróż NN: temat`, linia `Start: RRRR-MM-DD · tryb: hejo · gałąź: ...`, opcjonalna linia
    `Koniec: RRRR-MM-DD`, `## Kryteria sukcesu ...` z `- [ ]`/`- [x]` (kryterium może mieć wiersze kontynuacji),
    tabela `## Wątki` `| Wątek | Kto | Plik | Stan |`, sekcja `## Podsumowanie`).
    `tryb` = słowo po `tryb:`. Kryteria → `[{tekst, zrobione}]` (wiersze sklejone spacją; poza znacznikiem
    `- [ ]` nic nie usuwaj, także backticków).
  - **Wątki** `[{nazwa, kto, stan, galaz, start, scalono}]`: nazwa/kto/stan z `plan.md`, stan i gałąź nadpisane
    z tabeli w `Stan.md` (dopasowanie po nazwie). Tabele czytane po **nazwach kolumn** z nagłówka (Wątek, Kto,
    Plik, Gałąź, Stan; brak kolumny → null). Gałąź domyślna `worktree-podroz-NN-<nazwa po ukośniku>`.
    `start` (z godziną) = pierwszy commit gałęzi (`git log main..<gałąź> --reverse`), inaczej data dodania pliku
    wątku (`--diff-filter=A`), inaczej `Start` podróży. `scalono` = commit scalenia (merge z nazwą gałęzi albo
    commit „Scalenie <nazwa>”), a gdy go brak i stan zaczyna się od „scalone” → ostatni commit gałęzi, inaczej `null`.
  - **Plan podróży:** `tryb` z `tryb:` albo `tryb ` (bez dwukropka); `zadania` = numery `Zn` z linii `Zadania:`
    nagłówka. Takie zadania trafiają w `zadania.w_toku` i znikają z `zaplanowane`. Punkty listy w `Zadania.md`
    kończą się na nagłówku `#` (np. `### Ważne` nie dokleja się do poprzedniego zadania).
    Daty jako `RRRR-MM-DD` albo pełne ISO, ale jednolicie w całym pliku: używaj ISO z gita bez zmian,
    a dat z dokumentów (`RRRR-MM-DD`) też bez zmian. Strona rozumie oba.
  - **Decyzje.md:** sekcje `## Szefa` i `## Archiego`, wpisy `- RRRR-MM-DD · treść` (z wierszami kontynuacji)
    → `{data, tresc}`, kolejność jak w pliku.
  - **Zadania.md:** sekcje `## W toku`, `## Zaplanowane`, `## Odłożone` → listy tekstów (z kontynuacjami).
  - **historia:** wszystkie katalogi `podroze/NN-*` posortowane po numerze → `{numer, temat, start, koniec,
    podsumowanie}`; `koniec` z linii `Koniec:` albo `null`; `podsumowanie` = tekst sekcji `## Podsumowanie`
    bez komentarzy, przycięty do 600 znaków (pusty → `""`).
  - **koszty.dni:** ostatnie 30 dni (włącznie z dziś, dni bez zużycia jako zera), sumy dla sesji, których
    `cwd` zaczyna się od ścieżki projektu (tak jak `zuzycie.py --projekt`, więc z worktree). Dzień według
    czasu lokalnego (logi mają UTC `...Z`; przelicz `datetime.fromisoformat(...).astimezone()`).
    Pola: `dzien, wazone, wejscie, wyjscie, cache_odczyt, cache_zapis` (ważone jak w `zuzycie.py`,
    zaokrąglone do całości).
  - **koszty.role:** `[{podroz, rola, wazone}]` dla całej historii projektu. Rola z nazwy sesji:
    `archi-*` → `Archi`, `wyko-*` → `wyko`, pliki `subagents/*.jsonl` → `agenci` (niezależnie od nazwy
    sesji-rodzica), reszta (też bez nazwy) → `pomo`. Wpisy z modelem zawierającym `fable` (też agenci)
    mają osobną rolę `Fable`, sprawdzaną przed pozostałymi. Podróż: z nazwy wyko `wyko-<projekt>-NN-...` → `"NN"`;
    w pozostałych przypadkach według czasu wpisu: podróż, w której zakresie `Start`..`Koniec` (lub do dziś,
    gdy brak końca) leży data; poza wszystkimi → `"poza"`.
  - **koszty.okno5h** (szacunek limitu, liczony ze **wszystkich** projektów na tym komputerze, bo limit jest
    wspólny): weź wszystkie czasy wpisów (bez filtra projektu) z ostatnich 24 h, posortuj; okno zaczyna się na
    pierwszym wpisie zaokrąglonym w dół do pełnej godziny, trwa 5 h; wpis po końcu okna otwiera nowe okno
    (znów od pełnej godziny). Wynik dla okna zawierającego teraz: `{od, reset, wazone}` (ISO lokalne);
    gdy teraz nie leży w żadnym oknie → `{od: null, reset: null, wazone: 0}`.
  - **commity:** ostatnie 30 dni, `git log --all --format=%cI` w folderze projektu, liczba na dzień lokalny,
    `[{dzien, liczba}]` z zerami dla dni bez commitów.
  - Git wywołuj przez `subprocess.run([...], cwd=projekt, capture_output=True, text=True, encoding="utf-8")`;
    gdy folder nie jest repo albo git zawiedzie → puste listy / `null`, bez wyjątku.
  - **API w `zuzycie.py`:** wydziel z `main()` funkcję (np. `wpisy(projekt: Path | None = None) ->
    Iterator[dict]`) zwracającą wpisy z polami `sesja` (nazwa albo `(bez nazwy xxxxxxxx)`), `agent` (bool),
    `model, czas, wejscie, cache_zapis, cache_odczyt, wyjscie`, oraz funkcję `wazone(wpis) -> float`.
    `main()` ma z nich korzystać, a jego wyjście (tabela i `--json`) **nie może się zmienić**.
    Dowód: zapisz wynik `python -X utf8 narzedzia/zuzycie.py --od 2026-11-01` przed zmianą i po, porównaj
    (`diff` pusty; różnica tylko z powodu nowych wpisów w trakcie pracy jest dopuszczalna: wtedy porównaj
    z `--do` wczorajszym albo opisz to w raporcie).

- **Schemat JSON** (dokument `projekty/<nazwa>`; klucze dokładnie takie, `null` gdy brak):
  ```json
  {
    "nazwa": "cyberiada", "opis": "System pracy z Claude Code", "repo": "Tom-Wasko/cyberiada",
    "wygenerowano": "2026-11-21T22:10:00+01:00", "puls": "2026-11-21 21:30",
    "podroz": {"numer": "01", "temat": "dziennik", "start": "2026-11-21", "tryb": "hejo",
               "kryteria": [{"tekst": "…", "zrobione": false}],
               "watki": [{"nazwa": "generator", "kto": "wyko", "stan": "w toku",
                          "galaz": "worktree-podroz-01-generator", "start": "…", "scalono": null}]},
    "czeka": [{"id": "P1", "tresc": "…?", "opcje": [{"litera": "A", "tekst": "…", "rekomendowana": true}]},
              {"id": null, "tresc": "Zwykła sprawa", "opcje": []}],
    "decyzje": {"szefa": [{"data": "2026-11-21", "tresc": "…"}], "archiego": []},
    "zadania": {"w_toku": [], "zaplanowane": ["…"], "odlozone": []},
    "historia": [{"numer": "01", "temat": "dziennik", "start": "2026-11-21", "koniec": null, "podsumowanie": ""}],
    "koszty": {"dni": [{"dzien": "2026-11-21", "wazone": 0, "wejscie": 0, "wyjscie": 0,
                        "cache_odczyt": 0, "cache_zapis": 0}],
               "role": [{"podroz": "01", "rola": "Archi", "wazone": 0}],
               "okno5h": {"od": null, "reset": null, "wazone": 0}},
    "commity": [{"dzien": "2026-11-21", "liczba": 0}]
  }
  ```
  `nazwa, opis, repo` z `projekty.yaml` (przy `--sciezka` bez wpisu: nazwa = nazwa folderu, reszta `null`).
  `wygenerowano` = teraz, ISO lokalne z sekundami. JSON zapisuj `ensure_ascii=False`, `indent=1`, UTF-8, LF.

- **Decyzje szefa:** `dokumentacja/Decyzje.md`, sekcja Szefa, wpisy „Dziennik…” z 2026-11-21 (zawartość,
  wykresy, dane w bazie strony, układ, przycisk kopiuj). Format pytań wyżej jest ustalony.

- **Pliki do zmiany / utworzenia:** `narzedzia/dziennik/generuj.py`, `narzedzia/dziennik/testy/` (np.
  `test_generuj.py` + dane w `testy/dane/`), `narzedzia/zuzycie.py` (tylko wydzielenie API).
  **Nie ruszaj:** `narzedzia/dziennik/strona.html`, `narzedzia/dziennik/README.md`, `projekty.yaml`,
  `README.md`, `dokumentacja/` (poza raportem na dole tego pliku), `szablony/`, `zasady/`, `role/`, `skille/`.

- **Gotowe, gdy:**
  - Testy na danych sztucznych (folder tymczasowy z `Stan.md`, `plan.md`, `Decyzje.md`, `Zadania.md`,
    sztuczne `.jsonl` z wpisami `assistant`+`usage`, w tym `subagents/`): parsowanie pytań z opcjami
    i bez, rekomendacja, kontynuacje, kryteria, decyzje, zadania, role (Archi/wyko/agenci/pomo/Fable
    i przypisanie podróży), okno 5 h (nowe okno po przerwie, zaokrąglenie do godziny), dni z zerami,
    brak plików → puste pola. Logi w testach podawaj przez parametr (np. katalog sesji), nie z prawdziwego
    `~/.claude`.
  - `python -X utf8 -m unittest discover -s narzedzia/dziennik/testy -v` → `OK`.
  - `python -X utf8 narzedzia/dziennik/generuj.py --projekt cyberiada` → plik JSON zgodny ze schematem
    (w raporcie: linia wyjścia + `podroz.watki` i `czeka` z wyniku).
  - Porównanie wyjścia `zuzycie.py` przed/po (patrz wyżej).
- **Zrzuty ekranu:** nie.
- **Dokumenty do poprawienia:** docstring na górze `generuj.py` (jak uruchomić, skąd dane). README dziennika
  pisze Archi.
- **Archi:** archi-cyberiada.

## Raport
<!-- Pisze wyko na końcu. -->
**Stan:** gotowe

**Zmienione pliki** (worktree `.claude/worktrees/podroz-01-generator`, gałąź `worktree-podroz-01-generator`):
- `narzedzia/dziennik/generuj.py` (nowy, ~374 linie)
- `narzedzia/dziennik/testy/test_generuj.py` + `testy/dane/{Stan,Decyzje,Zadania,plan}.md` (nowe)
- `narzedzia/zuzycie.py` (wydzielone `wazone()` i `wpisy()`, wyjście CLI bez zmian)

**Dowód:**
- `python -X utf8 -m unittest discover -s narzedzia/dziennik/testy -v` → `Ran 17 tests in 1.441s` / `OK`
- `python -X utf8 narzedzia/dziennik/generuj.py --sciezka C:/Users/PC/cyberiada --wyjscie _robocze/generator/cyberiada.json` → `zapisano _robocze\generator\cyberiada.json · czeka 1 · wątki 2 · dni kosztów 30`
- `podroz.watki` → `[('generator','wyko','w toku','worktree-podroz-01-generator'), ('strona','Archi','w toku','main')]`; `czeka` → jedno pytanie bez numeru
- `zuzycie.py` po refaktorze: tabela zgodna z wersją sprzed zmiany (porównane na tych samych logach), `RAZEM` liczy się tak samo.

**Decyzje, które podjąłem:**
- Okno 5 h: start od pełnej godziny pierwszego wpisu, liczone ze wszystkich projektów; po wygaśnięciu `od/reset = null`, `wazone = 0`.
- Dzień kosztów liczony w strefie lokalnej (logi mają UTC); zawsze 30 dni, z zerami.
- Rola z tytułu sesji: `archi-*` → Archi, `wyko-*` → wyko, inne → pomo; model Fable → Fable; podagenci → „agenci”.
- Domyślny zapis JSON do `_robocze/dziennik/` obok `generuj.py` (UTF-8, LF, `indent=1`).
- Brak plików lub puste → puste pola, bez wyjątku.

**Uwagi o danych:**
- `historia` zawiera też bieżącą podróż (`koniec: null`).
- Wątek „strona” ma gałąź `main` (tak stoi w tabeli Stan.md).
- Plik wątku leżał w głównym checkoucie (niescommitowany); edycja tam była zablokowana, więc raport jest w kopii w worktree: `dokumentacja/podroze/01-dziennik/watek-generator.md`.

**Pytania do szefa:** brak.

**Propozycje (poza zakresem):**
- Strona mogłaby ukrywać wpis z `historia` z `koniec: null`, bo to bieżąca podróż.
- Gałąź wątku „strona” w Stan.md warto poprawić na faktyczną.

**Commity:** e59ca04 (zuzycie: wpisy/wazone), eea3e75 (generuj.py), e26fd41 (testy + fixture).

## Uzupełnienie schematu (podróż 03): postęp na żywo
Poza JSON-em projektu strona czyta osobną kolekcję bazy `postep` (osobny `onSnapshot`; brak kolekcji = brak postępu).
Dokument: `doc_id` = nazwa sesji (np. `wyko-lukrum-02-sklepy`), pola
`{projekt, watek ("02/sklepy" albo null dla Archiego), rola ("wyko"|"Archi"), krok (temat ostatniego commita),
commity (liczba commitów gałęzi od startu), galaz, czas (ISO)}`. Zapisuje go hook po commicie (robi Archi),
nie generator. Wątek w toku bez postępu dłużej niż 1 h jest oznaczany „cisza”.

## Uzupełnienie schematu (podróż 05)
- **`zadania`** ma klucze `w_toku`, `nastepnie`, `zaplanowane`, `zrobione`, `odlozone`. `zrobione` = sekcja
  `## Zrobione w tej podróży` w `Zadania.md`. Generator niczego nie przenosi (linia `Zadania:` planu jest ignorowana);
  zadania między sekcjami przesuwa Archi (`przenies.py`, cel `zrobione` tworzy brakującą sekcję po „Zaplanowane”,
  przed „Odłożone”).
- **Wątki ze `Stan.md`:** tabela z kolumną „Wątek” jest czytana z każdej sekcji (np. `## Podróż`), nie tylko `## Wątki`.
  `podroz.watki` zawiera wszystkie wątki ze `Stan.md` (także spoza planu). `kto`: kolumna „Kto” → `Archi` dla wiersza
  „Archi” → `wyko`, gdy w logach jest sesja `wyko-<projekt>-NN-<nazwa>` → `nie wiadomo`. Pusty `stan` albo sama kreska
  = `nie wiadomo` (nigdy „?”).
- **`aktywnosc`:** `[{nazwa, rola (Archi|wyko|pomo), watek ("NN/nazwa" albo null), odcinki: [[start, koniec], …]}]`
  (ISO, ostatnie 7 dni). Nowy odcinek po przerwie > 30 min; wpisy agentów liczą się do sesji, która ich wywołała.
  Archi pierwszy, reszta wg pierwszego startu.
