import { useEffect, useState, useRef, useCallback } from 'react';
import {
  useConnectionState,
  RoomAudioRenderer,
  useLocalParticipant,
  useRoomContext,
  useVoiceAssistant,
} from '@livekit/components-react';
import { ConnectionState } from 'livekit-client';
import AppShell from './AppShell';

export default function VoiceInterface({ onNewChat }) {
  const connectionState = useConnectionState();
  const { localParticipant } = useLocalParticipant();
  const room = useRoomContext();

  // useVoiceAssistant: state ("connecting"|"initializing"|"listening"|"thinking"|"speaking"|"disconnected")
  // agentTranscriptions: array of { text, isFinal, participantIdentity }
  const { state: agentState, agentTranscriptions } = useVoiceAssistant();

  const [micEnabled, setMicEnabled] = useState(false);
  const [sessionActive, setSessionActive] = useState(true);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatHistory, setChatHistory] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);

  const hasShownGreeting = useRef(false);
  const seenSegments = useRef(new Set());

  const isConnected = connectionState === ConnectionState.Connected;

  // Load chat history on mount
  useEffect(() => {
    const saved = localStorage.getItem('vaani-chat-history');
    if (saved) setChatHistory(JSON.parse(saved));
  }, []);

  // Show instant UI greeting when connected
  useEffect(() => {
    if (isConnected && !hasShownGreeting.current) {
      hasShownGreeting.current = true;
      const newChatId = Date.now();
      setCurrentChatId(newChatId);
      setChatMessages([{
        id: 'greeting-' + newChatId,
        text: "Connected! Vaani is preparing your financial snapshot...",
        isUser: false,
        timestamp: Date.now(),
      }]);
    }
  }, [isConnected]);

  // Consume agentTranscriptions from useVoiceAssistant (agent side)
  useEffect(() => {
    if (!agentTranscriptions || agentTranscriptions.length === 0) return;

    agentTranscriptions.forEach((seg) => {
      if (!seg.final || !seg.text?.trim()) return;
      if (seenSegments.current.has(seg.id)) return;
      seenSegments.current.add(seg.id);

      setChatMessages(prev => [...prev, {
        id: seg.id || Date.now(),
        text: seg.text.trim(),
        isUser: false,
        timestamp: Date.now(),
      }]);
    });
  }, [agentTranscriptions]);

  // Capture user transcriptions via microphone track transcription events
  useEffect(() => {
    if (!room || !localParticipant) return;

    const handleTranscription = (segments, participant) => {
      if (participant?.identity !== localParticipant.identity) return;
      segments.forEach((seg) => {
        if (!seg.final || !seg.text?.trim()) return;
        if (seenSegments.current.has(seg.id)) return;
        seenSegments.current.add(seg.id);

        setChatMessages(prev => [...prev, {
          id: seg.id || Date.now(),
          text: seg.text.trim(),
          isUser: true,
          timestamp: Date.now(),
        }]);
      });
    };

    room.on('transcriptionReceived', handleTranscription);
    return () => room.off('transcriptionReceived', handleTranscription);
  }, [room, localParticipant]);

  // Auto-scroll transcript
  useEffect(() => {
    if (!sessionActive) {
      const el = document.querySelector('.chat-history-scroll');
      if (el) el.scrollTop = el.scrollHeight;
    }
  }, [chatMessages, sessionActive]);

  // Save chat to localStorage
  const saveChatToHistory = useCallback(() => {
    if (chatMessages.length > 1 && currentChatId) {
      const userMessages = chatMessages.filter(m => m.isUser);
      const title = userMessages.length > 0
        ? userMessages[0].text.slice(0, 40) + (userMessages[0].text.length > 40 ? '...' : '')
        : 'New conversation';

      const newChat = { id: currentChatId, title, messages: chatMessages, timestamp: Date.now() };
      setChatHistory(prev => {
        const filtered = prev.filter(c => c.id !== currentChatId);
        const updated = [newChat, ...filtered].slice(0, 20);
        localStorage.setItem('orion-chat-history', JSON.stringify(updated));
        return updated;
      });
    }
  }, [chatMessages, currentChatId]);

  useEffect(() => {
    const handleBeforeUnload = () => {
      if (chatMessages.length > 1 && currentChatId) {
        const userMessages = chatMessages.filter(m => m.isUser);
        const title = userMessages.length > 0 ? userMessages[0].text.slice(0, 40) : 'New conversation';
        const newChat = { id: currentChatId, title, messages: chatMessages, timestamp: Date.now() };
        const saved = localStorage.getItem('orion-chat-history');
        const history = saved ? JSON.parse(saved) : [];
        const updated = [newChat, ...history.filter(c => c.id !== currentChatId)].slice(0, 20);
        localStorage.setItem('orion-chat-history', JSON.stringify(updated));
      }
    };
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [chatMessages, currentChatId]);

  const handleNewChat = useCallback(() => {
    saveChatToHistory();
    setChatMessages([]);
    hasShownGreeting.current = false;
    seenSegments.current = new Set();
    setSessionActive(true);
    setCurrentChatId(null);
    if (onNewChat) onNewChat();
  }, [onNewChat, saveChatToHistory]);

  const handleLoadChat = useCallback((chat) => {
    saveChatToHistory();
    setChatMessages(chat.messages);
    setCurrentChatId(chat.id);
    setSessionActive(false);
    hasShownGreeting.current = true;
  }, [saveChatToHistory]);

  const handleMicClick = async () => {
    const next = !micEnabled;
    await localParticipant?.setMicrophoneEnabled(next);
    setMicEnabled(next);
    if (next) setSessionActive(true);
  };

  const handleEndSession = () => {
    setSessionActive(false);
    setMicEnabled(false);
    localParticipant?.setMicrophoneEnabled(false);
    if (room) room.disconnect();
    saveChatToHistory();
  };

  const getStatusText = () => {
    if (!isConnected) return "Establishing connection...";
    if (sessionActive) {
      if (agentState === "speaking") return "Vaani is speaking";
      if (agentState === "thinking") return "Vaani is thinking...";
      if (agentState === "listening") return micEnabled ? "Listening..." : "Tap mic to speak";
      if (agentState === "initializing") return "Vaani is starting up...";
      return micEnabled ? "Listening..." : "Tap mic to speak";
    }
    return "Transcript View";
  };

  return (
    <>
      <RoomAudioRenderer />
      <AppShell
        isLoading={!isConnected}
        agentState={agentState}
        chatMessages={chatMessages}
        micEnabled={micEnabled}
        sessionActive={sessionActive}
        onMicClick={handleMicClick}
        onEndSession={handleEndSession}
        onNewChat={handleNewChat}
        statusText={getStatusText()}
        chatHistory={chatHistory}
        onLoadChat={handleLoadChat}
      />
    </>
  );
}
 
 
 
 
 
 
 
 
 
 
 
