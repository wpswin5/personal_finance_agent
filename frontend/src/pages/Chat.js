import React from 'react';
import './Chat.css';

const Chat = () => {
  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>AI Financial Assistant</h1>
        <p>Get personalized financial advice and insights</p>
      </div>
      
      <div className="chat-content">
        <div className="coming-soon">
          <div className="coming-soon-icon">💬</div>
          <h2>AI Chat Coming Soon</h2>
          <p>
            We're developing an intelligent financial assistant that will help you understand your 
            spending, create budgets, and make informed financial decisions through natural conversation.
          </p>
          <div className="features-preview">
            <div className="feature-item">
              <span className="feature-icon">🤖</span>
              <span>Natural Language Processing</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">💰</span>
              <span>Personalized Financial Advice</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">📋</span>
              <span>Budget Planning Assistance</span>
            </div>
            <div className="feature-item">
              <span className="feature-icon">🔍</span>
              <span>Transaction Analysis</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;