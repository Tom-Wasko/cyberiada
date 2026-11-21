"""Seria zrzutów w jednej sesji Chrome (CDP), z wypisaniem błędów konsoli.

Użycie: python zrzuty.py URL KROK...
Kroki:  js:<kod>      wykonaj JS (wynik wypisany), potem 1 s przerwy
        png:<plik>    zrzut całej strony (do 5000 px wysokości)
        okno:<plik>   zrzut samego okna (bez przewijania)
        rozmiar:SZERxWYS[:mobile]
        czekaj:<sekundy>
        idz:<url>
Na końcu wypisuje błędy konsoli i wyjątki JS (albo „konsola: czysto”).
"""
import base64
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from cdp import CHROME, PORT, WS  # noqa: E402


class Sesja(WS):
    def __init__(self, url):
        super().__init__(url)
        self.bledy = []

    def odbierz(self):
        m = super().odbierz()
        met = m.get("method")
        if met == "Runtime.exceptionThrown":
            d = m["params"]["exceptionDetails"]
            self.bledy.append("WYJĄTEK: " + (d.get("exception", {}).get("description") or d.get("text", ""))[:400])
        elif met == "Runtime.consoleAPICalled" and m["params"]["type"] in ("error", "warning"):
            t = " ".join(str(a.get("value", a.get("description", ""))) for a in m["params"]["args"])
            self.bledy.append(m["params"]["type"].upper() + ": " + t[:400])
        elif met == "Log.entryAdded" and m["params"]["entry"]["level"] == "error":
            e = m["params"]["entry"]
            self.bledy.append("LOG: " + e.get("text", "")[:300] + " " + e.get("url", ""))
        return m


def main():
    url, *kroki = sys.argv[1:]
    prof = tempfile.mkdtemp()
    szer, wys_okna, mobile = 1400, 900, False
    ch = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                           f"--remote-debugging-port={PORT}", f"--user-data-dir={prof}",
                           f"--window-size={szer},{wys_okna}", "about:blank"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(50):
            try:
                cele = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json"))
                strona = next(c for c in cele if c["type"] == "page")
                break
            except Exception:
                time.sleep(0.2)
        ws = Sesja(strona["webSocketDebuggerUrl"])
        ws.wyslij("Page.enable")
        ws.wyslij("Runtime.enable")
        ws.wyslij("Log.enable")
        ws.wyslij("Emulation.setDeviceMetricsOverride", width=szer, height=wys_okna, deviceScaleFactor=1, mobile=False)
        ws.wyslij("Page.navigate", url=url)
        time.sleep(4)
        for k in kroki:
            co, _, arg = k.partition(":")
            if co == "js":
                r = ws.wyslij("Runtime.evaluate", expression=arg, awaitPromise=True, returnByValue=True)
                res = r.get("result", {})
                if "exceptionDetails" in res:
                    print("BŁĄD JS:", res["exceptionDetails"].get("exception", {}).get("description", "")[:300])
                w = res.get("result", {}).get("value")
                if w is not None:
                    print(w)
                time.sleep(1)
            elif co == "czekaj":
                time.sleep(float(arg))
            elif co == "idz":
                ws.wyslij("Page.navigate", url=arg)
                time.sleep(4)
            elif co == "rozmiar":
                cz = arg.split(":")
                szer, wys_okna = (int(x) for x in cz[0].split("x"))
                mobile = len(cz) > 1
                ws.wyslij("Emulation.setDeviceMetricsOverride", width=szer, height=wys_okna,
                          deviceScaleFactor=1, mobile=mobile)
                time.sleep(0.8)
            elif co in ("png", "okno"):
                if co == "png":
                    w = ws.wyslij("Runtime.evaluate", expression="document.documentElement.scrollHeight",
                                  returnByValue=True)["result"]["result"]["value"]
                    ws.wyslij("Emulation.setDeviceMetricsOverride", width=szer, height=max(wys_okna, min(int(w), 5000)),
                              deviceScaleFactor=1, mobile=mobile)
                    time.sleep(0.5)
                img = ws.wyslij("Page.captureScreenshot", format="png")["result"]["data"]
                with open(arg, "wb") as f:
                    f.write(base64.b64decode(img))
                print("zapisano", arg)
                if co == "png":
                    ws.wyslij("Emulation.setDeviceMetricsOverride", width=szer, height=wys_okna,
                              deviceScaleFactor=1, mobile=mobile)
        print("konsola:", "czysto" if not ws.bledy else "")
        for b in dict.fromkeys(ws.bledy):
            print("  ", b)
    finally:
        ch.kill()


if __name__ == "__main__":
    main()
