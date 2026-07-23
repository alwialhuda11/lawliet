# THREADS AFFILIATE BOT - DEPLOYMENT GUIDE

Bot otomatis comment Threads dengan affiliate link Shopee.

## FITUR
- Multi-account (4 akun sekaligus)
- Headless mode (jalan di VPS tanpa GUI)
- Auto-detect kategori post (skincare/makeup/parfum)
- Comment Gen Z style + affiliate link

## DEPLOYMENT KE VPS UBUNTU

### Step 1: Upload ke GitHub (di Windows)
```bash
cd threads-affiliate-bot
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/USERNAME/threads-affiliate-bot.git
git push -u origin master
```

### Step 2: Clone di VPS
```bash
ssh root@VPS_IP
cd ~
git clone https://github.com/USERNAME/threads-affiliate-bot.git
cd threads-affiliate-bot
```

### Step 3: Auto Setup
```bash
bash setup-vps.sh
```

### Step 4: Login Manual (Sekali Saja)
Karena VPS headless (tanpa GUI), perlu VNC temporary buat login:

```bash
bash login-manual.sh
```

**Cara login:**
1. Download VNC Viewer: https://www.realvnc.com/download/viewer/
2. Connect ke: `VPS_IP:5900`
3. Login Threads manual di browser (4 akun)
4. Setelah selesai, tekan CTRL+C di terminal VPS

**Profile tersimpan otomatis di:** `~/chrome-profiles/`

### Step 5: Test Jalankan Bot
```bash
bash run-bot.sh
```

### Step 6: Setup Cron (Otomatis Tiap 30 Menit)
```bash
crontab -e
```

Tambahkan baris:
```
*/30 * * * * /home/root/threads-affiliate-bot/run-bot.sh >> /tmp/threads-bot.log 2>&1
```

Cek log:
```bash
tail -f /tmp/threads-bot.log
```

## STRUKTUR FILE
```
threads-affiliate-bot/
├── threads-bot.py        # Bot script utama
├── requirements.txt      # Python dependencies
├── setup-vps.sh         # Auto-setup VPS
├── run-bot.sh           # Launcher headless (production)
├── login-manual.sh      # VNC login helper (sekali pakai)
└── README.md            # Guide ini
```

## TROUBLESHOOTING

**Bot gak jalan?**
- Cek Chrome jalan: `curl http://localhost:9222/json`
- Cek log: `tail -f /tmp/threads-bot.log`

**Profile hilang / minta login lagi?**
- Ulangi Step 4 (login manual)
- Pastikan folder `~/chrome-profiles/` ada

**VNC gak connect?**
- Cek firewall VPS: `sudo ufw allow 5900`
- Cek IP VPS: `curl ifconfig.me`

## CONFIGURATION

Edit `threads-bot.py` kalau mau ubah:
- `AFFILIATE_DB` - Ganti link affiliate
- `MAX_AGE_DAYS` - Umur post max (default: 60 hari)
- `DRY_RUN = True` - Test mode (gak beneran posting)

## CREDITS
Made with ❤️ for affiliate marketing automation.
