"""Testy filtra projektu w narzedzia/zuzycie.py (nazwa albo folder, worktree, bez podobnych nazw)."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import zuzycie  # noqa: E402


def sesja(katalog: Path, nazwa: str, cwd: str) -> None:
    folder = katalog / nazwa
    folder.mkdir(parents=True)
    wpis = {"type": "assistant", "cwd": cwd, "timestamp": "2026-11-23T10:00:00Z", "requestId": nazwa,
            "message": {"id": nazwa, "model": "claude-sonnet-5-5",
                        "usage": {"input_tokens": 10, "output_tokens": 1}}}
    (folder / "s.jsonl").write_text(json.dumps({"type": "custom-title", "customTitle": nazwa}) + "\n"
                                    + json.dumps(wpis) + "\n", encoding="utf-8")


class TestFiltrProjektu(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.projekt = self.tmp / "lukrum"
        (self.projekt / ".claude" / "worktrees" / "w").mkdir(parents=True)
        sesja(self.tmp / "sesje", "archi", str(self.projekt))
        sesja(self.tmp / "sesje", "wyko", str(self.projekt / ".claude" / "worktrees" / "w"))
        sesja(self.tmp / "sesje", "obcy", str(self.tmp / "lukrum2"))

    def nazwy(self, projekt: Path) -> set[str]:
        return {w["sesja"] for w in zuzycie.wpisy(projekt, self.tmp / "sesje")}

    def test_folder_z_worktree_bez_podobnych_nazw(self) -> None:
        self.assertEqual(self.nazwy(self.projekt), {"archi", "wyko"})

    def test_ukosniki_w_przod(self) -> None:
        self.assertEqual(self.nazwy(Path(self.projekt.as_posix() + "/")), {"archi", "wyko"})

    def test_nazwa_z_rejestru(self) -> None:
        stare = zuzycie.projekty
        zuzycie.projekty = lambda: {"lukrum": self.projekt}
        try:
            self.assertEqual(zuzycie.folder_projektu("lukrum"), self.projekt)
            self.assertEqual(zuzycie.folder_projektu(str(self.tmp)), self.tmp)
        finally:
            zuzycie.projekty = stare


if __name__ == "__main__":
    unittest.main()
