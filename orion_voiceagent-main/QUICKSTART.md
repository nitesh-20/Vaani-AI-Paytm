# 🎯 Vaani Quick Reference

## 🚀 Quick Start Commands

```bash
# One-command start (recommended)
./start.sh

# Or manually start each service:

# Terminal 1: Token Server
cd backend && source venv/bin/activate && python token_server.py

# Terminal 2: AI Agent
cd backend && source venv/bin/activate && python agent.py dev

# Terminal 3: Frontend
cd client && npm run dev
```

## 🛑 Stop Services

```bash
./stop.sh
```

## 📁 Project Structure

```
orion-voiceagent/
├── backend/
│   ├── agent.py              # Main AI voice agent
│   ├── config.py             # Configuration management
│   ├── token_server.py       # Token generation server
│   ├── requirements.txt      # Python dependencies
│   ├── .env                  # Environment variables (create from .env.example)
│   └── .env.example          # Environment template
│
├── client/
│   ├── src/
│   │   ├── App.jsx           # Main app component
│   │   ├── App.css           # App styles
│   │   ├── main.jsx          # React entry point
│   │   ├── index.css         # Global styles
│   │   └── components/
│   │       ├── VoiceInterface.jsx    # Voice UI component
│   │       └── VoiceInterface.css    # Voice UI styles
│   ├── public/
│   │   └── orion-icon.svg    # App icon
│   ├── package.json          # Node dependencies
│   ├── .env                  # Environment variables (create from .env.example)
│   └── .env.example          # Environment template
│
├── logs/                     # Service logs
├── README.md                 # Project overview
├── SETUP.md                  # Detailed setup guide
├── start.sh                  # Start all services
└── stop.sh                   # Stop all services
```

## 🔧 Configuration

### Backend (.env)
```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
OPENAI_API_KEY=sk-your-key
ELEVENLABS_API_KEY=your_key
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
```

### Frontend (.env)
```env
VITE_LIVEKIT_URL=wss://your-project.livekit.cloud
VITE_TOKEN_SERVER_URL=http://localhost:3001
```

## 🎨 Customization

### Change AI Voice
1. Browse [ElevenLabs Voices](https://elevenlabs.io/voice-library)
2. Copy the voice ID
3. Update `ELEVENLABS_VOICE_ID` in `backend/.env`

### Modify Teaching Style
Edit the `SYSTEM_PROMPT` in `backend/config.py`

### Customize UI Colors
Edit CSS variables in `client/src/index.css`:
```css
:root {
  --color-text-accent: #667eea;
  --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  /* ... more variables ... */
}
```

### Change LLM Model
Edit `backend/agent.py`:
```python
llm_instance = openai.LLM(
    model="gpt-4o",  # Change to gpt-4, gpt-3.5-turbo, etc.
    temperature=0.7,
)
```

## 📊 Monitoring

### View Logs
```bash
# Token server logs
tail -f logs/token-server.log

# AI agent logs
tail -f logs/agent.log

# Frontend logs
tail -f logs/frontend.log
```

### LiveKit Dashboard
- URL: https://cloud.livekit.io/
- Monitor active rooms, participants, and audio tracks

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Port already in use | Run `./stop.sh` or kill processes on ports 3001, 5173 |
| Module not found | Run `pip install -r requirements.txt` or `npm install` |
| No audio | Check microphone permissions in browser |
| Agent not responding | Verify LiveKit credentials and agent is running |
| Token error | Ensure token server is running on port 3001 |

## 🔑 Keyboard Shortcuts (Coming Soon)

- `Space` - Mute/unmute microphone
- `Ctrl+R` - Repeat last response
- `Ctrl+S` - Save conversation
- `Esc` - Leave session

## 📈 Performance Tips

1. **Use Chrome/Edge** for best WebRTC performance
2. **Wired internet** recommended for low latency
3. **Close other tabs** to reduce CPU usage
4. **Use headphones** to prevent echo

## 🚀 Next Steps

1. ✅ Get Vaani running locally
2. 📝 Test with different topics
3. 🎨 Customize the UI to your liking
4. 🧠 Adjust the system prompt for your use case
5. 📊 Add conversation history
6. 🌐 Deploy to production

## 📚 Resources

- [LiveKit Docs](https://docs.livekit.io/)
- [OpenAI API](https://platform.openai.com/docs)
- [ElevenLabs Docs](https://elevenlabs.io/docs)
- [React Docs](https://react.dev/)

---

**Happy Learning! 🌟**
 
 
 
 
 
 
 
 
 
 
