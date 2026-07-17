# Threads Affiliate Comment Bot

Bot auto-komen Threads dengan link affiliate Shopee pada post yang relevan
(skincare / makeup / parfum). Satu run = satu komentar di 1 post viral/relevan.
Jalan di Windows maupun Linux/VPS (portable via environment variable).

## Cara kerja singkat
1. Buka Chrome dengan remote-debugging aktif (port 9222).
2. Bot scan search Threads (mode viral = tab "Top", atau newest = tab "Recent").
3. Pilih post pertama yang cocok kategori, ketik komentar + link, kirim.
4. Catat post ke `posted.txt` biar gak repeat di run berikutnya.
5. Filter umur: cuma comment post ≤ `MAX_AGE_DAYS` hari (default 60 = 2 bulan).
   Post lebih tua di-skip otomatis biar gak nyomentarin post basi yg jarang dibuka.

## Setup Windows (lokal)
1. Install Python 3.11 + pip install -r requirements.txt
2. Jalankan Chrome debug (pakai profile terpisah, default "User Data" ditolak Chrome):
   ```
   "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
     --remote-debugging-port=9222 ^
     --user-data-dir="C:\Users\ALWI ALHUDAHADIASA\AppData\Local\Google\Chrome\Profile_Bot" ^
     --remote-allow-origins=* --no-first-run --no-default-browser-check
   ```
3. Login Threads sekali di profile itu, biarkan Chrome nyala.
4. Tes dulu (DRY_RUN): set `DRY_RUN = True` di threads-bot.py, lalu:
   ```
   python threads-bot.py
   ```
5. Kalau OK, set `DRY_RUN = False`, lalu jalankan otomatis tiap 25 mnt:
   - Klik kanan `install_task.bat` → Run as administrator (daftarkan Task Scheduler).
   - Atau manual: `python run_scheduled.py` (ini juga otomatis nyalain Chrome kalau mati).

## Setup VPS / Linux (headless)
1. Install Chromium: `sudo apt install chromium` (atau `google-chrome-stable`).
2. `pip install -r requirements.txt`
3. Siapkan profile yg SUDAH LOGIN Threads (paling gampang: copy folder
   `Profile_Bot` dari Windows ke VPS, taruh di `~/.threads-bot-profile`).
   Atau jalankan sekali tanpa headless + pakai Xvfb/display buat login.
4. Jalankan (headless):
   ```
   export CHROME_BIN=google-chrome
   export CHROME_PROFILE=$HOME/.threads-bot-profile
   export HEADLESS=true
   python run_scheduled.py
   ```
   run_scheduled.py akan nyalain Chrome headless (+--remote-debugging-port=9222)
   dan menjalankan bot. Lock file mencegah overlap antar run.
5. Biar jalan terus: pakai cron / systemd / screen. Contoh cron tiap 25 mnt:
   ```
   */25 * * * * cd /path/threads-affiliate-bot && /usr/bin/python3 run_scheduled.py >> bot.log 2>&1
   ```

## Konfigurasi (environment variable, opsional)
| Var             | Default (Win)                                  | Default (Linux)            |
|-----------------|------------------------------------------------|----------------------------|
| CHROME_HOST     | localhost                                      | localhost                  |
| CHROME_PORT     | 9222                                           | 9222                       |
| CHROME_BIN      | ...\Chrome\Application\chrome.exe              | google-chrome              |
| CHROME_PROFILE  | ...\Chrome\Profile_Bot                         | ~/.threads-bot-profile     |
| HEADLESS        | false                                          | false                      |
| MAX_AGE_DAYS    | 60                                             | 60                         |

Lihat `config.env.example`.

## File penting
- `threads-bot.py`    → inti bot (edit YOUR_USERNAME & AFFILIATE_DB di dalamnya).
- `run_scheduled.py`  → runner: pastikan Chrome nyala + jalankan bot + lock.
- `affiliate-links.txt` → export 45 link (backup; AFFILIATE_DB di script yg dipakai).
- `posted.txt` / `last_comment.txt` → state runtime (gitignored, regenerate otomatis).

## Catatan safety
- 1 akun komentar berulang = risiko ToS/spam Threads. Jaga interval >= 20–30 mnt & variasi teks.
- Multi-akun butuh profile Chrome terpisah + port beda (9223, 9224…) + proxy tiap akun.
