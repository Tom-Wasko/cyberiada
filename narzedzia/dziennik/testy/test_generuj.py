"""Testy generatora dziennika.

  python -X utf8 -m unittest discover -s narzedzia/dziennik/testy -v

Dokumenty bierze z `dane/` (Stan.md, Decyzje.md, Zadania.md, plan.md), a logi sesji buduje w kodzie
w katalogu tymczasowym (podawanym jako `katalog_sesji`), żeby nie dotykać prawdziwych sesji.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

TESTY = Path(__file__).resolve().parent
DANE = TESTY / "dane"
sys.path.insert(0, str(TESTY.parent))
import generuj  # noqa: E402

TERAZ = datetime(2026, 11, 21, 14, 30).astimezone()


def czas(dzien: int, godz: int, minuta: int = 0) -> datetime:
    """Czas lokalny: `dzien` dni przed TERAZ (data), o danej godzinie."""
    d = (TERAZ - timedelta(days=dzien)).replace(hour=godz, minute=minuta, second=0, microsecond=0)
    return d


def znacznik(d: datetime) -> str:
    return d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def linia(id_: str, model: str, kiedy: datetime, cwd: str, **uzycie) -> str:
    u = {"input_tokens": 0, "cache_creation_input_tokens": 0,
         "cache_read_input_tokens": 0, "output_tokens": 0}
    u.update(uzycie)
    return json.dumps({"type": "assistant", "timestamp": znacznik(kiedy), "cwd": cwd,
                       "requestId": "r-" + id_,
                       "message": {"id": id_, "model": model, "usage": u}})


class Pomoc(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.korzen = Path(self.tmp.name)
        self.projekt = self.korzen / "probny"
        self.sesje = self.korzen / "sesje"
        self.sesje.mkdir()

    def dokumentacja(self) -> None:
        dok = self.projekt / "dokumentacja"
        (dok / "podroze" / "02-wyglad").mkdir(parents=True)
        for nazwa in ("Stan.md", "Decyzje.md", "Zadania.md"):
            shutil.copy(DANE / nazwa, dok / nazwa)
        shutil.copy(DANE / "plan.md", dok / "podroze" / "02-wyglad" / "plan.md")

    def sesja(self, nazwa: str, wiersze: list[str], uuid: str, agent: str | None = None,
              folder: str = "proj") -> None:
        """Zapisuje dziennik sesji `nazwa`; z `agent` wiersze trafiają do subagents/ tej sesji."""
        katalog = self.sesje / folder
        katalog.mkdir(exist_ok=True)
        dziennik = katalog / f"{uuid}.jsonl"
        if not dziennik.exists():
            dziennik.write_text("", encoding="utf-8")
            meta = katalog / uuid
            meta.mkdir()
            (meta / "custom-title.json").write_text(json.dumps({"customTitle": nazwa}), encoding="utf-8")
        cel = dziennik
        if agent:
            cel = katalog / uuid / "subagents" / f"{agent}.jsonl"
            cel.parent.mkdir(exist_ok=True)
        with open(cel, "a", encoding="utf-8") as f:
            f.write("\n".join(wiersze) + "\n")

    def logi(self) -> None:
        cwd = str(self.projekt.resolve())
        self.sesja("archi-probny", [linia("a1", "claude-opus-5-5", czas(0, 13, 30), cwd,
                                          input_tokens=50, output_tokens=5)], "u-archi")
        # sonnet: 100 + 5*10 = 150 (z modelem opus podwojone, więc tu sprawdzamy mnożnik 2 → 300)
        self.sesja("archi-probny", [linia("g1", "claude-haiku-5-5", czas(0, 13, 45), cwd,
                                          input_tokens=1000)], "u-archi", agent="agent1")
        wyko = linia("w1", "claude-opus-5-5", czas(0, 10, 15), cwd, input_tokens=100,
                     cache_creation_input_tokens=50, cache_read_input_tokens=1000, output_tokens=20)
        self.sesja("wyko-probny-02-css", [wyko, wyko], "u-wyko")  # powtórzony komunikat liczy się raz
        self.sesja("rozmowa", [
            linia("p1", "claude-sonnet-5-5", czas(1, 20), cwd, input_tokens=300),
            linia("p2", "claude-sonnet-5-5", czas(2, 9), cwd, input_tokens=40),
            linia("p3", "claude-sonnet-5-5", czas(10, 9), cwd, input_tokens=70),
            linia("p4", "claude-sonnet-5-5", czas(40, 9), cwd, input_tokens=5),
        ], "u-rozmowa")
        # inny projekt: liczy się tylko do okna 5 h
        self.sesja("archi-inny", [linia("i1", "claude-sonnet-5-5", czas(0, 12, 10),
                                        str(self.korzen / "inny"), input_tokens=200)],
                   "u-inny", folder="inny")


class TestParsery(unittest.TestCase):
    def test_pytanie_z_opcjami_i_rekomendacja(self):
        p = generuj.pytanie(["P1: Który wygląd?", "  - A: Jasny (rekomendowane)", "  - B: Ciemny",
                             "    z dopiskiem"])
        self.assertEqual(p["id"], "P1")
        self.assertEqual(p["tresc"], "Który wygląd?")
        self.assertEqual(p["opcje"], [
            {"litera": "A", "tekst": "Jasny", "rekomendowana": True},
            {"litera": "B", "tekst": "Ciemny z dopiskiem", "rekomendowana": False}])

    def test_pytanie_bez_opcji_i_bez_numeru(self):
        self.assertEqual(generuj.pytanie(["P7: Samo pytanie,", "  ciąg dalszy."]),
                         {"id": "P7", "tresc": "Samo pytanie, ciąg dalszy.", "opcje": []})
        self.assertEqual(generuj.pytanie(["Zwykła sprawa"]),
                         {"id": None, "tresc": "Zwykła sprawa", "opcje": []})

    def test_komentarze_sa_pomijane(self):
        plik = Path(tempfile.mkdtemp()) / "x.md"
        self.addCleanup(shutil.rmtree, plik.parent)
        plik.write_bytes("a <!-- ukryte\nw dwóch liniach --> b\r\nc".encode("utf-8"))
        self.assertEqual(generuj.czytaj(plik), "a  b\nc")

    def test_rola(self):
        self.assertEqual(generuj.rola("archi-x", False), "Archi")
        self.assertEqual(generuj.rola("wyko-x-01-a", False), "wyko")
        self.assertEqual(generuj.rola("rozmowa", False), "Pomocnik")
        self.assertEqual(generuj.rola("archi-x", True), "agenci")


class TestDokumenty(Pomoc):
    def setUp(self) -> None:
        super().setUp()
        self.dokumentacja()
        self.dane = generuj.zbuduj(self.projekt, "probny", "Opis", "u/probny", TERAZ, self.sesje)

    def test_schemat_i_json(self):
        self.assertEqual(set(self.dane), {"nazwa", "opis", "repo", "wygenerowano", "puls", "podroz", "czeka",
                                          "decyzje", "zadania", "historia", "koszty", "commity"})
        self.assertEqual(set(self.dane["koszty"]), {"dni", "role", "okno5h"})
        json.dumps(self.dane, ensure_ascii=False)  # serializuje się bez błędu
        self.assertEqual((self.dane["nazwa"], self.dane["opis"], self.dane["repo"]),
                         ("probny", "Opis", "u/probny"))

    def test_puls(self):
        self.assertEqual(self.dane["puls"], "2026-11-20 18:45")

    def test_czeka(self):
        c = self.dane["czeka"]
        self.assertEqual([x["id"] for x in c], ["P1", None, "P2"])
        self.assertEqual(c[0]["opcje"], [
            {"litera": "A", "tekst": "Jasny", "rekomendowana": True},
            {"litera": "B", "tekst": "Ciemny z dopiskiem w drugiej linii", "rekomendowana": False}])
        self.assertEqual(c[1]["tresc"], "Zwykła sprawa bez numeru.")
        self.assertEqual(c[2]["tresc"], "Pytanie bez opcji, ciąg dalszy w kolejnej linii.")
        self.assertEqual(c[2]["opcje"], [])

    def test_podroz(self):
        p = self.dane["podroz"]
        self.assertEqual((p["numer"], p["temat"], p["start"], p["tryb"]),
                         ("02", "wyglad", "2026-11-18", "nadzorowany"))
        self.assertEqual(p["kryteria"], [
            {"tekst": "Strona działa na telefonie", "zrobione": False},
            {"tekst": "Kolory z palety w dwóch liniach", "zrobione": True}])
        css, tresc = p["watki"]
        self.assertEqual((css["nazwa"], css["kto"], css["stan"], css["galaz"]),
                         ("css", "wyko", "w toku", "worktree-podroz-02-css"))
        self.assertEqual((tresc["nazwa"], tresc["kto"], tresc["stan"], tresc["galaz"]),
                         ("tresc", "Archi", "gotowy", "podroz-02"))
        for w in (css, tresc):
            self.assertEqual(w["start"], "2026-11-18")  # poza gitem: start podróży
            self.assertIsNone(w["scalono"])

    def test_decyzje_i_zadania(self):
        self.assertEqual(self.dane["decyzje"]["szefa"], [
            {"data": "2026-11-18", "tresc": "Strona ma być prosta."},
            {"data": "2026-11-19", "tresc": "Bez animacji, nawet małych."}])
        self.assertEqual(self.dane["decyzje"]["archiego"],
                         [{"data": "2026-11-18", "tresc": "Dane w JSON."}])
        self.assertEqual(self.dane["zadania"], {"w_toku": ["Podróż 02-wyglad."],
                                                "zaplanowane": ["Testy na telefonie.", "Druga rzecz."],
                                                "odlozone": []})

    def test_historia(self):
        self.assertEqual(self.dane["historia"], [{"numer": "02", "temat": "wyglad", "start": "2026-11-18",
                                                  "koniec": None,
                                                  "podsumowanie": "Krótko o tym, co wyszło."}])


class TestKoszty(Pomoc):
    def setUp(self) -> None:
        super().setUp()
        self.dokumentacja()
        self.logi()
        self.dane = generuj.zbuduj(self.projekt, "probny", teraz=TERAZ, katalog_sesji=self.sesje)
        self.koszty = self.dane["koszty"]

    def test_dni_z_zerami(self):
        dni = self.koszty["dni"]
        self.assertEqual(len(dni), 30)
        self.assertEqual(dni[-1]["dzien"], "2026-11-21")
        self.assertEqual(dni[0]["dzien"], "2026-10-23")
        po = {d["dzien"]: d for d in dni}
        # dziś: Archi opus 2*(50+5*5)=150, agent haiku 0.05*1000=50, wyko opus 2*(100+100+100+100)=800
        self.assertEqual(po["2026-11-21"]["wazone"], 1000)
        self.assertEqual(po["2026-11-21"]["wejscie"], 1150)
        self.assertEqual(po["2026-11-21"]["cache_zapis"], 50)
        self.assertEqual(po["2026-11-21"]["cache_odczyt"], 1000)
        self.assertEqual(po["2026-11-21"]["wyjscie"], 25)
        self.assertEqual(po["2026-11-20"]["wazone"], 300)
        self.assertEqual(po["2026-11-19"]["wazone"], 40)
        zerowe = [d for d in dni if d["dzien"] not in ("2026-11-21", "2026-11-20", "2026-11-19", "2026-11-11")]
        self.assertTrue(all(d["wazone"] == 0 and d["wejscie"] == 0 for d in zerowe))

    def test_role_i_podroze(self):
        role = {(r["podroz"], r["rola"]): r["wazone"] for r in self.koszty["role"]}
        self.assertEqual(role, {("02", "Archi"): 150, ("02", "agenci"): 50, ("02", "wyko"): 800,
                                ("02", "Pomocnik"): 340, ("poza", "Pomocnik"): 75})
        self.assertEqual(self.koszty["role"][-1]["podroz"], "poza")  # „poza” zawsze na końcu

    def test_okno_5h(self):
        o = self.koszty["okno5h"]
        # okno od pełnej godziny pierwszego wpisu (10:15 → 10:00); wpis z wczoraj to osobne, wygasłe okno
        self.assertEqual(o["od"], czas(0, 10).isoformat(timespec="seconds"))
        self.assertEqual(o["reset"], czas(0, 15).isoformat(timespec="seconds"))
        self.assertEqual(o["wazone"], 1000 + 200)  # razem z innym projektem

    def test_okno_po_wygasnieciu(self):
        pozniej = czas(0, 20)
        o = generuj.okno5h(pozniej, self.sesje)
        self.assertEqual(o, {"od": None, "reset": None, "wazone": 0})

    def test_nowe_okno_po_przerwie(self):
        # o 12:00 trwa okno 10:00–15:00 z wpisem z 10:15, a wpis z wczoraj nie wlicza się
        o = generuj.okno5h(czas(0, 12), self.sesje)
        self.assertEqual(o["od"], czas(0, 10).isoformat(timespec="seconds"))
        self.assertEqual(o["wazone"], 800)


class TestBrakDanych(Pomoc):
    def test_pusty_projekt_bez_wyjatku(self):
        self.projekt.mkdir()
        d = generuj.zbuduj(self.projekt, "probny", teraz=TERAZ, katalog_sesji=self.sesje)
        self.assertIsNone(d["puls"])
        self.assertIsNone(d["podroz"])
        self.assertEqual(d["czeka"], [])
        self.assertEqual(d["decyzje"], {"szefa": [], "archiego": []})
        self.assertEqual(d["zadania"], {"w_toku": [], "zaplanowane": [], "odlozone": []})
        self.assertEqual(d["historia"], [])
        self.assertEqual(len(d["koszty"]["dni"]), 30)
        self.assertTrue(all(x["wazone"] == 0 for x in d["koszty"]["dni"]))
        self.assertEqual(d["koszty"]["role"], [])
        self.assertEqual(d["koszty"]["okno5h"], {"od": None, "reset": None, "wazone": 0})
        self.assertIsInstance(d["commity"], list)

    def test_puste_pliki(self):
        dok = self.projekt / "dokumentacja"
        dok.mkdir(parents=True)
        for nazwa in ("Stan.md", "Decyzje.md", "Zadania.md"):
            (dok / nazwa).write_text("", encoding="utf-8")
        d = generuj.zbuduj(self.projekt, "probny", teraz=TERAZ, katalog_sesji=self.sesje)
        self.assertIsNone(d["podroz"])
        self.assertEqual(d["czeka"], [])
        self.assertEqual(d["zadania"]["w_toku"], [])


if __name__ == "__main__":
    unittest.main()
