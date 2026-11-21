# cyberiada

System pracy z Claude Code dla wszystkich projektów szefa: kto co robi, jak przebiega praca, gdzie leży stan.
Nazwy z Lema: **Archi** (kierownik projektu), **wyko** (wykonawca w tle), **Pomocnik** (każdy zwykły czat),
**podróż** (praca od celu do scalenia), **dziennik** (panel stanu na claude.ai).

## Ściągawka poleceń

**W terminalu (PowerShell):**

| Polecenie | Co robi |
|---|---|
| `archi` | lista projektów tego komputera (w folderze projektu: otwiera jego Archiego) |
| `archi <projekt>` | otwiera czat Archiego projektu, a jeśli już był, wznawia go (Opus, Remote Control) |
| `archi <projekt> hejo` | to samo i od razu tryb nadzorowany (`/hejo`) |
| `archi <projekt> papa 4h` | to samo i od razu tryb autonomiczny (`/papa`) z budżetem |
| `claude` | zwykły czat: Pomocnik (Sonnet), do drobnych spraw w dowolnym folderze |
| `claude agents` | lista sesji w tle (wyko); `claude attach <id>` podgląd i rozmowa z wyko |
| `python -X utf8 C:/Users/PC/cyberiada/narzedzia/zuzycie.py [--projekt <folder>] [--od RRRR-MM-DD]` | zużycie tokenów według sesji |
| `python -X utf8 C:/Users/PC/cyberiada/narzedzia/dziennik/generuj.py --projekt <nazwa>` | dane projektu do dziennika (Archi zapisuje je na stronę: `narzedzia/dziennik/README.md`) |
| `.\zainstaluj.ps1 [-Sprawdz]` | instalacja albo sprawdzenie cyberiady na tym komputerze |

**W czacie Archiego** (z komputera albo z telefonu; każde działa też zwykłym tekstem, np. „papa 4h”):

| Polecenie | Co robi |
|---|---|
| `/podroz [temat]` | nowa podróż: cel, kryteria sukcesu, wątki (w trybie nadzorowanym przez plan do zatwierdzenia) |
| `/podroz koniec` | domknięcie: scalenie, dokumentacja, porządek, gotowe `/compact` dla szefa |
| `/podroz porzuc` | porzucenie podróży (gałęzie zostają, wątki trafiają do zadań) |
| `/hejo` | „jestem”, włącza **tryb nadzorowany**: podsumowanie pracy pod nieobecność, czekające pytania okienkiem, scalenie do `main` |
| `/papa <budżet>` | „wychodzę”, włącza **tryb autonomiczny**: praca bez szefa; budżet `4h`, `do 18:00`, `2M` (tokeny) albo `do skończenia X` |
| `/wznow` | po restarcie komputera albo po limicie: odtworzenie stanu z plików, wznowienie wyko |

**W dowolnym czacie:** `/nowy-projekt <nazwa>` zakłada projekt (szablon, git, rejestr, zaufanie, GitHub).

Zwykłe polecenia Claude Code przydatne codziennie: `/compact <co zachować>`, `/rewind` (cofnięcie złej ścieżki),
`/btw` (pytanie poboczne bez zaśmiecania rozmowy), `/effort high` (dokładniej, drożej), `/context` (zajętość).

## Jak to działa w skrócie
- **Pomocnik**: każdy czat bez roli. Zasady wspólne (`zasady/baza.md`) i preferencje szefa
  (`zasady/preferencje.md`) wczytują się same w każdym folderze.
- **Archi**: jeden czat na projekt (`archi-<projekt>`). Rozmawia z szefem, planuje podróże, część robi sam,
  obszerne wątki zleca wyko, przegląda, scala, pisze dokumentację, odświeża dziennik. Rola: `role/archi.md`.
- **wyko**: sesja w tle na jeden wątek (`narzedzia/wyko.py`), Sonnet, własny worktree i gałąź, bez push i sieci.
  Brief i raport w jednym pliku wątku. Rola: `role/wyko.md`, uprawnienia: `narzedzia/wyko/ustawienia.json`.
- **agenci**: tylko `zwiadowca` (Haiku, zwiad) i `recenzent` (Sonnet, świeże oko). Wbudowane Explore, Plan
  i general-purpose są zablokowane (drogie).
- **Tryby:** nadzorowany (polecenie `/hejo`: szef odpowiada od razu, okienka, scalanie do `main`) i autonomiczny
  (polecenie `/papa`: szef z telefonu przez
  Remote Control, pytania tekstem + push, scalanie do gałęzi `podroz-NN`, nic nieodwracalnego).
- **Numery** (te same w każdym projekcie): zadanie `Z7`, podróż `01`, wątek `01/generator`.
- **Stan** zawsze w plikach projektu: `dokumentacja/Stan.md` (teraz), `Zadania.md`, `Decyzje.md`,
  `podroze/NN-temat/` (plan i wątki).

## Mapa repozytorium
```
zasady/        baza.md, preferencje.md – wczytywane zawsze (~/.claude/rules → tu)
role/          archi.md, wyko.md – dopisywane do promptu systemowego przy starcie
skille/        podroz, hejo, papa, wznow, nowy-projekt (~/.claude/skills/<nazwa> → tu)
agenci/        zwiadowca, recenzent (~/.claude/agents → tu)
szablony/      projekt/ (nowy projekt), watek.md, plan-podrozy.md
narzedzia/     archi.py + bin/archi.cmd, wyko.py, zuzycie.py, instaluj.py, cdp.py i zrzuty.py (zrzuty ekranu), dziennik/ (panel stanu)
dokumentacja/  stan, zadania, decyzje i podróże samej cyberiady (jest też projektem); wiedza/: testy.md
               (co sprawdzono w praktyce) i notatki ze źródłami
projekty.yaml  rejestr projektów i komputerów
skrzynka.md    spostrzeżenia o szefie do przejrzenia (nie wczytywana na starcie)
```

## Instalacja na nowym komputerze
1. Claude Code, git, Python 3.10+, GitHub CLI (`gh auth login`).
2. `git clone https://github.com/Tom-Wasko/cyberiada C:/Users/PC/cyberiada` (prywatne repo).
3. W `projekty.yaml` dopisz komputer: `NAZWA-KOMPUTERA: <katalog bazowy>` (nazwa: `$env:COMPUTERNAME`).
4. `.\zainstaluj.ps1`, potem nowy terminal. Sprawdzenie w każdej chwili: `.\zainstaluj.ps1 -Sprawdz`.

Instalator jest idempotentny i robi kopie zapasowe: dowiązania do `~/.claude`, ustawienia (Sonnet medium,
tryb auto, blokada drogich agentów, bez dopisków AI w commitach, bez goal check-inów), zaufanie folderom
projektów, `archi` w PATH. Aktualizacja systemu: `git pull` w tym folderze (dowiązania działają od razu).
