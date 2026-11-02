@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist "_depart\vigie" (
  echo Le dossier _depart\ est absent : impossible de repartir de zero.
  pause
  exit /b 1
)
echo ATTENTION : ton code du dossier vigie\ sera remplace par la version de depart.
set /p REP=Tape O puis Entree pour confirmer :
if /i not "%REP%"=="O" (
  echo Annule, rien n'a ete modifie.
  pause
  exit /b 0
)
if exist "rapports" rmdir /s /q "rapports"
rmdir /s /q "vigie"
xcopy "_depart\vigie" "vigie\" /e /i /q >nul
echo Termine. Le dossier vigie\ est revenu a son etat de depart.
pause
