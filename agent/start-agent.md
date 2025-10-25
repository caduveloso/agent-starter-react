# Starting the bitHuman Agent

## Method 1: Using PowerShell Script (Recommended)

```powershell
.\run.ps1
```

## Method 2: Using Batch File (Command Prompt)

```cmd
run.bat
```

## Method 3: Manual Commands (PowerShell)

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the agent
python agent.py dev
```

## Method 4: Manual Commands (Command Prompt)

```cmd
# Activate virtual environment
venv\Scripts\activate

# Run the agent
python agent.py dev
```

## What You Should See

When the agent starts successfully, you'll see:

```
INFO:voice-agent:Connecting to room voice_assistant_room_XXXX
INFO:voice-agent:Starting bitHuman avatar...
INFO:voice-agent:Starting agent session...
INFO:voice-agent:Agent is ready and waiting for participants
```

## Troubleshooting

### "Execution of scripts is disabled on this system"

If you get this error in PowerShell, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try again.

### "OPENAI_API_KEY not set"

Make sure you added your OpenAI API key to the `.env` file in the project root.

### "Module not found"

Make sure you ran the setup first:

```powershell
.\setup.ps1
```
