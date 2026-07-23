#!/bin/bash
# run-bot.sh - Jalankan bot headless (tanpa GUI) menggunakan Xvfb
# Usage: bash run-bot.sh

echo "=========================================="
echo "Starting Threads Affiliate Bot (Headless)"
echo "=========================================="

# Kill existing processes
pkill -f chromium 2>/dev/null
pkill -f Xvfb 2>/dev/null
sleep 2

# Start Xvfb (virtual display)
echo "[1/4] Starting Xvfb..."
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
sleep 1

# Chrome profiles (ubah path kalau beda)
PROFILE_DIR="$HOME/chrome-profiles"

# Start Chromium for each account
echo "[2/4] Starting Chromium instances..."

# Account 1
chromium-browser \
  --remote-debugging-port=9222 \
  --user-data-dir="$PROFILE_DIR/akun1" \
  --headless --no-sandbox \
  --remote-allow-origins=* &
sleep 2

# Account 2
chromium-browser \
  --remote-debugging-port=9223 \
  --user-data-dir="$PROFILE_DIR/akun2" \
  --headless --no-sandbox \
  --remote-allow-origins=* &
sleep 2

# Account 3
chromium-browser \
  --remote-debugging-port=9224 \
  --user-data-dir="$PROFILE_DIR/akun3" \
  --headless --no-sandbox \
  --remote-allow-origins=* &
sleep 2

# Account 4
chromium-browser \
  --remote-debugging-port=9225 \
  --user-data-dir="$PROFILE_DIR/akun4" \
  --headless --no-sandbox \
  --remote-allow-origins=* &
sleep 3

# Run bots
echo "[3/4] Running bots..."
cd "$(dirname "$0")"

# Account 1
echo "--- Account 1: user529362927 ---"
export THREADS_USERNAME=user529362927
export CHROME_PORT=9222
python3 threads-bot.py

# Account 2
echo "--- Account 2: selenasupply ---"
export THREADS_USERNAME=selenasupply
export CHROME_PORT=9223
python3 threads-bot.py

# Account 3
echo "--- Account 3: cellinecorner ---"
export THREADS_USERNAME=cellinecorner
export CHROME_PORT=9224
python3 threads-bot.py

# Account 4
echo "--- Account 4: oliviapickss ---"
export THREADS_USERNAME=oliviapickss
export CHROME_PORT=9225
python3 threads-bot.py

# Done
echo "[4/4] All bots finished."
echo "Check log: tail -f /tmp/threads-bot.log"
