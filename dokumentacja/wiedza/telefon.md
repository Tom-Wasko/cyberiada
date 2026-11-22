# Telefon: Remote Control, powiadomienia, artefakty

Sprawdzone: 2026-11-22

## Remote Control (sterowanie sesją z telefonu)
- Co to: aplikacja Claude (iOS/Android) albo claude.ai/code łączy się z sesją Claude Code działającą na komputerze.
  Kod i pliki zostają na komputerze, telefon jest „oknem”. Źródło: https://code.claude.com/docs/en/remote-control
- Start: `claude --remote-control` (`--rc`) dla sesji interaktywnej, `/remote-control` w trwającej sesji, `claude remote-control`
  dla trybu serwera (do 32 sesji naraz). Źródło: https://code.claude.com/docs/en/remote-control
- Wymagania: plan Pro, Max, Ultra, Team lub Enterprise, logowanie `/login` (nie klucz API). Nie działa na Bedrock, Vertex, Foundry.
  Źródło: https://code.claude.com/docs/en/remote-control
- Z telefonu: wiadomości, załączniki (zdjęcia, pliki), zmiana modelu i `/effort`, tryby uprawnień (Manual, Accept edits, Plan, Auto;
  bez Bypass), podgląd subagentów. Polecenia tylko terminalowe (np. `/plugin`, `/resume`) nie działają.
  Źródła: https://code.claude.com/docs/en/remote-control , https://code.claude.com/docs/en/mobile
- Ograniczenia: komputer musi być włączony, a proces `claude` uruchomiony; po Ctrl+C w trybie serwera sesje da się wznowić ok. 4 godziny
  (`--continue`). Źródło: https://code.claude.com/docs/en/remote-control
- Na tym komputerze: sesja `archi-cyberiada` w aplikacji działa, okienko pytań z telefonu działa (`testy.md`, T2, T3).
  Zgody i pytania `AskUserQuestion` według dokumentacji tylko w streszczeniu strony, niezweryfikowane; potwierdza je T3.
- Sesje w tle (`--bg`) na telefonie: w dokumentacji **nie znaleziono** potwierdzenia, że da się je podejrzeć (strona opisuje tylko
  subagenty wewnątrz połączonej sesji). Do sprawdzenia próbą.

## Powiadomienia push
- Przy aktywnym Remote Control Claude może wysłać push po zakończeniu zadania albo gdy potrzebuje decyzji; można o to poprosić w prompcie.
  Źródło: https://code.claude.com/docs/en/remote-control (sekcja „Mobile push notifications”)
- Włączenie: aplikacja zainstalowana, to samo konto, zgoda systemu na powiadomienia, potem `/config` → „Push when Claude decides”
  i/lub „Push when actions required”. Błąd „No mobile registered”: otwórz aplikację, by odświeżyć token.
  Źródło: https://code.claude.com/docs/en/remote-control
- Osobnej strony o powiadomieniach nie ma (https://code.claude.com/docs/en/notifications → 404).

## Artefakty claude.ai w telefonie
- W aplikacji iOS/Android artefakty widać w zakładce Artifacts i można je edytować; zmiana udostępniania wymaga weba lub Desktopa.
  Wymagana opcja „Cloud code execution and file creation”. Źródło: https://support.claude.com/en/articles/9487310-what-are-artifacts-and-how-do-i-use-them
- Artefakt z Claude Code to prywatna żywa strona pod adresem URL (plany Pro/Max/Ultra/Team/Enterprise, `/login`).
  Źródło: https://code.claude.com/docs/en/artifacts
- Zapis danych w artefakcie (limit domyślny 100 MB i 25 000 dokumentów) jest opisany dla „Claude on the web and Claude Desktop”;
  o telefonie artykuł milczy. Czy dziennik z bazą działa w telefonie: do sprawdzenia próbą.
  Źródło: https://support.claude.com/en/articles/17153992-what-are-artifacts-and-how-do-i-use-them
- Obsługa JavaScriptu w artefaktach w aplikacji mobilnej: nie opisana, **nie znaleziono**.
