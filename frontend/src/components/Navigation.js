import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import './Navigation.css';

const Navigation = () => {
  const { logout, user, isAuthenticated } = useAuth0();
  const location = useLocation();

  if (!isAuthenticated) {
    return null;
  }

  const isActive = (path) => {
    return location.pathname === path ? 'nav-link active' : 'nav-link';
  };

  return (
    <nav className="navbar">
      <div className="nav-container">
        <div className="nav-brand">
          <Link to="/" className="brand-link">
            Finance Assistant
          </Link>
        </div>
        
        <div className="nav-menu">
          <Link to="/" className={isActive('/')}>
            <span className="nav-icon">🏠</span>
            Dashboard
          </Link>
          <Link to="/accounts" className={isActive('/accounts')}>
            <span className="nav-icon">🏦</span>
            Bank Accounts
          </Link>
          <Link to="/transactions" className={isActive('/transactions')}>
            <span className="nav-icon">💳</span>
            Transactions
          </Link>
          <Link to="/insights" className={isActive('/insights')}>
            <span className="nav-icon">📊</span>
            Insights
          </Link>
          <Link to="/chat" className={isActive('/chat')}>
            <span className="nav-icon">💬</span>
            AI Chat
          </Link>
        </div>

        <div className="nav-user">
          <div className="user-info">
            <img 
              src={user.picture || '/default-avatar.png'} 
              alt="User Avatar" 
              className="user-avatar"
            />
            <span className="user-name">{user.name || user.email}</span>
          </div>
          <button 
            onClick={() => logout({ returnTo: window.location.origin })}
            className="logout-btn"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;