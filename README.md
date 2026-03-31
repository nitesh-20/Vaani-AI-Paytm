# Vaani-AI-Paytm
# Vaani.AI — Voice AI for Merchant Intelligence

> From a Soundbox that speaks transactions → to an AI that understands business.

Vaani.AI is a real-time, voice-first AI assistant built to help merchants understand their finances — settlements, deductions, fees, and spending — using natural conversation.

It is built as an evolution of **Orion**, our base voice agent, extended with financial intelligence, transaction-aware reasoning, and merchant-specific workflows.

---

## 🧠 Project Structure

This repository contains two main systems:


### 1. Orion (Base Voice Agent)
A general-purpose, real-time voice AI agent.

- Real-time STT → LLM → TTS pipeline  
- Hinglish conversational support  
- Low-latency streaming via WebRTC  
- Modular architecture for extensibility  

### 2. Vaani.AI (Upgraded System)
Built on top of Orion, focused on **merchant intelligence**.

- Transaction-aware reasoning (RAG-based)  
- Settlement & fee breakdown explanations  
- Financial anomaly detection  
- Smart nudges (spending alerts, insights)  
- Context-aware responses using real transaction data  

---

## ⚡ Key Features

- 🎙️ Voice-first interaction (no dashboards required)  
- 💬 Natural language queries ("Why was ₹120 deducted?")  
- 📊 Settlement and fee breakdowns (MDR, instant settlement, etc.)  
- 🚨 Anomaly detection & spending insights  
- 🧠 Context-aware AI using transaction data  
- 🇮🇳 Hinglish-friendly conversational system  

---

## 🏗️ Tech Stack

### Frontend
- React 19 (Vite)
- TypeScript
- Tailwind CSS
- LiveKit Components (WebRTC)

### Backend
- Node.js (Express)
- Python (FastAPI / Flask)
- Firebase (Firestore)

### AI & Voice Stack
- Groq (LLaMA 3.3 70B) — core reasoning  
- Google Gemini 2.5 Flash — real-time audio  
- Deepgram (Nova-2) — Speech-to-Text  
- ElevenLabs — Text-to-Speech  
- Silero VAD — Voice Activity Detection  
- LiveKit Agents SDK — audio orchestration  

### Data Layer
- Custom RAG pipeline for transaction parsing  
- Structured merchant dataset (settlements, fees, deductions)  

---

## 🔁 System Architecture
User Voice Input
↓
Deepgram (STT)
↓
LLM (Groq / Gemini)
↓
RAG Context Injection (Transaction Engine)
↓
Response Generation
↓
ElevenLabs (TTS)
↓
Audio Output via LiveKit
---

## 📂 How It Works

1. User speaks a query (voice/text)
2. Speech is transcribed in real-time
3. Relevant transaction data is retrieved (RAG)
4. LLM processes query with context
5. Response is generated and converted to speech
6. Output is delivered instantly

---

## 🧪 Example Queries

- "Why was ₹120 deducted yesterday?"
- "Show my settlement breakdown"
- "Am I spending more than usual?"
- "What are my total fees this week?"

---

## 🛠️ Setup & Run

### Prerequisites
- Node.js (v18+)
- Python 3.x
- API keys: Groq, Gemini, Deepgram, ElevenLabs, LiveKit

### Installation

# Install frontend
cd frontend
npm install

# Install backend
cd ../backend
pip install -r requirements.txt
Create .env file: GROQ_API_KEY=
GEMINI_API_KEY=
DEEPGRAM_API_KEY=
ELEVENLABS_API_KEY=
LIVEKIT_API_KEY=
FIREBASE_CONFIG=

📌 Design Principles
Low latency first (real-time voice experience)
Explainability over black-box responses
Merchant-first UX (no dashboards required)
Modular AI pipeline (swap models easily)

🤝 Contribution
This is a hackathon prototype built under time constraints.
Contributions, feedback, and improvements are welcome.
