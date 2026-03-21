# 🚀 Vaani Setup Guide

Complete step-by-step guide to get Vaani running on your machine.

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** installed ([Download](https://www.python.org/downloads/))
- **Node.js 18+** and npm installed ([Download](https://nodejs.org/))
- **Git** installed ([Download](https://git-scm.com/downloads))

## 🔑 Step 1: Get API Keys

### LiveKit Account

1. Go to [LiveKit Cloud](https://cloud.livekit.io/)
2. Sign up for a free account
3. Create a new project
4. Copy your:
   - **LiveKit URL** (e.g., `wss://your-project.livekit.cloud`)
   - **API Key**
   - **API Secret**

### OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-...`)

### ElevenLabs API Key

1. Go to [ElevenLabs](https://elevenlabs.io/)
2. Sign up for a free account
3. Go to Profile Settings → API Keys
4. Copy your API key
5. (Optional) Browse voices and copy a voice ID you like

## ⚙️ Step 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# Edit .env file with your API keys
# Use your favorite editor (nano, vim, VSCode, etc.)
nano .env
```

### Configure `.env` file:

```env
# LiveKit Configuration
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key_here
LIVEKIT_API_SECRET=your_api_secret_here

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# ElevenLabs Configuration
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Agent Configuration
AGENT_NAME=Vaani
LOG_LEVEL=INFO
```

### Test Backend Setup

```bash
# Verify imports work
python -c "import livekit; import openai; print('✅ Backend setup successful!')"
```

## 🎨 Step 3: Frontend Setup

```bash
# Open a NEW terminal window
# Navigate to client directory
cd client

# Install dependencies
npm install

# Create .env file from example
cp .env.example .env

# Edit .env file
nano .env
```

### Configure client `.env` file:

```env
VITE_LIVEKIT_URL=wss://your-project.livekit.cloud
VITE_TOKEN_SERVER_URL=http://localhost:3001
```

### Test Frontend Setup

```bash
# Start development server (just to test)
npm run dev
# Press Ctrl+C to stop after verifying it starts
```

## 🎬 Step 4: Running Vaani

You need to run **THREE** processes simultaneously. Open three terminal windows:

### Terminal 1: Token Server

```bash
cd backend
source venv/bin/activate  # Activate venv if not already active
python token_server.py
```

You should see:
```
🚀 Token server running on http://localhost:3001
📝 Generating tokens for LiveKit rooms
```

### Terminal 2: AI Agent

```bash
cd backend
source venv/bin/activate  # Activate venv if not already active
python agent.py dev
```

You should see:
```
🎙️ Starting Vaani Voice Agent
🔗 LiveKit URL: wss://your-project.livekit.cloud
```

### Terminal 3: Frontend

```bash
cd client
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

## 🎉 Step 5: Test It Out!

1. Open your browser to **http://localhost:5173**
2. You should see the beautiful Vaani landing page
3. Enter your name (e.g., "Alex")
4. Enter a room name (e.g., "test-room")
5. Click **"Join Session"**
6. Allow microphone access when prompted
7. Start talking! Say something like:
   - "Hello Vaani, can you explain quantum physics?"
   - "What is machine learning?"
   - "Teach me about photosynthesis"

## 🐛 Troubleshooting

### "Failed to connect" error

**Problem**: Token server not running or wrong URL

**Solution**:
- Ensure token server is running on port 3001
- Check `VITE_TOKEN_SERVER_URL` in client `.env`
- Check browser console for errors

### "Configuration validation failed"

**Problem**: Missing API keys in backend `.env`

**Solution**:
- Double-check all API keys are set in `backend/.env`
- Ensure no extra spaces or quotes around values
- Verify API keys are valid (not expired)

### Agent not responding

**Problem**: AI agent not running or not connected to LiveKit

**Solution**:
- Ensure agent is running (`python agent.py dev`)
- Check agent logs for errors
- Verify LiveKit credentials are correct
- Check LiveKit dashboard for active rooms

### No audio / Can't hear AI

**Problem**: Audio permissions or browser compatibility

**Solution**:
- Allow microphone access in browser
- Use Chrome, Edge, or Safari (best WebRTC support)
- Check browser audio settings
- Ensure speakers/headphones are working

### "Module not found" errors

**Problem**: Dependencies not installed

**Solution**:
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd client
npm install
```

## 📊 Monitoring

### Check LiveKit Dashboard

1. Go to [LiveKit Cloud Dashboard](https://cloud.livekit.io/)
2. Navigate to your project
3. Click on "Rooms" to see active sessions
4. Monitor participants, audio tracks, and bandwidth

### Check Agent Logs

The agent logs show real-time conversation flow:
```
🚀 Starting Vaani voice agent for room: test-room
👤 Participant joined: Alex
🎤 User started speaking
💬 User said: Hello Vaani
🤖 Agent said: Hello! I'm Vaani, your AI learning companion...
```

## 🎯 Next Steps

Now that Vaani is running, you can:

1. **Customize the System Prompt**: Edit `backend/config.py` to change teaching style
2. **Change AI Voice**: Update `ELEVENLABS_VOICE_ID` in `.env`
3. **Adjust LLM Settings**: Modify temperature, model in `backend/agent.py`
4. **Customize UI**: Edit styles in `client/src/` files
5. **Add Features**: Implement conversation history, user profiles, etc.

## 🚀 Production Deployment

For production deployment:

1. **Backend**: Deploy to cloud (AWS, GCP, Heroku)
2. **Frontend**: Deploy to Vercel, Netlify, or Cloudflare Pages
3. **LiveKit**: Use LiveKit Cloud or self-host
4. **Security**: Implement proper authentication and rate limiting
5. **Monitoring**: Add error tracking (Sentry) and analytics

## 💬 Need Help?

- Check the [LiveKit Docs](https://docs.livekit.io/)
- Review [OpenAI API Docs](https://platform.openai.com/docs)
- Check [ElevenLabs Docs](https://elevenlabs.io/docs)

---

**Enjoy learning with Vaani! 🌟**
