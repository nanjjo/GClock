@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" gclock.py
) else (
    python gclock.py
)
if errorlevel 1 pause
