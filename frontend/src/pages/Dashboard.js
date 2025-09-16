import React, { useEffect, useState } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import axios from 'axios';
import './Dashboard.css';

const Dashboard = () => {
  const { getAccessTokenSilently, user, isAuthenticated } = useAuth0();
  const [me, setMe] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMe = async () => {
      if (isAuthenticated) {
        try {
          const token = await getAccessTokenSilently({
            audience: "https://fastapiexample.com",
            scope: "test:read"
          });
          const response = await axios.get("http://localhost:8000/user/me", {
            headers: { Authorization: `Bearer ${token}` },
          });
          setMe(response.data);
        } catch (err) {
          console.error(err);
        } finally {
          setLoading(false);
        }
      }
    };
    fetchMe();
  }, [isAuthenticated, getAccessTokenSilently]);

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading-spinner">Loading...</div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Welcome back, {user?.name || user?.email}!</h1>
        <p>Here's your financial overview</p>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <div className="card-icon">🏦</div>
          <div className="card-content">
            <h3>Bank Accounts</h3>
            <p>Connect and manage your bank accounts</p>
            <a href="/accounts" className="card-link">View Accounts →</a>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-icon">💳</div>
          <div className="card-content">
            <h3>Transactions</h3>
            <p>View and analyze your spending</p>
            <a href="/transactions" className="card-link">View Transactions →</a>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-icon">📊</div>
          <div className="card-content">
            <h3>Financial Insights</h3>
            <p>Get AI-powered financial analysis</p>
            <a href="/insights" className="card-link">View Insights →</a>
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-icon">💬</div>
          <div className="card-content">
            <h3>AI Assistant</h3>
            <p>Chat with your financial advisor</p>
            <a href="/chat" className="card-link">Start Chat →</a>
          </div>
        </div>
      </div>

      {me && (
        <div className="user-info-section">
          <h2>Account Information</h2>
          <div className="user-details">
            <pre>{JSON.stringify(me, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;