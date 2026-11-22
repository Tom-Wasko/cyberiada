# Podróż 04: reszta
Start: 2026-11-22 · tryb: nadzorowany · gałąź: `main`
Zadania: Z1, Z3

## Kontekst
Po podróży 03 w cyberiadzie zostały: Z1 (testy T4–T6, czekają od T2) i Z3 (notatki ze źródłami w
`dokumentacja/wiedza/`). Szef: „zajmijmy się resztą”, wybrał podróż 04 z Z1 + Z3: Archi robi T5 i T6 sam,
prowadzi szefa przez T4, Z3 pisze jeden wyko w tle ze źródłami z sieci (ok. 1–2 mln tokenów).

## Wątki
| Wątek | Kto | Pliki | Stan |
|---|---|---|---|
| 04/testy | Archi | `dokumentacja/wiedza/testy.md` | w toku |
| 04/wiedza | wyko | `dokumentacja/wiedza/{tokeny,telefon,claude-code}.md` | w toku |

### 04/testy (Archi, Z1)
- **T4 skille z telefonu:** szef w czacie Remote Control na telefonie pisze `/hejo` (albo `hejo`) do
  archi-cyberiada; sprawdzam, czy skill się uruchomił (wpis „Tryb: nadzorowany” w Stan.md). Jedna wiadomość szefa.
- **T5 narzut startu zwiadowcy:** jedno krótkie wywołanie agenta `zwiadowca` (pytanie na 1 polecenie), koszt
  pierwszej tury z jego logu (`subagents/*.jsonl`, `narzedzia/zuzycie.py` → `czytaj`). Porównanie z 47,6k wyko.
- **T6 % limitu ze statusline:** sprawdzić w dokumentacji code.claude.com (statusline: jakie pola JSON dostaje
  skrypt, czy jest limit 5 h) + próba na tym komputerze; wynik: da się / nie da się i jak.
- Wyniki do tabeli w `testy.md` (T4–T6 ✓/✗ + jedno zdanie, źródło).

### 04/wiedza (wyko, Z3)
Brief: trzy krótkie notatki (każda do ~1 strony, prosty język, każde twierdzenie z odnośnikiem do źródła,
data sprawdzenia):
1. `tokeny.md`: jak liczą się tokeny i koszt (cache odczyt/zapis, modele, limit 5 h i tygodniowy, co zjada
   kontekst: start sesji, agenci, skille), praktyczne zasady oszczędzania; zgodność z `narzedzia/zuzycie.py` (wagi).
2. `telefon.md`: Remote Control, powiadomienia push, dziennik na claude.ai w telefonie — co działa, ograniczenia.
3. `claude-code.md`: funkcje używane przez cyberiadę (sesje w tle `--bg`, worktree `-w`, hooki, `--settings`,
   skille, agenci, auto mode, artefakty z bazą) — co robią, odnośnik do docs, gdzie używamy.
Wyko tylko czyta i pisze te 3 pliki; nic nie zmienia w kodzie. Gdy źródło sprzeczne z testami w `testy.md`, zapisuje
to jako uwagę, nie rozstrzyga.

## Kryteria sukcesu
- [ ] T4, T5, T6 w `testy.md` z wynikiem i dowodem (liczba tokenów / źródło / odpowiedź z telefonu).
- [ ] 3 notatki w `dokumentacja/wiedza/`, każde twierdzenie z odnośnikiem, data sprawdzenia; przegląd Archiego.
- [ ] README (mapa repo) wymienia nowe notatki.
- [ ] Z1 i Z3 skreślone; podsumowanie z tabelą zrobione / następnie / reszta.

## Kroki
1. `podroze/04-reszta/plan.md`, Z1+Z3 do „W toku”, Stan, commit, push.
2. `watek-wiedza.md` (brief jak wyżej), commit, `wyko.py`.
3. Równolegle 04/testy: T5, T6 sam; T4 — proszę szefa o jedną wiadomość z telefonu.
4. Przegląd notatek, scalenie do `main`, kryteria, `/podroz koniec`.

## Sprawdzenie
- `git diff` notatek: odnośniki są (grep `https://`), brak twierdzeń bez źródła.
- Testy dziennika nadal OK (`python -X utf8 -m unittest discover -s narzedzia/dziennik/testy`).
- Dziennik pokazuje podróż 04, wątki i pracowników.

## Podsumowanie
