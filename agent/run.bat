@echo off
echo Starting bitHuman Avatar Agent...
echo.

if not exist venv (
    echo Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate
python agent.py dev
