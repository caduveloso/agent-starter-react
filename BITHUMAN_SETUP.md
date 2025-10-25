# bitHuman Avatar Integration Setup Guide

This guide will help you set up and run the bitHuman avatar agent with your LiveKit application.

## Overview

Your bitHuman avatar agent is configured with:
- **Avatar ID**: `A48QHJ6779`
- **bitHuman API Secret**: Already configured in `.env`
- **LiveKit Credentials**: Already configured in `.env`

## Prerequisites

Before you begin, make sure you have:

1. ✅ Python 3.9 or higher (You have Python 3.13.3)
2. ✅ bitHuman API Secret (Already in `.env`)
3. ✅ bitHuman Avatar ID (Already in `.env`)
4. ✅ LiveKit credentials (Already in `.env`)
5. ❌ OpenAI API Key (You need to add this)

## Step 1: Get Your OpenAI API Key

The agent uses OpenAI for:
- Speech-to-Text (Whisper)
- Language Model (GPT)
- Text-to-Speech (TTS)

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key
4. Open `.env` file in the project root
5. Add your key to the `OPENAI_API_KEY` line:
   ```env
   OPENAI_API_KEY=sk-your-api-key-here
   ```

## Step 2: Install Python Agent Dependencies

### Option A: Using the Setup Script (Recommended for Windows)

1. Open a terminal in the project root
2. Run:
   ```bash
   cd agent
   setup.bat
   ```

### Option B: Manual Installation

1. Open a terminal and navigate to the `agent` directory:
   ```bash
   cd agent
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Step 3: Run the Agent

### Option A: Using the Run Script (Windows)

From the `agent` directory:
```bash
run.bat
```

### Option B: Manual Run

1. Make sure the virtual environment is activated:
   ```bash
   venv\Scripts\activate
   ```

2. Run the agent:
   ```bash
   python agent.py dev
   ```

You should see output like:
```
INFO:voice-agent:Agent is ready and waiting for participants
```

## Step 4: Run the Frontend

In a **new terminal** (keep the agent running):

1. Navigate to the project root
2. Install frontend dependencies (if not already done):
   ```bash
   pnpm install
   ```

3. Run the development server:
   ```bash
   pnpm dev
   ```

4. Open your browser to `http://localhost:3000`

## Step 5: Test the Integration

1. Click "Start call" in the web interface
2. Allow microphone access when prompted
3. You should see your bitHuman avatar appear
4. Start talking - the avatar will listen and respond with expressions

## Architecture

Here's how it works:

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Browser   │ ◄─────► │   LiveKit    │ ◄─────► │   Python    │
│  (Next.js)  │         │    Server    │         │    Agent    │
└─────────────┘         └──────────────┘         └─────────────┘
                                                         │
                                                         ▼
                                                  ┌─────────────┐
                                                  │  bitHuman   │
                                                  │   Avatar    │
                                                  └─────────────┘
                                                         │
                                                         ▼
                                                  ┌─────────────┐
                                                  │   OpenAI    │
                                                  │ (STT/LLM/   │
                                                  │    TTS)     │
                                                  └─────────────┘
```

1. **Browser**: User interface where you interact with the avatar
2. **LiveKit Server**: Handles real-time communication (video/audio)
3. **Python Agent**: Runs the AI logic and avatar rendering
4. **bitHuman**: Renders the avatar with expressions
5. **OpenAI**: Provides voice recognition, AI responses, and voice synthesis

## Customization

### Change the Avatar Model Type

In `agent/agent.py`, you can change the model type:

```python
avatar = bithuman.AvatarSession(
    avatar_id=os.getenv("BITHUMAN_AVATAR_ID", "A48QHJ6779"),
    model="expression",  # or "essence"
)
```

- **expression**: Dynamic expressions and emotional responses (recommended)
- **essence**: Predefined actions and expressions

### Use a Different Avatar

If you want to use a different avatar from your bitHuman account:

1. Get the avatar ID from the [bitHuman ImagineX console](https://imaginex.bithuman.ai/)
2. Update `BITHUMAN_AVATAR_ID` in `.env`

### Customize the AI Personality

Edit the system prompt in `agent/agent.py`:

```python
initial_ctx = llm.ChatContext().append(
    role="system",
    text=(
        "Your custom personality here..."
    ),
)
```

## Troubleshooting

### "Module not found" errors
- Make sure you activated the virtual environment
- Run `pip install -r requirements.txt` again

### Avatar not appearing
- Check that `BITHUMAN_API_SECRET` is correct in `.env`
- Verify the avatar ID `A48QHJ6779` exists in your bitHuman account
- Check the agent logs for errors

### No voice/audio
- Make sure `OPENAI_API_KEY` is set and valid
- Check your OpenAI account has credits
- Verify your browser allowed microphone access

### Agent won't start
- Check all environment variables are set in `.env`
- Make sure LiveKit credentials are correct
- Check Python version is 3.9+

### Connection issues
- Verify `LIVEKIT_URL` is accessible
- Check firewall settings
- Make sure both the agent and frontend are running

## Learn More

- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [bitHuman Integration Guide](https://docs.livekit.io/agents/integrations/avatar/bithuman/)
- [bitHuman Console](https://imaginex.bithuman.ai/)
- [OpenAI Platform](https://platform.openai.com/)

## Support

If you encounter issues:
1. Check the agent logs for error messages
2. Check the browser console for frontend errors
3. Verify all API keys are valid and have credits
4. Make sure your LiveKit account is active
