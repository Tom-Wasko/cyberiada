import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from przenies import przenies  # noqa: E402

PLIK = "# Zadania\r\nNastępny numer: Z6\r\n\r\n## W toku\r\n\r\n## Zaplanowane\r\n- Z1 · jeden\r\n  - szczegół\r\n- Z2 · dwa\r\n\r\n## Odłożone\r\n"


class TestPrzenies(unittest.TestCase):
    def test_nowa_sekcja_i_podpunkty(self):
        t, z = przenies(PLIK, {"Z1": "nastepnie"})
        self.assertEqual(z, ["Z1 → Następnie"])
        self.assertIn("## W toku\r\n\r\n## Następnie\r\n- Z1 · jeden\r\n  - szczegół\r\n\r\n## Zaplanowane\r\n- Z2 · dwa", t)
        self.assertNotIn("\n\n\n", t.replace("\r", ""))

    def test_do_istniejacej_i_brak_zadania(self):
        t, z = przenies(PLIK, {"Z2": "w_toku", "Z9": "odlozone"})
        self.assertEqual(z, ["Z2 → W toku"])
        self.assertIn("## W toku\r\n- Z2 · dwa\r\n\r\n## Zaplanowane\r\n- Z1 · jeden\r\n  - szczegół\r\n\r\n## Odłożone", t)


if __name__ == "__main__":
    unittest.main()
