import React, { useState } from 'react';
import PlaidLink from './PlaidLink';
import PlaidData from './PlaidData';
import './PlaidIntegration.css';

const PlaidIntegration = ({ token }) => {
  const [plaidConnected, setPlaidConnected] = useState(false);
  const [connectionData, setConnectionData] = useState(null);

  const handlePlaidSuccess = (data, metadata) => {
    console.log('Plaid connection successful:', data, metadata);
    setConnectionData(data);
    setPlaidConnected(true);
    
    // Show success message
    alert(`Successfully connected to ${data.institution_name || 'your bank'}!`);
  };

  const handlePlaidError = (error) => {
    console.error('Plaid connection error:', error);
    alert('Failed to connect to your bank. Please try again.');
  };

  return (
    <div className="plaid-integration">
      <div className="plaid-header">
        <h2>Bank Account Integration</h2>
        <p>Connect your bank accounts to automatically import transactions and get personalized financial insights.</p>
      </div>

      <div className="plaid-content">
        {!plaidConnected && (
          <div className="plaid-connect-section">
            <div className="connect-info">
              <h3>Why Connect Your Bank?</h3>
              <ul>
                <li>Automatically import transactions</li>
                <li>Get real-time account balances</li>
                <li>Receive personalized financial insights</li>
                <li>Track spending patterns and budgets</li>
                <li>Detect unusual transactions</li>
              </ul>
            </div>
            
            <div className="connect-action">
              <PlaidLink 
                onSuccess={handlePlaidSuccess}
                onError={handlePlaidError}
                token={token}
              />
              <p className="security-note">
                🔒 Your data is encrypted and secure. We use bank-level security to protect your information.
              </p>
            </div>
          </div>
        )}

        <PlaidData 
          token={token} 
          plaidConnected={plaidConnected}
        />

        {plaidConnected && (
          <div className="add-more-accounts">
            <h3>Add Another Bank Account</h3>
            <PlaidLink 
              onSuccess={handlePlaidSuccess}
              onError={handlePlaidError}
              token={token}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default PlaidIntegration;