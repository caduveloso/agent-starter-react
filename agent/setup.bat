@echo off
echo Setting up bitHuman Avatar Agent...
echo.

echo Creating virtual environment...
python -m venv venv
echo.

echo Activating virtual environment...
call venv\Scripts\activate
echo.

echo Installing dependencies...
pip install -r requirements.txt
echo.

echo Setup complete!
echo.
echo To run the agent:
echo 1. Make sure your .env file has OPENAI_API_KEY set
echo 2. Run: venv\Scripts\activate
echo 3. Run: python agent.py dev
echo.
pause
