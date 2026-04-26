import React from 'react';
import './Sidebar.css';

const Sidebar = ({ isOpen, toggleSidebar, onNewChat, chatHistory = [], onLoadChat }) => {
    return (
        <div className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
            <div className="sidebar-header">
                <button className="icon-button menu-btn" onClick={toggleSidebar}>
                    <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z" /></svg>
                </button>
            </div>

            <div className="new-chat-container">
                <button className="new-chat-button" onClick={onNewChat}>
                    <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" /></svg>
                    {isOpen && <span>New chat</span>}
                </button>
            </div>

            <div className="sidebar-nav">
                <div className="nav-item">
                    <div className="nav-icon">
                        <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z" /></svg>
                    </div>
                    {isOpen && <span className="nav-label">My Stuff</span>}
                </div>
                <div className="nav-item">
                    <div className="nav-icon">
                        <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor"><path d="M12 1L9 9l-8 3 8 3 3 8 3-8 8-3-8-3-3-8z" /></svg>
                    </div>
                    {isOpen && <span className="nav-label">Gems</span>}
                </div>

                {isOpen && (
                    <div className="recent-section">
                        <h3 className="section-title">Chats</h3>
                        {chatHistory.length === 0 ? (
                            <div className="recent-item empty">
                                <span style={{ opacity: 0.5, fontSize: '13px' }}>No previous chats</span>
                            </div>
                        ) : (
                            chatHistory.map((chat) => (
                                <div
                                    key={chat.id}
                                    className="recent-item clickable"
                                    onClick={() => onLoadChat(chat)}
                                >
                                    <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z" /></svg>
                                    <span>{chat.title}</span>
                                </div>
                            ))
                        )}
                    </div>
                )}
            </div>

            <div className="sidebar-footer">
                <div className="nav-item">
                    <div className="nav-icon">
                        <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M19.43 12.98c.04-.32.07-.64.07-.98s-.03-.66-.07-.98l2.11-1.65c.19-.15.24-.42.12-.64l-2-3.46c-.12-.22-.39-.3-.61-.22l-2.49 1c-.52-.4-1.08-.73-1.69-.98l-.38-2.65C14.46 2.18 14.25 2 14 2h-4c-.25 0-.46.18-.49.42l-.38 2.65c-.61.25-1.17.59-1.69.98l-2.49-1c-.23-.09-.49 0-.61.22l-2 3.46c-.13.22-.07.49.12.64l2.11 1.65c-.04.32-.07.65-.07.98s.03.66.07.98l-2.11 1.65c-.19.15-.24.42-.12.64l2 3.46c.12.22.39.3.61.22l2.49-1c.52.4 1.08.73 1.69.98l.38 2.65c.03.24.24.42.49.42h4c.25 0 .46-.18.49-.42l.38-2.65c.61-.25 1.17-.59 1.69-.98l2.49 1c.23.09.49 0 .61-.22l2-3.46c.12-.22.07-.49-.12-.64l-2.11-1.65zM12 15.5c-1.93 0-3.5-1.57-3.5-3.5s1.57-3.5 3.5-3.5 3.5 1.57 3.5 3.5-1.57 3.5-3.5 3.5z" /></svg>
                    </div>
                    {isOpen && <span className="nav-label">Settings & help</span>}
                </div>
            </div>
        </div>
    );
};

export default Sidebar;
 
 
 
 
