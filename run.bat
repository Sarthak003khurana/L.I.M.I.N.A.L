@echo off
title L.I.M.I.N.A.L. Launcher
cd /d "%~dp0"

echo ===================================================
echo             Starting L.I.M.I.N.A.L.
echo  Linguistic Inference of Missing Information via
echo               Networked Agent Logic
echo ===================================================
echo.

:: 1. First, activate the virtual environment
if exist ".venv\Scripts\activate.bat" (
    echo [*] Activating virtual environment...
    call .venv\Scripts\activate.bat
    echo [*] Virtual environment activated successfully.
) else (
    echo [!] Warning: .venv\Scripts\activate.bat not found!
)
echo.

:: 2. Check for .env file
if not exist ".env" (
    if exist ".env.example" (
        echo [*] Creating .env from .env.example...
        copy ".env.example" ".env" >nul
    )
)

:: 3. Launch Backend in a dedicated window with Python 3.11
echo [*] Launching FastAPI Backend on http://localhost:8000 ...
start "LIMINAL Backend (FastAPI :8000)" cmd /k "cd /d "%~dp0" && py -3.11 backend\main.py"

:: Wait for backend to begin loading models
ping 127.0.0.1 -n 4 >nul

:: 4. Launch Frontend in a dedicated window
echo [*] Launching React / Vite Frontend on http://localhost:5173 ...
start "LIMINAL Frontend (Vite :5173)" cmd /k "cd /d "%~dp0frontend" && npm run dev"

:: Wait for frontend dev server
ping 127.0.0.1 -n 4 >nul

:: 5. Open Default Browser
echo [*] Opening L.I.M.I.N.A.L. HUD in default browser...
start http://localhost:5173

echo.
echo ===================================================
echo  All services have been started!
echo  - Virtual Environment: Activated (.venv)
echo  - Frontend:            http://localhost:5173
echo  - Backend:             http://localhost:8000
echo  - Swagger Docs:        http://localhost:8000/docs
echo ===================================================
echo.
echo Leave the opened terminal windows running while using the app.
pause
