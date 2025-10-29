import React, { useState } from 'react';
import PlaidLink from './PlaidLink';
import PlaidData from './PlaidData';
import './PlaidIntegration.css';

const PlaidIntegration = ({ token, plaidConnected, setPlaidConnected, setConnectionsRefreshKey }) => {
  // `plaidConnected` and `setPlaidConnected` are lifted to the parent `Accounts` page.
  const [connectionData, setConnectionData] = useState(null);

  const handlePlaidSuccess = (data, metadata) => {
    console.log('Plaid connection successful:', data, metadata);
    setConnectionData(data);
    if (typeof setPlaidConnected === 'function') setPlaidConnected(true);
    // Trigger a refresh in the parent so AccountConnections reloads its list.
    if (typeof setConnectionsRefreshKey === 'function') {
      // slight delay to give backend a moment to sync
      setTimeout(() => setConnectionsRefreshKey((k) => (k || 0) + 1), 800);
    }

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
        {/* Simplified: remove the long "Why connect" section and show the connect action only */}
        {!plaidConnected && (
          <div className="plaid-connect-section">
            <div className="connect-action">
              <PlaidLink
                onSuccess={handlePlaidSuccess}
                onError={handlePlaidError}
                token={token}
              />
              <p className="security-note">
                🔒 Your data is encrypted and secure.
              </p>
            </div>
          </div>
        )}

  <PlaidData token={token} plaidConnected={plaidConnected} showTabs={false} />

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