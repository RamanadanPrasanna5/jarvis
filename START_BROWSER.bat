@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
 .venv\Scripts\python.exe main.py --browser
) else (
 python main.py --browser
)
pause
