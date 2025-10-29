import React, { useEffect, useState } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { User, CreditCard, Home, MessageCircle } from 'lucide-react';
import LineChart, { MiniSparkline } from '../components/Charts';
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

      <div className="dashboard-stats">
        <div className="stat-card">
          <h4>Net worth</h4>
          <div className="chart-placeholder">
            <LineChart data={[1200, 1400, 1500, 1300, 1550, 1700, 1600]} width={520} height={140} />
          </div>
        </div>

        <div className="stat-card small">
          <h4>Spending (30d)</h4>
          <div className="chart-placeholder small">
            <MiniSparkline data={[200, 150, 180, 220, 140, 190, 210, 240, 200, 170, 190]} />
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        <Link to="/accounts" className="dashboard-card card-link-wrapper">
          <div className="card-icon"><CreditCard size={36} /></div>
          <div className="card-content">
            <h3>Bank Accounts</h3>
            <p>Connect and manage your bank accounts</p>
            <span className="card-link">View Accounts →</span>
          </div>
        </Link>

        <Link to="/profile" className="dashboard-card card-link-wrapper">
          <div className="card-icon"><User size={36} /></div>
          <div className="card-content">
            <h3>Profile</h3>
            <p>View and manage your user profile</p>
            <span className="card-link">View Profile →</span>
          </div>
        </Link>

        <Link to="/households" className="dashboard-card card-link-wrapper">
          <div className="card-icon"><Home size={36} /></div>
          <div className="card-content">
            <h3>Households</h3>
            <p>Manage household-linked accounts and aggregated balances</p>
            <span className="card-link">View Households →</span>
          </div>
        </Link>

        <Link to="/agent" className="dashboard-card card-link-wrapper">
          <div className="card-icon"><MessageCircle size={36} /></div>
          <div className="card-content">
            <h3>AI Assistant</h3>
            <p>Chat with your financial advisor</p>
            <span className="card-link">Start Chat →</span>
          </div>
        </Link>
      </div>

      {/* Account information block removed (redundant) */}
    </div>
  );
};

export default Dashboard;