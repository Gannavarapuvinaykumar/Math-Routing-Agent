import { useState, useEffect } from 'react';
import '../styles/Menu.css';

function HamburgerMenu({ onNewChat, submittedQuery }) {
  const [isOpen, setIsOpen] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredHistory, setFilteredHistory] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);

  // Load chat history from localStorage
  useEffect(() => {
    const savedHistory = localStorage.getItem('mathChatHistory');
    const savedSessionId = localStorage.getItem('currentChatSessionId');
    if (savedHistory) {
      setChatHistory(JSON.parse(savedHistory));
      setFilteredHistory(JSON.parse(savedHistory));
    }
    if (savedSessionId) {
      setCurrentSessionId(savedSessionId);
    }
  }, []);

  // Save submitted query to history (only when search is actually performed)
  useEffect(() => {
    if (submittedQuery && submittedQuery.trim()) {
      const timestamp = new Date().toISOString();
      
      // Read current history from localStorage to avoid infinite loop
      const savedHistory = localStorage.getItem('mathChatHistory');
      const currentHistory = savedHistory ? JSON.parse(savedHistory) : [];
      
      // Get the saved session ID from localStorage
      const savedSessionId = localStorage.getItem('currentChatSessionId');
      const lastChat = currentHistory[0];
      
      // Check if this exact query was just added (prevent duplicates)
      if (lastChat?.queries?.includes(submittedQuery)) {
        return; // Already added, skip
      }
      
      // Check if we should add to existing session or create new one
      // Use the last chat's lastUpdated instead of timestamp
      const timeSinceLastChat = lastChat?.lastUpdated 
        ? Date.now() - new Date(lastChat.lastUpdated).getTime() 
        : Infinity;
      
      const shouldCreateNewSession = !savedSessionId || !lastChat || timeSinceLastChat > 300000; // 5 minutes
      
      if (shouldCreateNewSession) {
        // Create new chat session
        const sessionId = timestamp;
        const newChat = {
          id: sessionId,
          sessionId: sessionId,
          queries: [submittedQuery],
          firstQuery: submittedQuery,
          timestamp: timestamp,
          lastUpdated: timestamp,
          date: new Date(timestamp).toLocaleDateString(),
          time: new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        
        const updatedHistory = [newChat, ...currentHistory].slice(0, 50);
        setChatHistory(updatedHistory);
        setFilteredHistory(updatedHistory);
        setCurrentSessionId(sessionId);
        localStorage.setItem('mathChatHistory', JSON.stringify(updatedHistory));
        localStorage.setItem('currentChatSessionId', sessionId);
      } else {
        // Add to existing session - use savedSessionId
        const updatedHistory = currentHistory.map(chat => {
          if (chat.sessionId === savedSessionId) {
            return {
              ...chat,
              queries: [...chat.queries, submittedQuery],
              lastUpdated: timestamp,
              time: new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            };
          }
          return chat;
        });
        
        setChatHistory(updatedHistory);
        setFilteredHistory(updatedHistory);
        localStorage.setItem('mathChatHistory', JSON.stringify(updatedHistory));
      }
    }
  }, [submittedQuery]); // Only depend on submittedQuery, not chatHistory!

  // Filter history based on search
  useEffect(() => {
    if (searchTerm.trim()) {
      const filtered = chatHistory.filter(chat => {
        // Search in first query and all queries
        const searchInQueries = chat.queries?.some(q => 
          q.toLowerCase().includes(searchTerm.toLowerCase())
        );
        const searchInFirst = chat.firstQuery?.toLowerCase().includes(searchTerm.toLowerCase());
        return searchInQueries || searchInFirst;
      });
      setFilteredHistory(filtered);
    } else {
      setFilteredHistory(chatHistory);
    }
  }, [searchTerm, chatHistory]);

  const handleNewChat = () => {
    // Create a new session
    setCurrentSessionId(null);
    localStorage.removeItem('currentChatSessionId');
    onNewChat();
    setIsOpen(false);
  };

  const handleChatClick = (chat) => {
    // When clicking a chat, load the first query from that session
    onNewChat(chat.firstQuery);
    setIsOpen(false);
  };

  const handleClearHistory = () => {
    if (window.confirm('Are you sure you want to clear all chat history?')) {
      setChatHistory([]);
      setFilteredHistory([]);
      localStorage.removeItem('mathChatHistory');
    }
  };

  const handleDeleteChat = (e, chatId) => {
    e.stopPropagation();
    const updatedHistory = chatHistory.filter(chat => chat.id !== chatId);
    setChatHistory(updatedHistory);
    setFilteredHistory(updatedHistory);
    localStorage.setItem('mathChatHistory', JSON.stringify(updatedHistory));
  };

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  // Group chats by date
  const groupChatsByDate = () => {
    const today = new Date().toLocaleDateString();
    const yesterday = new Date(Date.now() - 86400000).toLocaleDateString();
    
    const groups = {
      Today: [],
      Yesterday: [],
      'Previous 7 Days': [],
      'Previous 30 Days': [],
      Older: []
    };

    filteredHistory.forEach(chat => {
      const chatDate = chat.date;
      const daysAgo = Math.floor((Date.now() - new Date(chat.timestamp)) / 86400000);

      if (chatDate === today) {
        groups.Today.push(chat);
      } else if (chatDate === yesterday) {
        groups.Yesterday.push(chat);
      } else if (daysAgo <= 7) {
        groups['Previous 7 Days'].push(chat);
      } else if (daysAgo <= 30) {
        groups['Previous 30 Days'].push(chat);
      } else {
        groups.Older.push(chat);
      }
    });

    return groups;
  };

  const chatGroups = groupChatsByDate();

  return (
    <>
      {/* Hamburger Button */}
      <button 
        className={`hamburger-button ${isOpen ? 'active' : ''}`}
        onClick={toggleMenu}
        aria-label="Toggle menu"
      >
        <span></span>
        <span></span>
        <span></span>
      </button>

      {/* Overlay */}
      {isOpen && <div className="menu-overlay" onClick={toggleMenu}></div>}

      {/* Sidebar Menu */}
      <div className={`sidebar-menu ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h2>Math Routing Agent</h2>
        </div>

        {/* New Chat Button */}
        <button className="new-chat-button" onClick={handleNewChat}>
          <span className="icon">+</span>
          <span>New Chat</span>
        </button>

        {/* Search Chat */}
        <div className="search-chat-container">
          <input
            type="text"
            placeholder="Search chats..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-chat-input"
          />
          <span className="search-icon">🔍</span>
        </div>

        {/* Chat History */}
        <div className="chat-history">
          <div className="history-header">
            <h3>Chat History</h3>
            {chatHistory.length > 0 && (
              <button 
                className="clear-history-button"
                onClick={handleClearHistory}
                title="Clear all history"
              >
                🗑️
              </button>
            )}
          </div>

          <div className="history-list">
            {filteredHistory.length === 0 ? (
              <div className="empty-history">
                <p>No chat history yet</p>
                <small>Your conversations will appear here</small>
              </div>
            ) : (
              Object.entries(chatGroups).map(([groupName, chats]) => (
                chats.length > 0 && (
                  <div key={groupName} className="history-group">
                    <div className="group-name">{groupName}</div>
                    {chats.map((chat) => {
                      const displayText = chat.firstQuery || chat.query || chat.queries?.[0] || 'Untitled chat';
                      
                      return (
                        <div 
                          key={chat.id} 
                          className="history-item"
                          onClick={() => handleChatClick(chat)}
                        >
                          <div className="chat-preview">
                            <div className="chat-text">
                              {displayText}
                            </div>
                            <div className="chat-time">{chat.time}</div>
                          </div>
                          <button
                            className="delete-chat-button"
                            onClick={(e) => handleDeleteChat(e, chat.id)}
                            title="Delete chat"
                          >
                            ×
                          </button>
                        </div>
                      );
                    })}
                  </div>
                )
              ))
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="sidebar-footer">
          <div className="footer-info">
            <small>© 2025 Math Routing Agent</small>
          </div>
        </div>
      </div>
    </>
  );
}

export default HamburgerMenu;
