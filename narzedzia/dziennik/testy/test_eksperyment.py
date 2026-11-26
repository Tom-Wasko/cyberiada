"""Testy narzędzia eksperymentu Z10 (plan, stopy, wyniki, przebieg z udawanymi claude i git, raport)."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

EKS = Path(__file__).resolve().parents[2] / "eksperyment"
sys.path.insert(0, str(EKS))
sys.path.insert(0, str(EKS.parent))
import raport  # noqa: E402
import uruchom  # noqa: E402

ZADANIA = [
    {"id": "a", "wielkosc": "male", "projekt": "x", "repo": "r", "start": "s", "wzorzec": "w", "plik_watku": "p",
     "python": "python", "testy_cwd": ".", "testy": ["{python}", "-m", "unittest"], "oryginal": {"wazone_mln": 1.0}},
    {"id": "b", "wielkosc": "duze", "projekt": "x", "repo": "r", "start": "s", "wzorzec": "w", "plik_watku": "p",
     "python": "python", "testy_cwd": ".", "testy": ["{python}", "-m", "unittest"], "oryginal": {"wazone_mln": 2.0}},
]
PLAN = {"grupy": [
    {"opis": "g1", "zadania": ["wszystkie"], "modele": ["sonnet"], "effort": ["low", "high"], "powtorzenie": 1},
    {"opis": "g2", "zadania": ["duze"], "modele": ["opus"], "effort": ["medium"], "autocompact": ["120k"]},
    {"opis": "g3 (powtórka g1)", "zadania": ["wszystkie"], "modele": ["sonnet"], "effort": ["low"], "powtorzenie": 1},
]}


class TestPlan(unittest.TestCase):
    def test_rozwija_kolejnosc_bez_duplikatow(self) -> None:
        ids = [p["id"] for p in uruchom.rozwin_plan(PLAN, ZADANIA)]
        self.assertEqual(ids, ["a-sonnet-low-200k-p1", "a-sonnet-high-200k-p1", "b-sonnet-low-200k-p1",
                               "b-sonnet-high-200k-p1", "b-opus-medium-120k-p1"])

    def test_male_i_duze(self) -> None:
        p = uruchom.rozwin_plan({"grupy": [{"zadania": ["male"], "modele": ["haiku"], "effort": ["low"]}]}, ZADANIA)
        self.assertEqual([x["zadanie"] for x in p], ["a"])
        self.assertEqual(p[0]["wielkosc"], "male")

    def test_pliki_planu_i_zadan_sa_spojne(self) -> None:
        zadania = json.loads((EKS / "zadania.json").read_text(encoding="utf-8"))["zadania"]
        self.assertEqual({z["wielkosc"] for z in zadania}, {"male", "duze"})
        self.assertEqual(sum(z["wielkosc"] == "male" for z in zadania), 2)
        for z in zadania:
            for k in ("start", "wzorzec", "plik_watku", "testy", "uzasadnienie", "repo"):
                self.assertTrue(z.get(k), (z["id"], k))
        for nazwa in ("plan.json", "plan-proba.json"):
            plan = json.loads((EKS / nazwa).read_text(encoding="utf-8"))
            self.assertTrue(uruchom.rozwin_plan(plan, zadania), nazwa)

    def test_szacunek_zalezy_od_modelu_i_effortu(self) -> None:
        z = ZADANIA[0]
        s = lambda m, e: uruchom.szacunek({"model": m, "effort": e}, z)  # noqa: E731
        self.assertLess(s("haiku", "low"), s("sonnet", "low"))
        self.assertLess(s("sonnet", "low"), s("sonnet", "high"))
        self.assertLess(s("sonnet", "high"), s("opus", "high"))


class TestStopy(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.plik = self.tmp / "limit.json"
        self.teraz = datetime(2026, 11, 28, 12, 0, tzinfo=timezone.utc)
        self.do = datetime(2026, 11, 29, 16, 0, tzinfo=timezone.utc)

    def limit(self, uzyte: int, wiek_min: int, reset: float = 0) -> None:
        czas = (self.teraz - timedelta(minutes=wiek_min)).isoformat()
        self.plik.write_text(json.dumps({"five_hour": {"used": 10, "resets_at": reset},
                                         "seven_day": {"used": uzyte, "resets_at": 1}, "czas": czas}), encoding="utf-8")

    def stop(self, wyniki=None, budzet=45e6) -> str | None:
        return uruchom.powod_stopu(wyniki or [], budzet, self.do, self.teraz, self.plik)

    def test_brak_stopu(self) -> None:
        self.assertIsNone(self.stop())

    def test_budzet_liczy_przebiegi_i_oceny(self) -> None:
        wyniki = [{"tokeny_wazone": 1_000_000, "ocena_wazone": 500_000}, {"tokeny_wazone": 500_000}]
        self.assertIsNone(self.stop(wyniki, budzet=2_100_000))
        self.assertIn("budżet", self.stop(wyniki, budzet=2_000_000))

    def test_limit_tygodnia_tylko_gdy_plik_swiezy(self) -> None:
        self.limit(95, 5)
        self.assertIn("limit tygodnia", self.stop())
        self.limit(94, 5)
        self.assertIsNone(self.stop())
        self.limit(99, 16)  # nieświeży: ignorowany
        self.assertIsNone(self.stop())

    def test_brak_pliku_limitu(self) -> None:
        self.assertIsNone(self.stop())

    def test_termin(self) -> None:
        self.teraz = self.do
        self.assertIn("termin", self.stop())

    def test_reset_5h_z_pliku_albo_15_min(self) -> None:
        self.limit(10, 1, reset=self.teraz.timestamp() + 600)
        self.assertEqual(uruchom.sekundy_do_resetu(self.plik, self.teraz), 660)
        self.limit(10, 1, reset=self.teraz.timestamp() - 5)  # reset w przeszłości
        self.assertEqual(uruchom.sekundy_do_resetu(self.plik, self.teraz), 900)
        self.limit(10, 30, reset=self.teraz.timestamp() + 600)  # nieświeży plik
        self.assertEqual(uruchom.sekundy_do_resetu(self.plik, self.teraz), 900)

    def test_rozpoznanie_limitu_5h(self) -> None:
        self.assertTrue(uruchom.to_limit_5h({"is_error": True, "result": "5-hour limit reached ∙ resets 3pm"}, ""))
        self.assertTrue(uruchom.to_limit_5h({"is_error": True, "api_error_status": 429, "result": "x"}, ""))
        self.assertFalse(uruchom.to_limit_5h({"is_error": False, "result": "Zwiększyłem limit w kodzie"}, ""))
        self.assertFalse(uruchom.to_limit_5h({"is_error": True, "result": "inny błąd"}, ""))

    def test_budzet_z_tekstu(self) -> None:
        self.assertEqual(uruchom.parsuj_budzet("45M"), 45_000_000)
        self.assertEqual(uruchom.parsuj_budzet("2m"), 2_000_000)
        self.assertEqual(uruchom.parsuj_budzet("1,5M"), 1_500_000)


class TestPomocnicze(unittest.TestCase):
    def test_brief_bez_raportu(self) -> None:
        tekst = "# Wątek\n\n## Brief\n- cel\n- gotowe\n\n## Raport\nzrobione\n"
        self.assertEqual(uruchom.brief_z_tekstu(tekst), "- cel\n- gotowe")

    def test_ocena(self) -> None:
        self.assertEqual(uruchom.parsuj_ocene('Oto: {"ocena": 4, "uzasadnienie": "ok"}'), (4, "ok"))
        self.assertIsNone(uruchom.parsuj_ocene('{"ocena": 7, "uzasadnienie": "x"}'))
        self.assertIsNone(uruchom.parsuj_ocene("brak"))

    def test_wyniki_testow(self) -> None:
        pyt = uruchom.policz_testy(1, "x\n2 failed, 40 passed in 3s", False)
        self.assertFalse(pyt["zaliczone"])
        self.assertEqual((pyt["liczby"]["zaliczone"], pyt["liczby"]["niezaliczone"]), (40, 2))
        uni = uruchom.policz_testy(0, "Ran 17 tests in 0.1s\n\nOK", False)
        self.assertTrue(uni["zaliczone"])
        self.assertEqual(uni["liczby"]["uruchomione"], 17)
        self.assertFalse(uruchom.policz_testy(0, "Ran 1 tests\n\nOK", True)["zaliczone"])

    def test_odpowiedz_json_ostatnia_linia(self) -> None:
        self.assertEqual(uruchom.parsuj_odpowiedz('szum\n{"a": 1}\n'), {"a": 1})
        self.assertIsNone(uruchom.parsuj_odpowiedz("nie json"))

    def test_katalog_w_repo_odrzucony(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        (tmp / ".git").mkdir()
        self.assertTrue(uruchom.w_repo(tmp / "x"))
        self.assertTrue(uruchom.w_repo(Path.home() / "cyberiada" / "x"))
        self.assertFalse(uruchom.w_repo(Path(tempfile.mkdtemp()) / "x"))

    def test_polecenie_uzywa_wspolnych_flag_wyko(self) -> None:
        from wyko import wspolne_flagi
        self.assertIs(uruchom.wspolne_flagi, wspolne_flagi)

    def test_polecenie_testow_podstawia_python(self) -> None:
        z = dict(ZADANIA[0], python="C:/venv/python.exe")
        self.assertEqual(uruchom.polecenie_testow(z), ["C:/venv/python.exe", "-m", "unittest"])


class TestDiffy(unittest.TestCase):
    """Prawdziwy git w katalogu tymczasowym: diff wzorcowy kończy się na gałęzi wątku, pomija dokumentację podróży."""

    def g(self, *a: str) -> str:
        w = uruchom.subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", str(self.repo), *a],
                                   capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(w.returncode, 0, w.stderr)
        return w.stdout.strip()

    def zapisz(self, nazwa: str, tekst: str) -> None:
        p = self.repo / nazwa
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(tekst, encoding="utf-8")

    def test_diff_wzorcowy_i_przebiegu(self) -> None:
        self.repo = Path(tempfile.mkdtemp())
        self.g("init", "-q", "-b", "main")
        self.zapisz("a.py", "1\n")
        self.g("add", "-A")
        self.g("commit", "-qm", "start")
        start = self.g("rev-parse", "HEAD")
        self.g("switch", "-qc", "watek")
        self.zapisz("a.py", "2\n")
        self.zapisz("dokumentacja/podroze/01/watek-x.md", "raport\n")
        self.g("add", "-A")
        self.g("commit", "-qm", "watek")
        self.g("switch", "-q", "main")
        self.zapisz("cudze.py", "x\n")  # cudza praca na main po starcie
        self.g("add", "-A")
        self.g("commit", "-qm", "cudze")
        self.g("merge", "-q", "--no-ff", "-m", "scalenie", "watek")
        z = {"repo": str(self.repo), "start": start, "wzorzec": self.g("rev-parse", "HEAD")}
        d = uruchom.diff_wzorcowy(z)
        self.assertIn("+2", d)
        self.assertNotIn("cudze.py", d)
        self.assertNotIn("watek-x.md", d)
        self.zapisz("a.py", "3\n")
        self.zapisz("_robocze/s.txt", "x\n")
        dp = uruchom.diff_przebiegu(self.repo, start)
        self.assertIn("+3", dp)
        self.assertNotIn("_robocze", dp)


class TestTokeny(unittest.TestCase):
    def test_liczy_z_logu_razem_z_podagentami(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        folder = tmp / "proj"
        (folder / "sid" / "subagents").mkdir(parents=True)

        def wpis(i: str, wyj: int) -> str:
            return json.dumps({"type": "assistant", "cwd": "C:/k", "timestamp": "2026-11-27T10:00:00Z", "requestId": i,
                               "message": {"id": i, "model": "claude-sonnet-5-5",
                                           "usage": {"input_tokens": 100, "output_tokens": wyj}}}) + "\n"
        (folder / "sid.jsonl").write_text(wpis("a", 10) + wpis("a", 10) + wpis("b", 20), encoding="utf-8")
        (folder / "sid" / "subagents" / "x.jsonl").write_text(wpis("c", 30), encoding="utf-8")
        t = uruchom.tokeny_z_logu("sid", tmp)
        self.assertEqual(t["wpisy"], 3)  # powtórzony komunikat liczony raz
        self.assertEqual(t["surowe"], 100 + 10 + 100 + 20 + 100 + 30)
        self.assertEqual(t["wazone"], (100 + 50) + (100 + 100) + (100 + 150))
        self.assertIsNone(uruchom.tokeny_z_logu("brak", tmp))


class TestPrzebieg(unittest.TestCase):
    """Cała ścieżka na udawanych claude i git."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.a = mock.Mock(katalog=self.tmp / "kopie", wyniki=self.tmp / "wyniki.jsonl", zachowaj=True,
                           budzet=45e6, do="2099-01-01T00:00")
        self.ctx = uruchom.Kontekst(self.a, {z["id"]: z for z in ZADANIA}, [])
        self.spec = uruchom.rozwin_plan(PLAN, ZADANIA)[0]
        self.wywolania: list[list[str]] = []

    def claude(self, odpowiedzi: list):
        def udawaj(polecenie, cwd, wejscie, limit_s):
            self.wywolania.append(polecenie)
            return odpowiedzi.pop(0)
        return udawaj

    def uruchom_z(self, odpowiedzi: list, tokeny=None, stop_po_limicie: str | None = None):
        tokeny = {"wazone": 1234.0, "surowe": 999, "wpisy": 3, "modele": {}} if tokeny is None else tokeny
        with mock.patch.object(uruchom, "przygotuj_kopie"), \
                mock.patch.object(uruchom, "brief_zadania", return_value="brief"), \
                mock.patch.object(uruchom, "diff_przebiegu", return_value="+x\n"), \
                mock.patch.object(uruchom, "diff_wzorcowy", return_value="+y\n"), \
                mock.patch.object(uruchom, "tokeny_z_logu", return_value=tokeny), \
                mock.patch.object(uruchom, "sekundy_do_resetu", return_value=0), \
                mock.patch.object(uruchom.time, "sleep"), \
                mock.patch.object(uruchom, "uruchom_proces", side_effect=self.claude(odpowiedzi)), \
                mock.patch.object(uruchom, "powod_stopu", return_value=stop_po_limicie):
            return uruchom.przebieg(self.spec, self.ctx)

    @staticmethod
    def odp(**kw) -> tuple:
        d = {"session_id": "sid", "num_turns": 7, "duration_api_ms": 5000, "total_cost_usd": 0.5, "is_error": False,
             "usage": {"input_tokens": 1}, "result": "gotowe", "terminal_reason": "completed"}
        d.update(kw)
        return (0, json.dumps(d), "", False)

    def test_pelna_sciezka(self) -> None:
        ocena = self.odp(result='{"ocena": 5, "uzasadnienie": "dobrze"}', session_id="o")
        w = self.uruchom_z([self.odp(), (0, "Ran 3 tests\n\nOK", "", False), ocena])
        self.assertTrue(w["kompletny"], w["bledy"])
        self.assertEqual((w["tury"], w["tokeny_wazone"], w["tokeny_surowe"], w["ocena"]), (7, 1234, 999, 5))
        self.assertEqual(w["ocena_wazone"], 1234)  # tokeny oceny osobno
        self.assertTrue(w["testy"]["zaliczone"])
        linie = self.a.wyniki.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(linie), 1)
        self.assertEqual(json.loads(linie[0])["id"], self.spec["id"])
        self.assertIn("--name", self.wywolania[0])
        self.assertIn(f"eks-{self.spec['id']}", self.wywolania[0])
        self.assertIn("--output-format", self.wywolania[0])
        self.assertIn("sonnet", self.wywolania[2])  # ocena na Sonnecie

    def test_limit_5h_powtarza_przebieg(self) -> None:
        limit = self.odp(is_error=True, result="5-hour limit reached ∙ resets 3pm")
        ocena = self.odp(result='{"ocena": 4, "uzasadnienie": "ok"}')
        w = self.uruchom_z([limit, self.odp(), (0, "Ran 1 tests\n\nOK", "", False), ocena])
        self.assertEqual(w["proby"], 2)
        self.assertTrue(any("limit 5 h" in b for b in w["bledy"]))
        self.assertFalse(w["kompletny"])  # błąd w historii: niekompletny, ale z pomiarem
        self.assertEqual(w["ocena"], 4)

    def test_limit_czasu_przebiegu(self) -> None:
        ocena = self.odp(result='{"ocena": 1, "uzasadnienie": "nic"}')
        w = self.uruchom_z([(-1, "", "", True), (1, "FAILED", "", False), ocena])
        self.assertTrue(any("limit czasu" in b for b in w["bledy"]))
        self.assertFalse(w["testy"]["zaliczone"])
        self.assertFalse(w["kompletny"])

    def test_wyjatek_nie_zatrzymuje(self) -> None:
        with mock.patch.object(uruchom, "przygotuj_kopie", side_effect=RuntimeError("git clone: boom")):
            w = uruchom.przebieg(self.spec, self.ctx)
        self.assertIn("boom", w["bledy"][0])
        self.assertEqual(len(self.a.wyniki.read_text(encoding="utf-8").splitlines()), 1)

    def test_wznow_pomija_tylko_kompletne(self) -> None:
        plik = self.tmp / "w.jsonl"
        plik.write_text(json.dumps({"id": "x", "kompletny": True}) + "\n" + json.dumps({"id": "y"}) + "\n{urwana",
                        encoding="utf-8")
        wyniki = uruchom.wczytaj_wyniki(plik)
        self.assertEqual([w["id"] for w in wyniki], ["x", "y"])
        self.assertEqual({w["id"] for w in wyniki if uruchom.kompletny(w)}, {"x"})


class TestRaport(unittest.TestCase):
    @staticmethod
    def w(rid, wielkosc, model, effort, wazone, czas, ocena, testy=True) -> dict:
        return {"id": rid, "zadanie": "z", "wielkosc": wielkosc, "model": model, "effort": effort, "autocompact": "200k",
                "tokeny_wazone": wazone, "czas_s": czas, "ocena": ocena, "testy": {"zaliczone": testy},
                "ocena_wazone": 100, "tury": 5, "bledy": [], "kompletny": True}

    def test_optimum_sen_i_komp_osobno_dla_wielkosci(self) -> None:
        wyniki = [
            self.w("1", "male", "haiku", "low", 100_000, 300, 3),                 # tanio, ale ocena 3
            self.w("2", "male", "sonnet", "low", 500_000, 600, 4),                # dobre, tańsze
            self.w("3", "male", "sonnet", "high", 900_000, 200, 5),               # dobre, najszybsze
            self.w("4", "male", "sonnet", "medium", 50_000, 100, 5, testy=False),  # testy nie przeszły
            self.w("5", "duze", "opus", "medium", 3_000_000, 900, 5),
        ]
        o = raport.optimum(wyniki)
        self.assertEqual(o["male"]["sen"][0], ("sonnet", "low", "200k"))
        self.assertEqual(o["male"]["komp"][0], ("sonnet", "high", "200k"))
        self.assertEqual(o["duze"]["sen"][0], ("opus", "medium", "200k"))
        self.assertEqual(o["male"]["kandydaci"], 2)

    def test_srednia_z_powtorzen_i_brak_kandydata(self) -> None:
        wyniki = [self.w("1", "male", "sonnet", "low", 100, 60, 5), self.w("2", "male", "sonnet", "low", 100, 60, 2)]
        self.assertIsNone(raport.optimum(wyniki)["male"]["sen"])  # średnia 3,5 < 4
        tekst = raport.raport(wyniki)
        self.assertIn("Brak ustawienia", tekst)
        self.assertIn("| male | sonnet | low | 200k | 2 |", tekst)

    def test_pusty_plik(self) -> None:
        self.assertIn("Przebiegów: 0", raport.raport([]))


if __name__ == "__main__":
    unittest.main()
