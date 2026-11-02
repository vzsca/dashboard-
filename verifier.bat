@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"
if "%~1"=="" (
  echo Utilisation : verifier.bat V1   ^(V1 a V6 ou "tout"^)
  "python\python.exe" vigie\verifier.py tout
) else (
  "python\python.exe" vigie\verifier.py %*
)
echo.
pause
