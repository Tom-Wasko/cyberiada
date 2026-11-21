# Podróż 01: dziennik
Start: 2026-11-21 · tryb: hejo · gałąź: `main`

## Cel
Jedna strona na claude.ai ze stanem wszystkich projektów i rzeczami, które czekają na szefa, czytelna na telefonie
i komputerze. Źródłem prawdy zostaje dokumentacja projektów, logi sesji i git; dziennik tylko je pokazuje.

## Kryteria sukcesu (zatwierdzone przez szefa)
- [x] `python -X utf8 narzedzia/dziennik/generuj.py --projekt cyberiada` tworzy JSON zgodny ze schematem;
      testy `python -X utf8 -m unittest discover -s narzedzia/dziennik/testy` przechodzą (dowód: ostatnie linie).
- [x] Strona opublikowana jako Artifact, adres w `projekty.yaml` (`dziennik:`).
- [x] Po zapisie danych przez ArtifactData strona pokazuje cyberiadę: puls, podróż 01 i wątki, pytania z
      „Czeka na szefa” z przyciskiem kopiuj, decyzje, zadania, 5 wykresów (zrzut na 390 px i 1280 px).
- [x] Odświeżenie dziennika to jedno polecenie + jeden zapis ArtifactData, opisane w `narzedzia/dziennik/README.md`.
- [x] Ściągawka w `README.md` i szablon `Stan.md` (format pytań) zaktualizowane.

## Wątki
| Wątek | Kto | Plik | Stan |
|---|---|---|---|
| generator | wyko | `watek-generator.md` | scalono 2026-11-21 |
| strona | Archi | (bez pliku) | gotowe 2026-11-21 |

## Podsumowanie
Koniec: 2026-11-21. Szef obejrzał stronę i ją zatwierdził („jest ok, działa”).

- Zrobione: generator `narzedzia/dziennik/generuj.py` (17 testów, `Ran 17 tests … OK`), strona `strona.html`
  opublikowana (https://claude.ai/artifact/5c5LeHX3ohn5qRanw6XyoT) z bazą `db`, opis odświeżania
  `narzedzia/dziennik/README.md`, ściągawka, szablon `Stan.md`, adres w `projekty.yaml`.
- Zrzuty 390/1280 px i test przycisku Kopiuj: przeglądarka nie działała („No group with id”), stronę sprawdził
  szef na swoich urządzeniach. Dane testowe `projekty/przyklad` usunięte z bazy.
- Odłożone: nic.
- Koszt (`zuzycie.py --projekt . --od 2026-11-21`, ważone tokeny): archi-cyberiada 3 740 681,
  wyko-cyberiada-01-generator 845 242; razem z próbami 4 596 783.
