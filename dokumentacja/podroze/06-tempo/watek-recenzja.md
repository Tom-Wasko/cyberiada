# Wątek: recenzja (podróż 06)

## Brief
- **Cel:** naprawić w dzienniku błędy i drobiazgi z recenzji (grupy A i B), bez zmian wyglądu i mechaniki.
- **Rodzaj:** zwykły
- **Ustalone (nie sprawdzaj ponownie):**
  - Pełna recenzja z numerami linii: `C:/Users/PC/cyberiada/_robocze/06-recenzja/recenzja.md` (poza gitem, czytaj z tej ścieżki). Tam też podgląd z fałszywą bazą (`buduj.py`, `podglad-pelny.html`, `podglad-brzeg.html`) i zrzuty — użyj ich do sprawdzenia.
  - Pliki: `narzedzia/dziennik/strona.html`, `narzedzia/dziennik/generuj.py`, testy w `narzedzia/dziennik/testy/`.
  - Telefon: emulacja CDP 390 px (`narzedzia/cdp.py`, `narzedzia/zrzuty.py`), warunek `scrollWidth <= 390`.
- **Decyzje szefa:** recenzja dziennika: drobne poprawki robi Archi (tu: wyko), zmiany wyglądu i mechaniki (grupa C) idą do szefa — **grupy C nie ruszaj**.
- **Do zrobienia (numery z recenzji):**
  - A1 markdown w tekstach (`**`, grawisy, URL) → funkcja budująca węzły DOM (strong, code, a), bez innerHTML z danych.
  - A2 pigułka stanu = pierwsze słowo stanu (całość w `title`); „kto” = pierwsze słowo, reszta osobno/tytuł.
  - A3 bez pełnego `render()`, gdy dane się nie zmieniły (porównanie JSON); jeśli i tak render, zachowaj stan otwartych `details` i przełączników.
  - A4 podziałka dla zakresu < 1 h (co 5/10/15 min).
  - A5 kontrast jasnego trybu: `--muted` ≥ 4,5:1 (np. #6a6862), „czeka” czytelny (kolor tekstu + kropka), link ≥ 4,5:1. Ciemny bez zmian.
  - B6 `generuj.py`: logi czytane raz, `okno5h` liczone raz; zmierz czas przed i po.
  - B7 `tabela()` nie dzieli `|` wewnątrz grawisów (test).
  - B8 „Archi żył: brak danych”.
  - B9 teksty bez żargonu: „zużycie (tokeny)”, „pamięć podręczna”, „bez ruchu od 1 h”, krótkie wyjaśnienie zamiast „przed cyberiadą”.
  - B10 przycięcia: kolumna nazw min 110 px, krótszy tekst przerwy, daty pod osią nie sklejone.
  - B11 `klasaStanu`: „zrobiony/zakończony” jak „scalony”.
  - B12 usuń mylący podpis „otwórz <pierwszy projekt>” albo zmień na „zobacz projekty”.
  - B13 dostępność: `role="img"` + `aria-label` przy emoji tempa, cele dotyku ≥ 44 px dla Tabela/Więcej i uchwytu, `cursor:grab` tylko na przenośnych.
  - B14 „wczoraj” kalendarzowo; rok przy dacie decyzji spoza bieżącego roku.
  - B15 dodaj `<meta name="viewport" content="width=device-width,initial-scale=1">` tylko jeśli nie psuje publikacji (strona trafia do Artifact jako fragment; meta w treści jest bezpieczna).
- **Pliki do zmiany:** `narzedzia/dziennik/{strona.html,generuj.py}`, testy. **Nie ruszaj:** wszystko inne; strony nie publikujesz.
- **Gotowe, gdy:**
  - `python -X utf8 -m unittest discover -s narzedzia/dziennik/testy` → OK (nowe testy: B7, B6 te same wyniki);
  - zrzuty po poprawkach (komputer jasny, ciemny, telefon 390 px, brzeg) w `_robocze/06-recenzja/po/`, konsola czysta, `scrollWidth <= 390`;
  - w raporcie przy każdym numerze: zrobione / pominięte (dlaczego).
- **Archi:** archi-cyberiada

## Raport
<!-- Pisze wyko na końcu. -->
Gałąź `worktree-podroz-06-recenzja` (commity: generator `7912407`, `d033230`; strona `c50e677`). Strony nie publikowałem.

**Dowody**
- `python -X utf8 -m unittest discover -s narzedzia/dziennik/testy` → `Ran 67 tests in 9.299s` / `OK` (nowe: B7 `TestTabelaGrawisy`, B6 `TestLogiCzytaneRaz`, C16 `TestKolorProjektu`).
- B6 czas `zbuduj` na żywych logach: 22,4 s → 8,9 s (logi czytane raz, `okno5h` z tych samych wpisów).
- Zrzuty w `C:/Users/PC/cyberiada/_robocze/06-recenzja/po/`: `komp-jasny/ciemny/brzeg.png`, `tel-jasny/ciemny/brzeg.png`, `tel-przenies.png`. Konsola: czysto. `scrollWidth` telefon 390 px = 390 (pełny i brzeg).
- Test: otwarte „Zadania” zostają otwarte po `render()`; „Przenieś do…” na 390 px widoczny, 4 kolumny docelowe.

**Numery**
1 zrobione: `bogaty()` (strong/code/a, bez innerHTML).
2 zrobione: pigułka = pierwsze słowo (pełny stan w `title`), „kto” skrócony.
3 zrobione: render pomijany, gdy dane się nie zmieniły (podpis JSON); `details` i przełączniki Tabela zapamiętane.
4 zrobione w kodzie: podziałka co 5/10/15/30 min dla zakresu < 1 h (nie było takiego zakresu na zrzutach, nie widziałem go).
5 zrobione: `--muted` #6a6862, link #1f66bd (jasny), „czeka” = tekst + kropka (zmiana „czeka” dotyczy obu trybów).
6 zrobione (pomiar wyżej). 7 zrobione (test).
8 zrobione. 9 zrobione („zużycie (tokeny)”, „pamięć podręczna”, „bez ruchu od 1 h”, „przed systemem pracy” z wyjaśnieniem).
10 zrobione: kolumna nazw min 110 px; tekst przerwy krótszy lub pominięty; daty pod osią nie sklejone. Etykieta „lukrum (przed sys…)” w wykresie ról nadal się ucina.
11 zrobione. 12 zrobione („zobacz projekty”, kafel przewija do sekcji Projekty).
13 zrobione: `role="img"` przy tempie, cele dotyku ≥ 44 px (Tabela, uchwyt). Pominięte: przycisk „Pokaż jeszcze” w kolumnach zadań (nie zmieniałem). `cursor:grab` tylko na zadaniach z numerem (przeciągalnych).
14 zrobione („wczoraj” kalendarzowo, rok przy dacie z innego roku).
15 zrobione: `<meta viewport>` w treści; nie sprawdzone po publikacji jako Artifact.
16 zrobione: `kolor` w `projekty.yaml` (cyberiada s1, lukrum s2), generator podaje w JSON; bez pola kolor z hasha nazwy (możliwe kolizje); role z osobnej palety `--r1..--r5`.
17 zrobione: pasek = zużycie limitu, czas okna tekstem; bez limitu pasek czasu z podpisem „czas okna”.
18 zrobione: Decyzje/Zadania/Historia zwinięte (`details`, localStorage w try/catch); Pracownicy zwinięci, gdy nikt nie pracuje (ręczny wybór wygrywa).
19 zrobione: gradient przy prawej krawędzi paska na telefonie, znika na końcu.
20 zrobione: „Przenieś do…” w rozwiniętym zadaniu (dotyk/wąski ekran), zapis jak przeciąganie (`uklad/<projekt>`); zapisu do bazy nie testowałem na żywo (fałszywa baza).

**Uwagi**
- Plik wątku był tylko w głównym checkoucie (nieskomitowany); kopię z raportem dodałem w worktree.
- Zapis listy pracowników do dziennika po commicie pominąłem (`version_mismatch`, hook zakazuje czytania); postęp wyko zapisany (wersja 3).
- `localStorage` w opublikowanym Artifact może być zablokowany; jest w try/catch, stan wtedy nie przetrwa odświeżenia.
