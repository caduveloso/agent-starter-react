Write-Host "Starting Voice-Only Agent (without bitHuman avatar)..." -ForegroundColor Cyan
Write-Host ""

if (-Not (Test-Path "venv")) {
    Write-Host "Virtual environment not found!" -ForegroundColor Red
    Write-Host "Creating virtual environment and installing dependencies..." -ForegroundColor Yellow
    python -m venv venv
    & .\venv\Scripts\python.exe -m pip install -r requirements_voice_only.txt
}

Write-Host "Running voice-only agent..." -ForegroundColor Green
# Use the venv Python directly
& .\venv\Scripts\python.exe agent_voice_only.py dev
