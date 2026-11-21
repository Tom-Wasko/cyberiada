# dziennik
Panel stanu wszystkich projektów na claude.ai: https://claude.ai/artifact/5c5LeHX3ohn5qRanw6XyoT
(adres też w `projekty.yaml`, pole `dziennik`). Strona tylko pokazuje dane; źródłem prawdy jest dokumentacja
projektu (`Stan.md`, `Zadania.md`, `Decyzje.md`, `podroze/`), logi sesji (`zuzycie.py`) i git.

## Odświeżenie (robi Archi swojego projektu)
1. Wygeneruj dane:
   `python -X utf8 C:/Users/PC/cyberiada/narzedzia/dziennik/generuj.py --projekt <nazwa>`
   (zapisuje `C:/Users/PC/cyberiada/_robocze/dziennik/<nazwa>.json`).
2. Zapisz je do bazy strony narzędziem ArtifactData: `set`, url jak wyżej, collection `projekty`,
   doc_id `<nazwa>`, file_path ten JSON. Dokument już istnieje, więc najpierw `get` i podaj `if_version`.
3. W `Stan.md` wpisz puls: `Archi żył: RRRR-MM-DD GG:MM`.

Każdy Archi zapisuje tylko dokument swojego projektu. Strony nie publikuje się ponownie przy odświeżeniu.

## Pytania do szefa
Sekcja „Czeka na szefa” w `Stan.md`; strona pokazuje je w „Czeka na Ciebie” z przyciskiem Kopiuj
(kopiuje np. `cyberiada P1: A`, szef wkleja to w czat Archiego):
```
- P1: Treść pytania?
  - A: opcja (rekomendowane)
  - B: opcja
- Zwykła sprawa bez opcji (bez przycisku).
```

## Pliki
- `generuj.py`: składa JSON projektu (schemat: `dokumentacja/podroze/01-dziennik/watek-generator.md`).
- `strona.html`: strona (baza `db`, kolekcja `projekty`; strona tylko czyta, zapisuje admin).
- `testy/`: `python -X utf8 -m unittest discover -s narzedzia/dziennik/testy`.
