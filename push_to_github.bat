@echo off
title Push Abyssal Expedition to GitHub
cd /d "%~dp0"

echo ========================================================
echo   PUSHING ABYSSAL EXPEDITION TO GITHUB
echo ========================================================
echo.

git branch -M main 2>nul
git push -u origin main
if %errorlevel% neq 0 (
    echo.
    echo Trying master branch...
    git push -u origin master
)

echo.
echo ========================================================
echo  [+] Done! Check your GitHub repository.
echo ========================================================
pause
