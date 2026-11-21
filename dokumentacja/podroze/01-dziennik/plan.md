# Podróż 01: dziennik
Start: 2026-11-21 · tryb: hejo · gałąź: `main`

## Cel
Jedna strona na claude.ai ze stanem wszystkich projektów i rzeczami, które czekają na szefa, czytelna na telefonie
i komputerze. Źródłem prawdy zostaje dokumentacja projektów, logi sesji i git; dziennik tylko je pokazuje.

## Kryteria sukcesu (zatwierdzone przez szefa)
- [ ] `python -X utf8 narzedzia/dziennik/generuj.py --projekt cyberiada` tworzy JSON zgodny ze schematem;
      testy `python -X utf8 -m unittest discover -s narzedzia/dziennik/testy` przechodzą (dowód: ostatnie linie).
- [ ] Strona opublikowana jako Artifact, adres w `projekty.yaml` (`dziennik:`).
- [ ] Po zapisie danych przez ArtifactData strona pokazuje cyberiadę: puls, podróż 01 i wątki, pytania z
      „Czeka na szefa” z przyciskiem kopiuj, decyzje, zadania, 5 wykresów (zrzut na 390 px i 1280 px).
- [ ] Odświeżenie dziennika to jedno polecenie + jeden zapis ArtifactData, opisane w `narzedzia/dziennik/README.md`.
- [ ] Ściągawka w `README.md` i szablon `Stan.md` (format pytań) zaktualizowane.

## Wątki
| Wątek | Kto | Plik | Stan |
|---|---|---|---|
| generator | wyko | `watek-generator.md` | w toku |
| strona | Archi | (bez pliku) | w toku |

## Podsumowanie
<!-- Na końcu: co zrobione, co odłożone (→ Zadania.md), koszt (narzedzia/zuzycie.py). -->
