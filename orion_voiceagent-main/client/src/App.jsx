import React, { useEffect, useState, useCallback } from 'react';
import { LiveKitRoom } from '@livekit/components-react';
import '@livekit/components-styles';
import VoiceInterface from './components/VoiceInterface';
import AppShell from './components/AppShell'; // Import the shell for loading state
import './App.css';

// Token server URL - defaults to 127.0.0.1 for development (safer than localhost for some environments)
const TOKEN_SERVER_URL = import.meta.env.VITE_TOKEN_SERVER_URL || 'http://127.0.0.1:8000';

function App() {
  const [token, setToken] = useState("");
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [roomKey, setRoomKey] = useState(Date.now()); // Used to force room reconnection

  const fetchToken = useCallback(async () => {
    try {
      setToken("");
      setError("");
      setIsLoading(true);

      const roomName = `orion-${Date.now()}`;
      const identity = `user-${Math.floor(Math.random() * 1000)}`;

      console.log(`Fetching token from ${TOKEN_SERVER_URL}/token...`);

      const auth_token = import.meta.env.VITE_ORION_AUTH_TOKEN || 'change-me-123';
      const response = await fetch(
        `${TOKEN_SERVER_URL}/token?room=${roomName}&identity=${identity}`,
        {
          headers: {
            'X-Authorization': auth_token
          }
        }
      );

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      console.log('Token received successfully');
      setToken(data.token);
      setUrl(data.url);
    } catch (e) {
      console.error("Failed to fetch token:", e);
      setError(e.message || "Failed to connect to server");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchToken();
  }, [fetchToken, roomKey]);

  // Handler for creating a new chat - disconnects and reconnects to a new room
  const handleNewChat = useCallback(() => {
    setRoomKey(Date.now());
  }, []);

  if (error) {
    return (
      <div className="error-screen">
        <h2>Connection Error</h2>
        <p>{error}</p>
        <p style={{ fontSize: '12px', color: '#999', marginTop: '8px' }}>
          Make sure the token server is running at {TOKEN_SERVER_URL}
        </p>
        <button onClick={() => setRoomKey(Date.now())}>Retry</button>
      </div>
    );
  }

  // Show AppShell during loading - maintains visual consistency
  if (isLoading || !token) {
    return (
      <AppShell
        isLoading={true}
        onNewChat={() => { }}
        micEnabled={false}
        sessionActive={true}
      />
    );
  }

  return (
    <LiveKitRoom
      key={roomKey}
      video={false}
      audio={true}
      token={token}
      serverUrl={url}
      connect={true}
      onConnected={() => console.log("Connected!")}
      onDisconnected={() => console.log("Disconnected")}
      onError={(e) => setError("Connection failed")}
    >
      <VoiceInterface onNewChat={handleNewChat} />
    </LiveKitRoom>
  );
}

export default App;
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
