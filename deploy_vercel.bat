@echo off
title Deploy Abyssal Expedition to Vercel
cd /d "%~dp0"

echo ========================================================
echo   DEPLOYING ABYSSAL EXPEDITION TO VERCEL
echo ========================================================
echo.

echo Checking Vercel authentication...
vercel whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [!] You are not currently logged in to Vercel.
    echo Please log in below (opens browser or prompts for email):
    echo.
    vercel login
    if %errorlevel% neq 0 (
        echo.
        echo [X] Login failed or cancelled.
        pause
        exit /b %errorlevel%
    )
)

echo.
echo [*] Authenticated! Deploying project to Vercel Production...
echo.
vercel --prod --yes

echo.
echo ========================================================
echo  [+] Deployment complete! Your live game URL is above.
echo ========================================================
pause
