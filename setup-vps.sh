#!/bin/bash
# setup-vps.sh - Auto setup Threads Affiliate Bot di Ubuntu VPS
# Jalankan: bash setup-vps.sh

echo "=========================================="
echo "THREADS AFFILIATE BOT - VPS SETUP"
echo "=========================================="

# 1. Update system
echo "[1/6] Updating system..."
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
echo "[2/6] Installing dependencies..."
sudo apt install -y chromium-browser python3 python3-pip git xvfb x11vnc curl

# 3. Install Python packages
echo "[3/6] Installing Python packages..."
pip3 install -r requirements.txt

# 4. Create Chrome profiles directory
echo "[4/6] Creating Chrome profiles directory..."
mkdir -p ~/chrome-profiles/{akun1,akun2,akun3,akun4}

# 5. Make scripts executable
echo "[5/6] Making scripts executable..."
chmod +x run-bot.sh login-manual.sh

# 6. Done
echo "[6/6] Setup complete!"
echo ""
echo "=========================================="
echo "NEXT STEPS:"
echo "=========================================="
echo "1. Login manual (sekali saja):"
echo "   bash login-manual.sh"
echo ""
echo "2. Setelah login sukses, jalankan bot:"
echo "   bash run-bot.sh"
echo ""
echo "3. Setup cron (optional):"
echo "   crontab -e"
echo "   Tambahkan: */30 * * * * /home/$USER/threads-affiliate-bot/run-bot.sh >> /tmp/threads-bot.log 2>&1"
echo "=========================================="
