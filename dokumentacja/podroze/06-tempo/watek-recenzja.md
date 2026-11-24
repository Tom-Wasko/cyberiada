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
