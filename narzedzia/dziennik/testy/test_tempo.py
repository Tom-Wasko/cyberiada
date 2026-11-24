"""Testy narzędzi tempa: analiza.py, statusline.py, tempo.py, wyko.py (tempo), instaluj.py (statusLine),
generuj.py (tempo i limit). Dane testowe, bez prawdziwych logów i bez ruszania ~/.claude."""
from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

NARZEDZIA = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(NARZEDZIA))
sys.path.insert(0, str(NARZEDZIA / "dziennik"))
import analiza  # noqa: E402
import generuj  # noqa: E402
import instaluj  # noqa: E402
import statusline  # noqa: E402
import tempo  # noqa: E402
import wyko  # noqa: E402


def zapisz_sesje(katalog: Path, nazwa: str, wiersze: list[dict], uuid: str) -> None:
    folder = katalog / "proj"
    folder.mkdir(exist_ok=True)
    (folder / uuid).mkdir()
    (folder / uuid / "custom-title.json").write_text(json.dumps({"customTitle": nazwa}), encoding="utf-8")
    (folder / f"{uuid}.jsonl").write_text("\n".join(json.dumps(w, separators=(",", ":")) for w in wiersze) + "\n", encoding="utf-8")


def odp(id_: str, minuta: int, wej: int = 100, zapis: int = 0, odczyt: int = 0, wyj: int = 10, narzedzie=None,
        model: str = "claude-sonnet-5-5") -> dict:
    t = datetime(2026, 11, 20, 10, 0) + timedelta(minutes=minuta)
    tresc = [{"type": "tool_use", "name": narzedzie[0], "input": narzedzie[1]}] if narzedzie else []
    return {"type": "assistant", "timestamp": t.strftime("%Y-%m-%dT%H:%M:%S.000Z"), "cwd": "C:\\x", "requestId": id_,
            "message": {"id": id_, "model": model, "content": tresc,
                        "usage": {"input_tokens": wej, "cache_creation_input_tokens": zapis,
                                  "cache_read_input_tokens": odczyt, "output_tokens": wyj}}}


class TestAnaliza(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        k = Path(self.tmp.name)
        zapisz_sesje(k, "archi-x", [
            {"type": "api-request", "querySource": "repl_main_thread", "params": {"output_config": {"effort": "high"},
                                                                              "model": "claude-opus-5-5"}},
            odp("a1", 0, odczyt=60_000, model="claude-opus-5-5"),
            odp("a2", 1, odczyt=150_000, model="claude-opus-5-5"),
            odp("a3", 90, zapis=150_000, model="claude-opus-5-5"),  # po przerwie > 1 h
            {"type": "system", "subtype": "compact_boundary", "timestamp": "2026-11-20T11:35:00.000Z",
             "compactMetadata": {"preTokens": 150000, "postTokens": 20000}},
            odp("a4", 100, odczyt=20_000, model="claude-opus-5-5"),
        ], "u1")
        zapisz_sesje(k, "wyko-x-01-w", [
            odp("w1", 0), odp("w2", 1, narzedzie=("Read", {})), odp("w3", 2, narzedzie=("Edit", {})),
            odp("w4", 10, narzedzie=("Bash", {"command": "git -c user.name=T commit -m x"})),
        ], "u2")
        self.r = analiza.analizuj(k, None, None)

    def test_udzialy_sumuja_sie_do_100(self) -> None:
        self.assertAlmostEqual(sum(self.r["udzial_proc"].values()), 100, delta=0.3)
        self.assertEqual(set(self.r["udzial_proc"]), {"archi", "wyko"})

    def test_kontekst_archiego(self) -> None:
        self.assertEqual(self.r["archi_kontekst"]["50–100k"]["tur"], 1)
        self.assertEqual(self.r["archi_kontekst"][">200k"]["tur"], 0)

    def test_przerwy(self) -> None:
        self.assertEqual(self.r["przerwy"][">1 h"]["tur"], 1)
        self.assertGreater(self.r["przerwy"][">1 h"]["zapis_suma"], 0)

    def test_wyko_start_i_commity(self) -> None:
        w = self.r["wyko"]
        self.assertEqual((w["sesji"], w["tur_startu_mediana"], w["commitow_srednio"]), (1, 3, 1))

    def test_compact_i_effort(self) -> None:
        self.assertEqual(self.r["compact"]["ile"], 1)
        self.assertEqual(self.r["compact"]["przed_srednio"], 150000)
        self.assertIn(("archi", "opus-5-5", "high"), {(m["rodzaj"], m["model"], m["effort"]) for m in self.r["model_effort"]})

    def test_raport_do_60_linii(self) -> None:
        self.assertLessEqual(len(analiza.raport(self.r).splitlines()), 60)


class TestStatusline(unittest.TestCase):
    DANE = {"model": {"display_name": "Sonnet"}, "context_window": {"used_percentage": 12.4},
            "rate_limits": {"five_hour": {"used_percentage": 40, "resets_at": 4102444800},
                            "seven_day": {"used_percentage": 5, "resets_at": 4102444800}}}

    def test_linia(self) -> None:
        t = statusline.linia(self.DANE)
        self.assertIn("Sonnet", t)
        self.assertIn("kontekst 12%", t)
        self.assertIn("limit 5h 40%", t)
        self.assertIn("do resetu", t)

    def test_zapis_atomowy_i_brak_limitu(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            plik = Path(d) / "l.json"
            statusline.zapisz(statusline.limity(self.DANE), plik)
            z = json.loads(plik.read_text(encoding="utf-8"))
            self.assertEqual(z["five_hour"]["used"], 40)
            self.assertEqual(z["seven_day"]["used"], 5)
            self.assertIn("czas", z)
            self.assertFalse(list(Path(d).glob("*.tmp")))
        self.assertIsNone(statusline.limity({"model": {"display_name": "X"}}))
        self.assertEqual(statusline.linia({}), "?")


class TestTempo(unittest.TestCase):
    def limit(self, uzyte: float, uplynelo_min: float = 150) -> tuple[dict, datetime]:
        teraz = datetime(2026, 11, 24, 12, 0).astimezone()
        koniec = teraz + timedelta(minutes=300 - uplynelo_min)
        return {"five_hour": {"used": uzyte, "resets_at": koniec.timestamp()}, "czas": teraz.isoformat()}, teraz

    def test_zolw_za_szybko_dobrze_za_wolno(self) -> None:
        for uzyte, oczek in ((70, "oszczędniej"), (50, "tempo dobre"), (30, "dodaj wyko")):
            l, t = self.limit(uzyte)
            self.assertIn(oczek, tempo.licz(l, t, "zolw")["rada"])

    def test_zolw_nigdy_czekaj(self) -> None:
        for uzyte in (10, 50, 95):
            l, t = self.limit(uzyte)
            self.assertNotIn("czekaj", tempo.tekst(tempo.licz(l, t, "zolw")).lower())

    def test_liczby_i_prognoza(self) -> None:
        l, t = self.limit(40)  # 50% czasu, 40% limitu → 100% po 375 min, czyli po resecie
        w = tempo.licz(l, t, "krolik")
        self.assertEqual((w["czas_proc"], w["limit_proc"], w["roznica_pp"]), (50.0, 40.0, -10.0))
        self.assertFalse(w["przed_resetem"])
        self.assertNotIn("rada", w)

    def test_stare_dane_ostrzezenie(self) -> None:
        l, t = self.limit(40)
        l["czas"] = (t - timedelta(minutes=30)).isoformat()
        self.assertTrue(any("30 min" in o for o in tempo.licz(l, t, "zolw")["ostrzezenia"]))

    def test_brak_danych(self) -> None:
        self.assertTrue(tempo.licz({}, datetime.now().astimezone(), "zolw")["ostrzezenia"])

    def test_nazwy_i_stan_md(self) -> None:
        self.assertEqual([tempo.tempo_nazwa(x) for x in ("żółw", "Zwykły", "królik", "kot")],
                         ["zolw", "zwykly", "krolik", None])
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "dokumentacja").mkdir()
            (Path(d) / "dokumentacja" / "Stan.md").write_text("# Stan\nTempo: żółw\n", encoding="utf-8")
            self.assertEqual(tempo.tempo_ze_stanu(Path(d)), "zolw")


class TestWyko(unittest.TestCase):
    def test_tempa(self) -> None:
        mech, trudny, nic = "- Rodzaj: mechaniczny\n", "Rodzaj: trudny\n", "Brief bez rodzaju. (`Rodzaj: mechaniczny` w tekście)"
        self.assertEqual(wyko.ustawienia_tempa("zolw", mech), {"model": "sonnet", "effort": "low", "autocompact": "120k"})
        self.assertEqual(wyko.ustawienia_tempa("zolw", nic)["effort"], "medium")
        self.assertEqual(wyko.ustawienia_tempa("zwykly", trudny), {"model": "sonnet", "effort": "medium", "autocompact": "200k"})
        self.assertEqual(wyko.ustawienia_tempa("krolik", trudny)["effort"], "high")
        self.assertEqual(wyko.ustawienia_tempa("krolik", nic)["effort"], "medium")

    def test_flagi(self) -> None:
        f = wyko.wspolne_flagi("sonnet", "low", "120k")
        self.assertEqual(f[f.index("--effort") + 1], "low")
        self.assertEqual(f[f.index("--autocompact") + 1], "120k")


class TestInstalujStatusline(unittest.TestCase):
    def uruchom(self, zawartosc: dict | None) -> tuple[dict, list[str]]:
        with tempfile.TemporaryDirectory() as d:
            plik = Path(d) / "settings.json"
            if zawartosc is not None:
                plik.write_text(json.dumps(zawartosc), encoding="utf-8")
            with mock.patch.object(instaluj, "USTAWIENIA", plik), mock.patch.object(instaluj, "problemy", []) as pr, \
                    redirect_stdout(io.StringIO()):
                instaluj.statusline(False)
            return json.loads(plik.read_text(encoding="utf-8")), list(pr)

    def test_dopisuje_gdy_brak(self) -> None:
        d, _ = self.uruchom({"model": "sonnet"})
        self.assertEqual(d["statusLine"]["type"], "command")
        self.assertTrue(d["statusLine"]["command"].endswith("narzedzia/statusline.py"))
        self.assertEqual(d["model"], "sonnet")

    def test_nie_nadpisuje_cudzego(self) -> None:
        cudzy = {"type": "command", "command": "moj-status"}
        d, _ = self.uruchom({"statusLine": cudzy})
        self.assertEqual(d["statusLine"], cudzy)


class TestGeneratorTempo(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.k = Path(self.tmp.name)
        (self.k / "dokumentacja").mkdir()
        (self.k / "sesje").mkdir()

    def stan(self, tekst: str) -> dict:
        (self.k / "dokumentacja" / "Stan.md").write_text(tekst, encoding="utf-8")
        return generuj.czytaj_stan(self.k)

    def test_tempo_w_stanie(self) -> None:
        self.assertEqual(self.stan("# Stan: p\nArchi żył: 2026-11-20 18:45\nTempo: żółw\n\n## Podróż\n—\n")["tempo"], "zolw")
        self.assertEqual(self.stan("# Stan: p\nTempo: królik\n")["tempo"], "krolik")
        self.assertIsNone(self.stan("# Stan: p\nArchi żył: —\n")["tempo"])
        self.assertIsNone(self.stan("# Stan: p\nTempo: szybkie\n")["tempo"])

    def test_limit_z_pliku(self) -> None:
        plik = self.k / "limit.json"
        statusline.zapisz({"five_hour": {"used": 41.26, "resets_at": 4102444800}, "czas": "2026-11-24T12:00:00+01:00"}, plik)
        d = generuj.zbuduj(self.k, "p", teraz=datetime(2026, 11, 24, 12, 0), katalog_sesji=self.k / "sesje", plik_limitu=plik)
        self.assertEqual(d["koszty"]["limit"]["used"], 41.3)
        self.assertEqual(d["koszty"]["limit"]["czas"], "2026-11-24T12:00:00+01:00")
        self.assertIn("reset", d["koszty"]["limit"])

    def test_brak_limitu_to_null(self) -> None:
        self.assertIsNone(generuj.limit5h(self.k / "nie-ma.json"))
        d = generuj.zbuduj(self.k, "p", teraz=datetime(2026, 11, 24, 12, 0), katalog_sesji=self.k / "sesje")
        self.assertIsNone(d["koszty"]["limit"])
        self.assertIsNone(d["tempo"])


if __name__ == "__main__":
    unittest.main()
