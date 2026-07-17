import subprocess, time, sys, os, platform, requests

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


def ensure_chrome():
    if chrome_up():
        return
    args = [CHROME_BIN, f"--remote-debugging-port={CHROME_PORT}",
            f"--user-data-dir={PROFILE_DIR}", "--remote-allow-origins=*",
            "--no-first-run", "--no-default-browser-check"]
    if HEADLESS:
        args += ["--headless=new", "--disable-gpu", "--no-sandbox"]
    subprocess.Popen(args)
    for _ in range(25):
        time.sleep(1)
        if chrome_up():
            return


if __name__ == "__main__":
    if os.path.exists(LOCK):
        print("LOCK ada, skip (run sebelumnya msh jalan)")
        sys.exit(0)
    open(LOCK, "w").close()
    try:
        ensure_chrome()
        subprocess.run([PY, "-u", BOT], cwd=HERE)
    finally:
        try:
            os.remove(LOCK)
        except Exception:
            pass
