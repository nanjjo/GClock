@echo off
setlocal
cd /d "%~dp0"
if not exist ".build-temp" mkdir ".build-temp"
set "TEMP=%CD%\.build-temp"
set "TMP=%TEMP%"
set "PYINSTALLER_CONFIG_DIR=%CD%\.build-temp\pyinstaller"
if exist ".venv\Scripts\python.exe" goto dependencies
where py >nul 2>nul
if errorlevel 1 goto usepython
py -3 -m venv .venv
if errorlevel 1 goto failed
goto dependencies
:usepython
python -m venv .venv
if errorlevel 1 goto failed
:dependencies
".venv\Scripts\python.exe" -m ensurepip --upgrade
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip install -r requirements-build.txt
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m unittest test_gclock.py test_gclock_ui.py test_audio_player.py test_display.py test_settings.py
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onefile --windowed --manifest "%CD%\windows.manifest" --hidden-import _cffi_backend --add-data "%CD%\THIRD_PARTY_NOTICES.txt;." --name GClock --distpath dist --workpath build\python --specpath build gclock.py
if errorlevel 1 goto failed
".venv\Scripts\python.exe" verify_executable.py
if errorlevel 1 goto failed
echo.
echo Build succeeded: %CD%\dist\GClock.exe
exit /b 0
:failed
echo.
echo Build failed. See the error above. Python is required on the build PC only.
exit /b 1
