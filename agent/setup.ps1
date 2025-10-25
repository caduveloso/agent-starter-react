Write-Host "Setting up bitHuman Avatar Agent..." -ForegroundColor Cyan
Write-Host ""

Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv
Write-Host ""

Write-Host "Installing dependencies..." -ForegroundColor Yellow
& .\venv\Scripts\python.exe -m pip install -r requirements.txt
Write-Host ""

Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To run the agent:" -ForegroundColor Cyan
Write-Host "1. Make sure your .env file has OPENAI_API_KEY set"
Write-Host "2. Run: .\run.ps1"
Write-Host ""
Read-Host "Press Enter to continue"
