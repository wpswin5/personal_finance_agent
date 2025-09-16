import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { useAuth0 } from "@auth0/auth0-react";
import Navigation from "./components/Navigation";
import Dashboard from "./pages/Dashboard";
import Accounts from "./pages/Accounts";
import Transactions from "./pages/Transactions";
import Insights from "./pages/Insights";
import Chat from "./pages/Chat";
import "./App.css";

function App() {
  const { loginWithPopup, isAuthenticated, isLoading } = useAuth0();

  if (isLoading) {
    return (
      <div className="app-container">
        <div className="loading-container">
          <div className="loading-spinner">Loading...</div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="app-container">
        <div className="login-container">
          <div className="login-card">
            <h1 className="app-title">💰 Personal Finance Agent</h1>
            <p className="app-subtitle">
              Take control of your finances with AI-powered insights and secure bank integration
            </p>
            <button 
              onClick={loginWithPopup}
              className="login-button"
            >
              Log In / Sign Up
            </button>
            <div className="features-list">
              <div className="feature">🏦 Secure Bank Integration</div>
              <div className="feature">📊 AI-Powered Insights</div>
              <div className="feature">💳 Transaction Analysis</div>
              <div className="feature">💬 Financial Assistant</div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="app-container">
        <Navigation />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/accounts" element={<Accounts />} />
            <Route path="/transactions" element={<Transactions />} />
            <Route path="/insights" element={<Insights />} />
            <Route path="/chat" element={<Chat />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
