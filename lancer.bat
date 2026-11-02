@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"
if not exist "python\python.exe" (
  echo Le dossier python\ est introuvable. Extrais bien tout le zip, sans deplacer lancer.bat.
  pause
  exit /b 1
)
"python\python.exe" vigie\main.py
echo.
pause
