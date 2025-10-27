# bitHuman Avatar Agent for LiveKit

This directory contains the Python backend agent that powers the bitHuman avatar integration with LiveKit.

## Prerequisites

1. **Docker Desktop** (required)
2. bitHuman API Secret (configured in `.env`)
3. bitHuman Avatar ID (configured in `.env` as `A48QHJ6779`)
4. OpenAI API Key (for LLM, STT, and TTS)
5. LiveKit credentials (configured in `.env`)

## Quick Start

### 1. Configure Environment Variables

Make sure you have the following in your `.env` file (in the project root):

```env
# LiveKit credentials
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=wss://your_livekit_url

# bitHuman credentials
BITHUMAN_API_SECRET=your_bithuman_api_secret
BITHUMAN_AVATAR_ID=A48QHJ6779

# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key
```

### 2. Run the Agent with Docker

From the `agent` directory:

```bash
docker compose up --build
```

That's it! The agent will start and connect to your LiveKit room.

To stop the agent, press `Ctrl+C`

## How It Works

1. The agent connects to your LiveKit room
2. When a user joins, the bitHuman avatar is rendered
3. The agent uses:
   - **Silero VAD** for voice activity detection
   - **OpenAI Whisper** for speech-to-text
   - **OpenAI GPT** for conversation
   - **OpenAI TTS** for text-to-speech
   - **bitHuman** for avatar rendering with expressions

## Using Different Avatar Configurations

### Using an Avatar ID (Current Setup)
```python
avatar = bithuman.AvatarSession(
    avatar_id="A48QHJ6779",
    model="expression"
)
```

### Using a Local .imx Model
```python
avatar = bithuman.AvatarSession(
    model_path="./your_avatar.imx",
    model="expression"
)
```

### Using an Image
```python
from PIL import Image

avatar = bithuman.AvatarSession(
    avatar_image=Image.open("avatar.jpg").convert("RGB"),
    model="expression"
)
```

## Models

- **expression**: Dynamic expressions and emotional responses (recommended)
- **essence**: Predefined actions and expressions

## Troubleshooting

### Agent not connecting
- Verify LiveKit credentials are correct
- Check that LIVEKIT_URL is accessible

### Avatar not rendering
- Verify BITHUMAN_API_SECRET is correct
- Check that avatar ID `A48QHJ6779` exists in your bitHuman account
- Check the agent logs for bitHuman-specific errors

### Voice not working
- Ensure OPENAI_API_KEY is set and valid
- Check that you have credits in your OpenAI account

## Learn More

- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [bitHuman Integration Guide](https://docs.livekit.io/agents/integrations/avatar/bithuman/)
- [bitHuman Console](https://imaginex.bithuman.ai/)
