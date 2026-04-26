# 🎙️ Vaani Voice Agent

A real-time AI voice conversation system for interactive teaching and learning. Built with LiveKit for WebRTC streaming, Python for the AI agent backend, and React for the client interface.

## 🏗️ Architecture

```
┌──────────────────────────────────────────────┐
│                  USER                        │
│        (Browser / Mobile App)                │
│                                              │
│  🎤 Mic Input        🔊 Speaker Output        │
│                                              │
│  (React + LiveKit SDK)                        │
└───────────────▲──────────────────────────────┘
                │  WebRTC Audio Stream
                │
┌───────────────┴──────────────────────────────┐
│              LIVEKIT SERVER                   │
│        (LiveKit Cloud / Self-hosted)          │
│                                              │
│  • Real-time audio routing                   │
│  • Room / session management                 │
│  • Low-latency streaming                     │
│  • Interrupt handling                        │
└───────────────▲──────────────────────────────┘
                │  Audio Frames (16kHz PCM)
                │
┌───────────────┴──────────────────────────────┐
│              AI VOICE AGENT                  │
│          (Python + LiveKit Agents SDK)        │
│                                              │
│  1️⃣ Audio Ingestion (LiveKit)                 │
│  2️⃣ Speech → Text (Whisper)                   │
│  3️⃣ Conversation Intelligence (GPT-4o)        │
│  4️⃣ Response Generation                       │
│  5️⃣ Text → Speech (ElevenLabs)                │
│  6️⃣ Audio Publisher (LiveKit)                 │
└──────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- LiveKit Cloud account (or self-hosted LiveKit server)
- OpenAI API key
- ElevenLabs API key

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the agent
python agent.py dev
```

### Frontend Setup

```bash
cd client
npm install
npm run dev
```

Open http://localhost:5173 in your browser and start talking to Vaani! 🎤

## 🔑 Environment Variables

### Backend (.env)

```env
# LiveKit Configuration
LIVEKIT_URL=wss://your-livekit-server.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# OpenAI (for Whisper STT and GPT-4o)
OPENAI_API_KEY=your_openai_api_key

# ElevenLabs (for TTS)
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Default: Rachel

# Agent Configuration
AGENT_NAME=Vaani
SYSTEM_PROMPT=You are Vaani, an expert AI teacher...
```

### Frontend (.env)

```env
VITE_LIVEKIT_URL=wss://your-livekit-server.livekit.cloud
```

## 📚 Features

- ✅ Real-time voice conversation with AI
- ✅ Low-latency audio streaming (< 500ms)
- ✅ Natural interruption handling
- ✅ Context-aware responses
- ✅ Teacher-style explanations
- ✅ Beautiful, modern UI
- ✅ Mobile-responsive design

## 🛠️ Tech Stack

- **Frontend**: React + Vite + LiveKit SDK
- **Backend**: Python + LiveKit Agents SDK
- **STT**: OpenAI Whisper
- **LLM**: GPT-4o
- **TTS**: ElevenLabs
- **WebRTC**: LiveKit

## 📖 Documentation

- [Architecture Overview](docs/architecture.md)
- [API Documentation](docs/api.md)
- [Deployment Guide](docs/deployment.md)

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines first.

## 📄 License

MIT License - see LICENSE file for details

---

Built with ❤️ by the Vaani team
 
 
 
 
 
 
 
 
 
