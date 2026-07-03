@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
start "ERP Server" /MIN python server\main.py
timeout /t 3 /nobreak > nul
start "ERP Client" pythonw client\main.py
exit
