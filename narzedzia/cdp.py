"""Minimalny klient Chrome DevTools Protocol (bez bibliotek): zrzuty ekranu po wykonaniu JS na stronie.

Użycie: python cdp.py URL PLIK.png [JS ...]   – każdy JS wykonywany po kolei z odstępem 1,5 s, potem zrzut.
Zmienne środowiskowe: CHROME_PATH (domyślnie Chrome w Program Files), CDP_PORT (domyślnie 9333).
"""
import base64
import json
import os
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.request

CHROME = os.environ.get("CHROME_PATH", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
PORT = int(os.environ.get("CDP_PORT", "9333"))


class WS:
    def __init__(self, url):
        host, path = url[len("ws://"):].split("/", 1)
        h, p = host.split(":")
        self.s = socket.create_connection((h, int(p)))
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((f"GET /{path} HTTP/1.1\r\nHost: {host}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                        f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += self.s.recv(4096)
        self.reszta = buf.split(b"\r\n\r\n", 1)[1]
        self.n = 0

    def _czytaj(self, n):
        while len(self.reszta) < n:
            self.reszta += self.s.recv(1 << 20)
        d, self.reszta = self.reszta[:n], self.reszta[n:]
        return d

    def wyslij(self, metoda, **params):
        self.n += 1
        dane = json.dumps({"id": self.n, "method": metoda, "params": params}).encode()
        maska = os.urandom(4)
        dl = len(dane)
        nag = bytes([0x81]) + (bytes([0x80 | dl]) if dl < 126 else bytes([0x80 | 126]) + struct.pack(">H", dl)
                               if dl < 65536 else bytes([0x80 | 127]) + struct.pack(">Q", dl))
        self.s.sendall(nag + maska + bytes(b ^ maska[i % 4] for i, b in enumerate(dane)))
        while True:
            m = self.odbierz()
            if m.get("id") == self.n:
                return m

    def odbierz(self):
        dane = b""
        while True:
            b1, b2 = self._czytaj(2)
            dl = b2 & 0x7F
            if dl == 126:
                dl = struct.unpack(">H", self._czytaj(2))[0]
            elif dl == 127:
                dl = struct.unpack(">Q", self._czytaj(8))[0]
            dane += self._czytaj(dl)
            if b1 & 0x80:
                return json.loads(dane)


def main():
    if len(sys.argv) < 3 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0 if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help") else 2)
    url, plik, *skrypty = sys.argv[1:]
    prof = tempfile.mkdtemp()
    ch = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--remote-debugging-port={PORT}",
                           f"--user-data-dir={prof}", "--window-size=1400,1000", "about:blank"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(50):
            try:
                cele = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json"))
                strona = next(c for c in cele if c["type"] == "page")
                break
            except Exception:
                time.sleep(0.2)
        ws = WS(strona["webSocketDebuggerUrl"])
        ws.wyslij("Page.enable")
        ws.wyslij("Page.navigate", url=url)
        time.sleep(5)
        for js in skrypty:
            r = ws.wyslij("Runtime.evaluate", expression=js, awaitPromise=True, returnByValue=True)
            wynik = r.get("result", {}).get("result", {}).get("value")
            if wynik is not None:
                print(wynik)
            time.sleep(1.5)
        wys = ws.wyslij("Runtime.evaluate", expression="document.documentElement.scrollHeight", returnByValue=True)["result"]["result"]["value"]
        ws.wyslij("Emulation.setDeviceMetricsOverride", width=1400, height=min(int(wys), 6000), deviceScaleFactor=1, mobile=False)
        time.sleep(0.5)
        img = ws.wyslij("Page.captureScreenshot", format="png")["result"]["data"]
        with open(plik, "wb") as f:
            f.write(base64.b64decode(img))
        print("zapisano", plik)
    finally:
        ch.kill()


if __name__ == "__main__":
    main()
