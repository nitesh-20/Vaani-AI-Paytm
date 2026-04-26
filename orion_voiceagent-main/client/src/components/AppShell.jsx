import React, { useState } from 'react';
import GeminiOrb from './GeminiOrb';
import Sidebar from './Sidebar';
import ThemeToggle from './ThemeToggle';
import './VoiceInterface.css';

export default function AppShell({
    isLoading = false,
    agentState = 'idle',
    chatMessages = [],
    selectedModel = "Vaani 1.0",
    micEnabled = false,
    onMicClick = () => { },
    onNewChat = () => { },
    sessionActive = true,   // New prop to control view mode. Default TRUE to prevent Orb pop on load.
    chatHistory = [],       // Chat history for sidebar
    onLoadChat = () => { }, // Handler to load a previous chat
}) {
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [isModelDropdownOpen, setIsModelDropdownOpen] = useState(false);

    return (
        <div className="voice-app-container">
            <Sidebar
                isOpen={isSidebarOpen}
                toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
                onNewChat={onNewChat}
                chatHistory={chatHistory}
                onLoadChat={onLoadChat}
            />

            <div className="voice-interface-wrapper">
                <header className="voice-header-main">
                    <div className="header-left">
                        <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">Vaani AI</span>
                        <div className="model-selector-container">
                            <div
                                className="model-selector"
                                onClick={() => setIsModelDropdownOpen(!isModelDropdownOpen)}
                            >
                                <span>{selectedModel}</span>
                                <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M7 10l5 5 5-5z" /></svg>
                            </div>

                            {isModelDropdownOpen && (
                                <div className="model-dropdown">
                                    <div className="dropdown-item active">
                                        <div className="model-info">
                                            <span className="model-name">Vaani 1.0</span>
                                            <span className="model-desc">Our most capable model</span>
                                        </div>
                                    </div>
                                    <div className="dropdown-item disabled">
                                        <div className="model-info">
                                            <span className="model-name">Vaani 1.0 Pro</span>
                                            <span className="model-desc">Coming soon</span>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                    <div className="header-right">
                        <ThemeToggle />
                        <div className="user-persona">S</div>
                    </div>
                </header>

                <main className="voice-main-content">
                    {/* 
             PERSISTENT ORB HERO
             The Orb is always present. It adapts its state but never leaves.
          */}
                    <div 
                        className={`central-orb-container ${sessionActive ? 'active-session' : 'transcript-mode'} ${micEnabled ? 'listening' : ''}`}
                        onClick={onMicClick}
                        style={{ cursor: 'pointer' }}
                        title={micEnabled ? "Listening... (Tap to mute)" : "Tap to wake Vaani"}
                    >
                        <GeminiOrb state={isLoading ? 'listening' : (agentState || 'idle')} />
                    </div>

                    {/* 
             WELCOME MESSAGE (Empty State)
             Visible regardless of mode, as long as there are no messages.
             This ensures "Hi Shreed" shows up with the Big Orb on load.
          */}
                    {chatMessages.length === 0 && !isLoading && (
                        <div className="empty-state-simple">
                            {/* Personalized Greeting */}
                            <h2>Hi Shreed, welcome back.</h2>
                        </div>
                    )}

                    {/* 
             Chat Overlay
             Only visible when session is NOT active (Transcript Mode)
          */}
                    {!sessionActive && (
                        <div className="chat-overlay-container visible">
                            <div className="chat-history-scroll">
                                {/* Messages */}
                                {chatMessages.map((msg) => (
                                    <div key={msg.id} className={`chat-message ${msg.isUser ? 'user' : 'agent'}`}>
                                        {!msg.isUser && <div className="msg-avatar">O</div>}
                                        <div className="msg-body">
                                            <div className="msg-sender">{msg.isUser ? 'You' : 'Orion'}</div>
                                            <div className="msg-text">{msg.text}</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </main>

                <footer className="voice-footer-main">
                    {/* Input area removed for a Siri-like experience */}
                </footer>
            </div>
        </div>
    );
}
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
