@echo off
echo Mendaftarkan task "ThreadsAffiliateBot" (jalan tiap 25 menit)...
schtasks /create /tn "ThreadsAffiliateBot" /tr "C:\Users\ALWI ALHUDAHADIASA\threads-affiliate-bot\run_bot.bat" /sc minute /mo 25 /f
if %errorlevel%==0 (
  echo BERHASIL. Task terdaftar.
) else (
  echo GAGAL. Jalankan file ini sebagai ADMINISTRATOR (klik kanan -> Run as admin).
)
pause
