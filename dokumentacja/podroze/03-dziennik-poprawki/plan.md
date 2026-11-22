# Podróż 03: dziennik-poprawki
Start: 2026-11-22 · tryb: nadzorowany · gałąź: `main`
Zadania: Z4

## Kontekst
Lista uwag szefa do dziennika (22.11): dane nie są na żywo, „Czeka na Ciebie” jest za długie (26 starych spraw
z lukrum), „Pomocnik” ma się nazywać „pomo”, Fable zjada tokeny i ginie w innych rolach, zadania nie przechodzą
do „W toku”, kryteria się nie odhaczają, wykres „Wątki” nie działa, formularz odpowiedzi do usunięcia, strona
zbyt czarno-biała. Jedna lista = jedno zadanie Z4.

Odpowiedzi szefa (do `Decyzje.md`, sekcja szefa):
- wygląd: kolor projektu (pasek i nagłówek karty, kolorowe kafle, kolorowe etykiety stanów); tło jasne;
- na żywo: po każdym commicie każdy wyko i Archi zapisuje postęp, pilnuje hook;
- „Czeka na Ciebie”: zwinięta na start, rozwija się sama tylko, gdy pojawi się coś nowego.

## Przyczyny (z rozpoznania)
- Wątki: `generuj.py` czyta kolumny tabeli po numerze; plan lukrum ma dodatkową kolumnę „Zakres”, więc „stan”
  dostaje listę plików, gałąź pusta, start tylko data (słupki zerowej długości).
- Zadania: generator bierze tylko sekcję „W toku”; nikt tam nie przenosi zadań podróży. Podpunkty `### Ważne`
  doklejają się do zadania przed nimi.
- Kryteria: odhacza je tylko Archi przy końcu podróży; brak zasady „odhacz po dowodzie”.
- `tryb` pusty: regex szuka `tryb:`, plan lukrum ma `tryb nadzorowany`.
- Fable: wpisy zużycia mają pole `model`, generator go nie używa.

## Wątki
| Wątek | Kto | Plik | Stan |
|---|---|---|---|
| 03/strona | wyko | watek-strona.md | scalone 22.11 |
| 03/zywo | Archi | (bez pliku) | gotowe; czeka próba w nowej sesji wyko |

Pliki: 03/strona: `narzedzia/dziennik/generuj.py`, `strona.html`, `testy/`; 03/zywo: `narzedzia/dziennik/hook_commit.py` (nowy), `narzedzia/wyko.py`, `narzedzia/archi.py`, `role/`, `skille/podroz`, README dziennika.

### 03/strona (wyko)
1. Generator: tabele czytane po nazwach kolumn (Wątek, Kto, Stan, Gałąź, Plik); gałąź domyślna
   `worktree-podroz-NN-<nazwa>`; start wątku = pierwszy commit gałęzi (albo dodanie pliku wątku), z godziną;
   `scalono` też ze stanu „scalone”. `tryb` z `tryb:` i `tryb `. Punkty listy kończą się na nagłówku `###`.
2. Zadania podróży z nagłówka planu (`Zadania: Z29, Z30…`) idą do „W toku” (usunięte z „Zaplanowane”).
3. Rola `Fable` z modelu (`fable` w nazwie), przed podziałem Archi/wyko/pomo; „Pomocnik” → „pomo”.
4. Strona: „Czeka na Ciebie” zwinięta z licznikiem; strona pamięta widziane sprawy (localStorage) i rozwija
   się sama tylko przy nowych, oznaczonych „nowe”. Bez przycisków Kopiuj i opcji do klikania: sama lista pytań
   (opcje jako zwykły tekst, rekomendowana wyróżniona).
5. Kolor projektu: pasek i nagłówek karty, kafle przeglądu, etykiety stanów wątków (w toku, scalone, czeka),
   paleta sprawdzona `validate_palette.js` dla jasnego i ciemnego.
6. Postęp na żywo: strona czyta też kolekcję `postep` (doc na sesję: projekt, wątek, rola, krok, commity, czas)
   i pokazuje przy wątku „ostatnio: <krok>, 5 min temu”; wątek bez postępu > 1 h oznaczony „cisza”.
7. Testy generatora na przypadkach z lukrum (dodatkowa kolumna, `###`, Fable).

### 03/zywo (Archi)
1. `hook_commit.py`: hook PostToolUse (Bash) — po udanym `git commit` wypisuje gotową instrukcję zapisu postępu
   (ArtifactData `set`, kolekcja `postep`, dane wyliczone przez skrypt z gita); dla Archiego także
   `generuj.py` + zapis dokumentu projektu. Przy konflikcie wersji ponowny zapis z wersją z błędu.
2. Hook podpięty tylko w sesjach wyko i Archi przez `--settings` w `wyko.py` i `archi.py` (bez zmiany
   globalnych `settings.json`).
3. Zasady w roli Archiego i `/podroz`: przy starcie podróży zadania do „W toku”; kryterium odhaczone od razu
   po dowodzie (po scaleniu wątku), potem odświeżenie.
4. Próba: czy sesja wyko w tle ma narzędzie ArtifactData (wynik do `wiedza/testy.md`). Jeśli nie — wyko nie
   zapisuje, postęp wyko z jego commitów zapisuje Archi przy swoim odświeżeniu; mówię szefowi od razu.

## Kryteria sukcesu
- [x] Wykres „Wątki” lukrum pokazuje 4 wątki ze stanem, gałęzią i słupkami (zrzut lub odczyt strony).
- [x] Z29, Z30, Z1, Z31, Z34 lukrum w „W toku”; brak `###` w treści zadań (JSON).
- [x] W „Kto zużywa” osobna rola Fable; brak „Pomocnik” na stronie (grep).
- [x] „Czeka na Ciebie” zwinięta, bez przycisków; nowa sprawa ją rozwija (próba na kopii danych).
- [x] Kolory projektu; walidator palety PASS (jasny i ciemny).
- [ ] Commit w sesji wyko/Archi daje wpis w `postep` widoczny na stronie bez ręcznego odświeżania.
- [x] Testy: `python -X utf8 -m unittest discover -s narzedzia/dziennik/testy` — ostatnie linie.

## Kroki
1. Plan podróży 03 w `dokumentacja/podroze/03-dziennik-poprawki/`, Z4 w Zadaniach (W toku), Decyzje, Stan, commit.
2. Brief `watek-strona.md`, commit, start wyko.
3. 03/zywo równolegle (pliki rozłączne).
4. Przegląd, scalenie do `main`, ponowne opublikowanie strony pod tym samym adresem, odświeżenie danych
   cyberiady i lukrum, sprawdzenie w przeglądarce (telefon i komputer).
5. Uwaga dla szefa: 24 pytania lukrum to stare sprawy z dawnego „Do decyzji” (przeniesione przy migracji);
   przy nowej logice nie będą się rozwijać same.

## Podsumowanie
