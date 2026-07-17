import subprocess, time, sys, os, platform, requests, json, websocket

IS_WIN = platform.system() == "Windows"


def env(name, default):
    return os.environ.get(name, default)


CHROME_HOST = env("CHROME_HOST", "localhost")
CHROME_PORT = int(env("CHROME_PORT", "9222"))
HEADLESS = env("HEADLESS", "false").lower() in ("1", "true", "yes")

# Chrome binary: Windows default vs Linux/VPS
DEFAULT_WIN = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CHROME_BIN = env("CHROME_BIN", DEFAULT_WIN if IS_WIN else "google-chrome")

# Profile dir for the remote-debugging Chrome instance
DEFAULT_PROFILE_WIN = r"C:\Users\ALWI ALHUDAHADIASA\AppData\Local\Google\Chrome\Profile_Bot"
DEFAULT_PROFILE_LINUX = os.path.expanduser("~/.threads-bot-profile")
PROFILE_DIR = env("CHROME_PROFILE", DEFAULT_PROFILE_WIN if IS_WIN else DEFAULT_PROFILE_LINUX)

HERE = os.path.dirname(os.path.abspath(__file__))
BOT = os.path.join(HERE, "threads-bot.py")
PY = sys.executable
LOCK = os.path.join(HERE, "run.lock")


def chrome_up():
    try:
        return requests.get(f"http://{CHROME_HOST}:{CHROME_PORT}/json/version", timeout=3).status_code == 200
    except Exception:
        return False


def chrome_ws_ok():
    """Cek koneksi WebSocket CDP beneran (HTTP 200 belum tentu WS jalan)."""
    try:
        r = requests.get(f"http://{CHROME_HOST}:{CHROME_PORT}/json", timeout=5)
        pages = r.json()
        if not pages:
            return False
        ws = websocket.create_connection(pages[0]["webSocketDebuggerUrl"], timeout=8)
        ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate",
                            "params": {"expression": "1+1"}}))
        ws.recv()
        ws.close()
        return True
    except Exception:
        return False


def kill_debug_chrome():
    """Kill hanya Chrome yg listen di port debugging (gak sentuh Chrome biasa)."""
    try:
        out = subprocess.run("netstat -ano | findstr :%s" % CHROME_PORT,
                             shell=True, capture_output=True, text=True).stdout
        pids = set()
        for line in out.splitlines():
            if "LISTENING" in line:
                pids.add(line.split()[-1])
        for pid in pids:
            subprocess.run(f"taskkill /F /PID {pid} /T", shell=True,
                           capture_output=True)
    except Exception:
        pass


def ensure_chrome():
    if chrome_up() and chrome_ws_ok():
        return
    if chrome_up() and not chrome_ws_ok():
        print("Chrome HTTP up tapi WS stale -> restart")
        kill_debug_chrome()
        time.sleep(2)
    args = [CHROME_BIN, f"--remote-debugging-port={CHROME_PORT}",
            f"--user-data-dir={PROFILE_DIR}", "--remote-allow-origins=*",
            "--no-first-run", "--no-default-browser-check"]
    if HEADLESS:
        args += ["--headless=new", "--disable-gpu", "--no-sandbox"]
    subprocess.Popen(args)
    for _ in range(25):
        time.sleep(1)
        if chrome_up() and chrome_ws_ok():
            return


if __name__ == "__main__":
    if os.path.exists(LOCK):
        print("LOCK ada, skip (run sebelumnya msh jalan)")
        sys.exit(0)
    open(LOCK, "w").close()
    log_path = os.path.join(HERE, "bot.log")
    try:
        ensure_chrome()
        with open(log_path, "a", encoding="utf-8") as log:
            log.write("\n===== RUN %s =====\n" % time.strftime("%Y-%m-%d %H:%M:%S"))
            subprocess.run([PY, "-u", BOT], cwd=HERE, stdout=log, stderr=subprocess.STDOUT)
    finally:
        try:
            os.remove(LOCK)
        except Exception:
            pass
