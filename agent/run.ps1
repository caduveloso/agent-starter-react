Write-Host "Starting bitHuman Avatar Agent..." -ForegroundColor Cyan
Write-Host ""

if (-Not (Test-Path "venv")) {
    Write-Host "Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup.ps1 first." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Use the venv Python directly instead of activating
& .\venv\Scripts\python.exe agent.py dev
