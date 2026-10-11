@echo off
setlocal
cd /d "%~dp0"
echo.
echo   JARVIS - Desktop setup
echo   ----------------------
where py >nul 2>nul
if errorlevel 1 goto usepython
py -3.12 -c "import sys" >nul 2>nul
if errorlevel 1 goto usepython
py -3.12 -m venv .venv
if errorlevel 1 goto fail
goto install
:usepython
python -c "import sys; assert (3,10) <= sys.version_info[:2] <= (3,13)" >nul 2>nul
if errorlevel 1 goto missing
python -m venv .venv
if errorlevel 1 goto fail
:install
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto browseronly
echo.
echo Setup complete. Double-click START_JARVIS.bat.
echo For AI chat, install Ollama and follow START_HERE.md.
pause
exit /b 0
:browseronly
echo.
echo The desktop window could not be installed. Browser mode is ready.
echo Double-click START_BROWSER.bat. See START_HERE.md for help.
pause
exit /b 0
:missing
echo Install Python 3.12 for Windows from https://www.python.org/downloads/
echo Check "Add python.exe to PATH" during installation, then run this again.
pause
exit /b 1
:fail
echo Setup failed. Copy the error above or read START_HERE.md.
pause
exit /b 1
