@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"
echo Ouverture de 3 ports de demo sur 127.0.0.1 (ton poste uniquement).
"python\python.exe" vigie\demo\services_demo.py
pause
