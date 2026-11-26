"""Testy narzędzi trybów: analiza.py, statusline.py, tryb.py, wyko.py (tryb), instaluj.py, archi.py, hook_commit.py,
generuj.py (tryb i limit). Dane testowe, bez prawdziwych logów i bez ruszania ~/.claude."""
from __future__ import annotations

import io
import json
import os
import subprocess
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
import archi  # noqa: E402
import hook_commit  # noqa: E402
import tryb  # noqa: E402
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


def tmp_stan(d: Path, tekst: str) -> None:
    (d / "dokumentacja").mkdir(exist_ok=True)
    (d / "dokumentacja" / "Stan.md").write_text(tekst, encoding="utf-8")


class TestTryb(unittest.TestCase):
    TERAZ = datetime(2026, 11, 24, 12, 0).astimezone()

    def limit(self, uzyte: float, uplynelo_min: float = 150, tydzien: float | None = None,
              tydzien_uplynelo_dni: float = 3.5) -> dict:
        koniec = self.TERAZ + timedelta(minutes=300 - uplynelo_min)
        l = {"five_hour": {"used": uzyte, "resets_at": koniec.timestamp()}, "czas": self.TERAZ.isoformat()}
        if tydzien is not None:
            l["seven_day"] = {"used": tydzien, "resets_at": (self.TERAZ + timedelta(days=7 - tydzien_uplynelo_dni)).timestamp()}
        return l

    def licz(self, uzyte, tryb_="sen", **kw):
        bez = kw.pop("bez_hamulca", False)
        return tryb.licz(self.limit(uzyte, **kw), self.TERAZ, tryb_, bez)

    def test_sen_za_szybko_dobrze_za_wolno(self) -> None:
        for uzyte, oczek, wyko_ in ((70, "oszczędniej", -1), (50, "tempo dobre", 0), (30, "dodaj wyko", 1)):
            w = self.licz(uzyte)
            self.assertIn(oczek, w["rada"])
            self.assertEqual(w["wyko"], wyko_)

    def test_nigdy_czekaj(self) -> None:
        for t in tryb.TRYBY:
            for uzyte in (10, 50, 95):
                self.assertNotIn("czekaj", tryb.tekst(self.licz(uzyte, t, tydzien=60)).lower())

    def test_komp_tylko_liczby(self) -> None:
        w = self.licz(40, "komp", tydzien=10)  # 50% czasu, 40% limitu → 100% po 375 min, po resecie
        self.assertEqual((w["czas_proc"], w["limit_proc"], w["roznica_pp"]), (50.0, 40.0, -10.0))
        self.assertFalse(w["przed_resetem"])
        self.assertNotIn("rada", w)
        self.assertEqual(w["wyko"], 0)
        self.assertIn("tydzien_proc", w)

    def test_szkola_cel_to_koniec_ramy(self) -> None:
        # okno 9:30–14:30, teraz 12:00; rama do 13:00 → cel 13:00, minęło 150/210 = 71% czasu
        do = {"tryb": "szkola", "od": None, "do": "13:00", "stan": "znikam"}
        w = self.licz(71, do)
        self.assertEqual((w["czas_proc"], w["cel"]), (71.4, "13:00"))
        self.assertEqual(w["wyko"], 0)
        self.assertEqual(self.licz(50, do)["wyko"], 1)
        self.assertEqual(self.licz(90, do)["wyko"], -1)

    def test_szkola_rama_po_resecie_liczy_okno(self) -> None:
        w = self.licz(50, {"tryb": "szkola", "od": None, "do": "20:00", "stan": None})
        self.assertEqual((w["czas_proc"], w["cel"]), (50.0, w["reset"]))
        self.assertNotIn("po_ramie", w)

    def test_szkola_po_ramie(self) -> None:
        w = self.licz(50, {"tryb": "szkola", "od": None, "do": "11:00", "stan": None})
        self.assertTrue(w["po_ramie"])
        self.assertIn("rama minęła: podsumowanie dla szefa, dalej jak w śnie", w["rada"])

    def test_hamulec_tygodniowy_wygrywa(self) -> None:
        w = self.licz(30, tydzien=60)  # tydzień 50% czasu, 60% limitu, okno wolno
        self.assertEqual(w["wyko"], -1)
        self.assertIn("tydzień przed linią o 10 pp: oszczędniej, bez nowego wyko", w["rada"])
        self.assertNotIn("dodaj wyko", w["rada"])
        self.assertEqual(self.licz(30, tydzien=53)["wyko"], 1)  # w marginesie 5 pp: bez hamulca
        b = self.licz(30, tydzien=60, bez_hamulca=True)
        self.assertEqual(b["wyko"], 1)
        self.assertNotIn("rada_tygodnia", b)
        self.assertNotIn("rada_tygodnia", self.licz(30, "komp", tydzien=90))

    def test_stare_dane_ostrzezenie(self) -> None:
        l = self.limit(40)
        l["czas"] = (self.TERAZ - timedelta(minutes=30)).isoformat()
        self.assertTrue(any("30 min" in o for o in tryb.licz(l, self.TERAZ, "sen")["ostrzezenia"]))

    def test_brak_danych(self) -> None:
        self.assertTrue(tryb.licz({}, self.TERAZ, "sen")["ostrzezenia"])

    def test_nazwy_i_stare_zapisy(self) -> None:
        self.assertEqual([tryb.tryb_nazwa(x) for x in ("komp", "Sen", "szkoła", "SZKOLA", "nadzorowany", "autonomiczny", "kot")],
                         ["komp", "sen", "szkola", "szkola", "komp", "sen", None])

    def test_linia_stanu(self) -> None:
        t = tryb.tryb_z_tekstu
        self.assertEqual(t("# S\nTryb: komp od 16:10\n"), {"tryb": "komp", "od": "16:10", "do": None, "stan": None})
        self.assertEqual(t("Tryb: sen od 23:10"), {"tryb": "sen", "od": "23:10", "do": None, "stan": None})
        self.assertEqual(t("- **Tryb:** szkoła do 16:00 (znikam)"), {"tryb": "szkola", "od": None, "do": "16:00", "stan": "znikam"})
        self.assertEqual(t("Tryb: szkola do 8:05 (jestem)")["do"], "08:05")
        self.assertEqual(t("Tryb: autonomiczny")["tryb"], "sen")
        self.assertIsNone(t("Tempo: żółw"))
        self.assertIsNone(t("Tryb: kot"))

    def test_stan_md_i_domyslny_komp(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(tryb.tryb_ze_stanu(Path(d))["tryb"], "komp")
            tmp_stan(Path(d), "# Stan\nBrak linii\n")
            self.assertEqual(tryb.tryb_ze_stanu(Path(d)), {"tryb": "komp", "od": None, "do": None, "stan": None})
            tmp_stan(Path(d), "# Stan\nTryb: szkoła do 16:00 (jestem)\n")
            self.assertEqual(tryb.tryb_ze_stanu(Path(d))["stan"], "jestem")

    def test_cli_json(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            plik = Path(d) / "l.json"
            plik.write_text(json.dumps(self.limit(70)), encoding="utf-8")
            with mock.patch.object(sys, "argv", ["tryb", "--tryb", "sen", "--plik", str(plik), "--json",
                                                 "--teraz", self.TERAZ.isoformat()]), redirect_stdout(io.StringIO()) as out:
                tryb.main()
            self.assertEqual(json.loads(out.getvalue())["wyko"], -1)


class TestWyko(unittest.TestCase):
    def test_tryby(self) -> None:
        mech, trudny, nic = "- Rodzaj: mechaniczny\n", "Rodzaj: trudny\n", "Brief bez rodzaju. (`Rodzaj: mechaniczny` w tekście)"
        self.assertEqual(wyko.ustawienia_trybu("komp", nic), {"model": "sonnet", "effort": "medium", "autocompact": "200k"})
        self.assertEqual(wyko.ustawienia_trybu("komp", trudny)["effort"], "high")
        self.assertEqual(wyko.ustawienia_trybu("komp", mech)["effort"], "medium")
        for t in ("sen", "szkola"):
            self.assertEqual(wyko.ustawienia_trybu(t, mech), {"model": "sonnet", "effort": "low", "autocompact": "120k"})
            self.assertEqual(wyko.ustawienia_trybu(t, trudny)["effort"], "medium")
            self.assertEqual(wyko.ustawienia_trybu(t, nic)["effort"], "medium")

    def test_flagi(self) -> None:
        f = wyko.wspolne_flagi("sonnet", "low", "120k")
        self.assertEqual(f[f.index("--effort") + 1], "low")
        self.assertEqual(f[f.index("--autocompact") + 1], "120k")


class TestArchi(unittest.TestCase):
    def polecenie(self, argv: list[str]) -> str:
        with tempfile.TemporaryDirectory() as d, \
                mock.patch.object(archi, "projekty", return_value={"p": Path(d)}), \
                mock.patch.object(archi, "sesja_o_nazwie", return_value=None), \
                mock.patch.object(archi.os, "chdir"), redirect_stdout(io.StringIO()) as out:
            self.assertEqual(archi.main(["p", *argv, "--pokaz"]), 0)
        return out.getvalue().splitlines()[-1]

    def test_start_bez_slowa_trybu(self) -> None:
        self.assertTrue(self.polecenie([]).endswith(" start"))

    def test_slowo_trybu_to_polecenie(self) -> None:
        self.assertTrue(self.polecenie(["sen"]).endswith(" /sen"))
        self.assertTrue(self.polecenie(["szkola", "16:00"]).endswith(' "/szkola 16:00"'))
        self.assertTrue(self.polecenie(["komp"]).endswith(" /komp"))


class TestHookCiaglosc(unittest.TestCase):
    def zadania(self, tresc: str | None) -> str | None:
        with tempfile.TemporaryDirectory() as d:
            if tresc is not None:
                (Path(d) / "dokumentacja").mkdir()
                (Path(d) / "dokumentacja" / "Zadania.md").write_text(tresc, encoding="utf-8")
            return hook_commit.nastepne_zadanie(Path(d))

    def test_nastepnie_wygrywa_i_obcina(self) -> None:
        dlugie = "x" * 200
        t = self.zadania(f"## W toku\n- Z1 · a\n## Następnie\n- Z5 · {dlugie}\n- Z6 · b\n## Zaplanowane\n- Z9 · c\n")
        self.assertIn("Z5 · xxx", t)
        self.assertNotIn("Z9", t)
        self.assertLess(len(t.split(". Ciągłość")[0]), 150)
        self.assertIn("Ciągłość: jeśli nie czeka na decyzję szefa, w tej samej turze napisz wątek i uruchom wyko", t)

    def test_zaplanowane_gdy_nastepnie_puste(self) -> None:
        self.assertIn("Z9 · c", self.zadania("## Następnie\n\n## Zaplanowane\n- Z9 · c\n"))

    def test_lista_pusta_i_brak_pliku(self) -> None:
        self.assertTrue(self.zadania("## Następnie\n\n## Zaplanowane\n\n## Odłożone\n- Z3 · d\n").startswith("Lista pusta"))
        self.assertIsNone(self.zadania(None))


class TestInstalujStare(unittest.TestCase):
    def test_stare_skille(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "cyb" / "skille" / "zyje").mkdir(parents=True)
            (d / "cyb" / "skille" / "stary").mkdir()
            (d / "inny").mkdir()
            skills = d / "clau" / "skills"
            skills.mkdir(parents=True)
            for nazwa, cel in (("zyje", d / "cyb" / "skille" / "zyje"), ("stary", d / "cyb" / "skille" / "stary"),
                               ("cudzy", d / "inny")):
                subprocess.run(["cmd", "/c", "mklink", "/J", str(skills / nazwa), str(cel)], check=True, capture_output=True)
            (d / "cyb" / "skille" / "stary").rmdir()
            (d / "inny").rmdir()  # cudzy też wisi, ale nie wskazuje do cyberiady
            with mock.patch.object(instaluj, "CYBERIADA", d / "cyb"), mock.patch.object(instaluj, "CLAUDE_DIR", d / "clau"):
                self.assertEqual([p.name for p in instaluj.stare_skille()], ["stary"])
                instaluj.usun_dowiazanie(skills / "stary")
                self.assertEqual(instaluj.stare_skille(), [])
            self.assertTrue(os.path.lexists(skills / "cudzy"))
            self.assertTrue((d / "cyb" / "skille" / "zyje").exists())


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


class TestGeneratorTryb(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.k = Path(self.tmp.name)
        (self.k / "dokumentacja").mkdir()
        (self.k / "sesje").mkdir()

    def stan(self, tekst: str) -> dict:
        (self.k / "dokumentacja" / "Stan.md").write_text(tekst, encoding="utf-8")
        return generuj.czytaj_stan(self.k)

    def test_tryb_w_stanie(self) -> None:
        self.assertEqual(self.stan("# Stan: p\nArchi żył: 2026-11-20 18:45\nTryb: szkoła do 16:00 (znikam)\n\n## Podróż\n—\n")["tryb"],
                         {"tryb": "szkola", "od": None, "do": "16:00", "stan": "znikam"})
        self.assertEqual(self.stan("# Stan: p\nTryb: nadzorowany\n")["tryb"]["tryb"], "komp")
        self.assertIsNone(self.stan("# Stan: p\nArchi żył: —\n")["tryb"])
        self.assertIsNone(self.stan("# Stan: p\nTempo: żółw\n")["tryb"])

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
        self.assertIsNone(d["tryb"])


if __name__ == "__main__":
    unittest.main()
