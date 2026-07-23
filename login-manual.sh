#!/bin/bash
# login-manual.sh - Login manual via VNC (sekali pakai)
# Usage: bash login-manual.sh
# Setelah login sukses, profile tersimpan otomatis

echo "=========================================="
echo "MANUAL LOGIN - THREADS AFFILIATE BOT"
echo "=========================================="
echo ""
echo "INSTRUKSI:"
echo "1. Script ini akan buka VNC server"
echo "2. Connect pakai VNC Viewer ke VPS_IP:5900"
echo "3. Login Threads manual (4 akun)"
echo "4. Setelah selesai, tekan CTRL+C di terminal ini"
echo ""

# Kill existing
pkill -f chromium 2>/dev/null
pkill -f Xvfb 2>/dev/null
pkill -f x11vnc 2>/dev/null
sleep 2

# Start Xvfb
echo "[1/3] Starting Xvfb..."
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
sleep 1

# Start Chromium (non-headless, with GUI via VNC)
echo "[2/3] Starting Chromium (VNC mode)..."
PROFILE_DIR="$HOME/chrome-profiles"

# Buka 4 profile sekaligus (bisa login bergantian)
chromium-browser --remote-debugging-port=9222 --user-data-dir="$PROFILE_DIR/akun1" &
sleep 2
chromium-browser --remote-debugging-port=9223 --user-data-dir="$PROFILE_DIR/akun2" &
sleep 2
chromium-browser --remote-debugging-port=9224 --user-data-dir="$PROFILE_DIR/akun3" &
sleep 2
chromium-browser --remote-debugging-port=9225 --user-data-dir="$PROFILE_DIR/akun4" &

# Start VNC
echo "[3/3] Starting VNC server..."
echo "VNC Password: threads123"
x11vnc -display :99 -forever -nopw -listen 0.0.0.0 -xkb -rfbport 5900 &

echo ""
echo "=========================================="
echo "VNC READY!"
echo "=========================================="
echo "1. Download VNC Viewer: https://www.realvnc.com/download/viewer/"
echo "2. Connect ke: $(curl -s ifconfig.me):5900"
echo "3. Login Threads di browser yang terbuka"
echo "4. Setelah selesai, tekan CTRL+C di sini"
echo "=========================================="

# Keep running
wait
