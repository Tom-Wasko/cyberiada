---
name: nowy-projekt
description: Zakłada nowy projekt cyberiady albo dodaje cyberiadę do istniejącego folderu (szablon, git, rejestr, zaufanie, GitHub).
argument-hint: "<nazwa> [ścieżka]"
disable-model-invocation: true
---
Polecenie: `/nowy-projekt $ARGUMENTS`. Szablon: `C:/Users/PC/cyberiada/szablony/projekt/`.

1. Ustal okienkiem (jedno, do 4 pytań): nazwa (identyfikator bez ogonków), jedno zdanie opisu, folder
   (domyślnie `C:/Users/PC/<nazwa>`), repo na GitHubie (prywatne / bez). Odpowiedź „prywatne” to zgoda na nowe repo.
2. Skopiuj szablon do folderu **bez nadpisywania** istniejących plików (istniejący projekt dostaje tylko to,
   czego brakuje). Uzupełnij `CLAUDE.md` i `README.md` (nazwa, opis, polecenia, jeśli znane).
3. `git init -b main` (jeśli nie ma repo), commit: `git -c user.name=Tom-Wasko commit -m "Start projektu"`.
4. Dopisz projekt do `C:/Users/PC/cyberiada/projekty.yaml` (sciezka względem katalogu bazowego komputera,
   gospodarz = nazwa tego komputera), commit w repo cyberiady.
5. Zaufanie folderowi: `python -X utf8 C:/Users/PC/cyberiada/narzedzia/instaluj.py --zaufaj`.
6. Repo: `gh repo create Tom-Wasko/<nazwa> --private --source <folder> --push` (tylko po zgodzie z punktu 1).
7. Powiedz szefowi: w nowym terminalu `archi <nazwa>`.
