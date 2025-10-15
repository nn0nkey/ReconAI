@echo off
echo ========================================
echo ReconAI Server Startup
echo ========================================
echo.

REM 激活虚拟环境
if exist venv\Scripts\activate.bat (
    echo [+] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [!] Virtual environment not found
    echo [!] Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo [+] Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo [+] Starting ReconAI Server...
echo [+] Server will run on http://localhost:9999
echo.
echo Press Ctrl+C to stop the server
echo.

python recon_server.py

pause



