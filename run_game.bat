@echo off
title Abyssal Expedition: Deep Sea Submarine
cd /d "%~dp0"

echo ====================================================
echo  ABYSSAL EXPEDITION: DEEP SEA SUBMARINE
echo  Multimedia Systems Lab - Lab Test 2
echo ====================================================

if exist ".venv\Scripts\python.exe" (
    echo Launching with virtual environment...
    ".venv\Scripts\python.exe" main.py
) else (
    echo Launching with system Python...
    python main.py
)

pause
