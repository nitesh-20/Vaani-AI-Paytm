# 🚀 How to Deploy Vaani Voice Agent

This guide will help you deploy your Vaani Voice Agent project so others can try it out.

The project consists of two parts that need to be deployed:
1.  **Backend** (Python): Handles the AI voice agent logic + Token generation.
2.  **Frontend** (React): The user interface.

---

## Prerequisites

You will need accounts on these services (most have free tiers):
1.  **GitHub**: To host your code.
2.  **LiveKit Cloud**: For real-time audio/video (you likely already have this).
3.  **Deepgram & OpenAI/Groq**: API keys for the AI models.
4.  **Render** (or Railway/Fly.io): To host the Backend.
5.  **Vercel** (or Netlify): To host the Frontend.

---

## Part 1: Prepare Your Code

1.  **Push to GitHub**: Ensure your project is pushed to a GitHub repository.
    ```bash
    git add .
    git commit -m "Ready for deployment"
    git push origin main
    ```

---

## Part 2: Deploy Backend (Render)

We will use **Render** because it's easy to set up Docker containers.

1.  Go to [dashboard.render.com](https://dashboard.render.com/) and click **New +** -> **Web Service**.
2.  Connect your GitHub repository.
3.  **Settings**:
    *   **Name**: `orion-backend` (or similar)
    *   **Root Directory**: `backend` (Important: set this to `backend`)
    *   **Runtime**: Docker
    *   **Region**: Choose one close to you (e.g., Oregon, Frankfurt).
    *   **Instance Type**: Free (Note: Free instances spin down after inactivity. For a voice agent that needs to be "always on" to answer quickly, consider the "Starter" plan for ~$7/mo, otherwise the first connection might fail or take 60s+ to wake up).
4.  **Environment Variables**:
    Add the following variables (copy values from your local `.env`):
    *   `LIVEKIT_URL`: (from LiveKit Cloud)
    *   `LIVEKIT_API_KEY`: (from LiveKit Cloud)
    *   `LIVEKIT_API_SECRET`: (from LiveKit Cloud)
    *   `DEEPGRAM_API_KEY`: (Your Deepgram key)
    *   `OPENAI_API_KEY`: (Your OpenAI key, if using)
    *   `ELEVENLABS_VOICE_ID`: (Your Voice ID)
    *   `CORS_ALLOWED_ORIGINS`: `*` (Start with * to allow all, or restrict to your Vercel URL later)
5.  Click **Create Web Service**.

**Wait for deployment**: Render will build the Docker image and start the service.
Once finished, copy the **Service URL** (e.g., `https://orion-backend.onrender.com`). You will need this for the frontend.

---

## Part 3: Deploy Frontend (Vercel)

1.  Go to [vercel.com](https://vercel.com) and **Add New** -> **Project**.
2.  Import your GitHub repository.
3.  **Project Settings**:
    *   **Framework Preset**: Vite
    *   **Root Directory**: `client` (Edit this to point to `client`)
4.  **Environment Variables**:
    *   `VITE_TOKEN_SERVER_URL`: Paste your Render Backend URL here (e.g., `https://orion-backend.onrender.com`).
        *   *Note: Do NOT add a trailing slash `/`.*
5.  Click **Deploy**.

---

## Part 4: Verification

1.  Open your new Vercel URL (e.g., `https://orion-voiceagent.vercel.app`).
2.  The app should load.
3.  Click the microphone/start button.
4.  **Backend Check**: The frontend will request a token from your Render backend.
    *   If Render is "sleeping" (Free tier), this request might take 50-60 seconds. Be patient on the first try.
5.  **Agent Check**: Once connected to the room, the Agent (running on Render) should join.
    *   If the agent doesn't join, check the Render logs.

---

## Troubleshooting

*   **"Connection failed"**: Check the `VITE_TOKEN_SERVER_URL` in Vercel. It must match your deployed backend URL.
*   **Agent never joins**: Check Render logs. Ensure `start_prod.sh` is running both the server and the agent.
*   **Audio lag**: Server location matters. Try to put Render and LiveKit Cloud regions close to each other.
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
