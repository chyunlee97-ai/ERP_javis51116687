@echo off
cd /d "%~dp0"
start "ERP Server" /MIN python server\main.py
timeout /t 3 /nobreak > nul
start "ERP Client" pythonw client\main.py
exit
