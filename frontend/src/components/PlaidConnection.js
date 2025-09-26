import React, { useState, useEffect } from 'react';

const PlaidConnection = ({ token, plaidConnected }) => {
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch accounts
  const fetchAccounts = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/plaid/accounts', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch accounts');
      }

      const data = await response.json();
      console.log('Accounts:')
      console.log(data)
      setAccounts(data.accounts);
    } catch (error) {
      console.error('Error fetching accounts:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Fetch connections
  const fetchConnections = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/plaid/connections', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch connections');
      }

      const data = await response.json();
      console.log('Connections:')
      console.log(data)
      setConnections(data);
    } catch (error) {
      console.error('Error fetching connections:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Delete connection
  const deleteConnection = async (connectionId) => {
    if (!window.confirm('Are you sure you want to delete this connection?')) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/plaid/connections/${connectionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete connection');
      }

      // Refresh connections
      fetchConnections();
    } catch (error) {
      console.error('Error deleting connection:', error);
      setError(error.message);
    }
  };

  useEffect(() => {
    if (plaidConnected && token) {
      fetchConnections();
      fetchAccounts();
    }
  }, [plaidConnected, token]);

  if (!plaidConnected) {
    return (
      <div className="alert alert-info">
        Connect a bank account to view your financial data.
      </div>
    );
  }

  return (
    <div className="plaid-data-container">


      {error && (
        <div className="alert alert-danger">
          Error: {error}
        </div>
      )}

      {loading && (
        <div className="loading">
          Loading...
        </div>
      )}

        <div className="connections-tab">
          <h3>Bank Connections</h3>
          {connections.length === 0 ? (
            <p>No bank connections found.</p>
          ) : (
            <div className="connections-list">
              {connections.map((connection) => (
                <div key={connection.id} className="connection-card">
                  <div className="connection-info">
                    <h4>{connection.institution_name || 'Unknown Institution'}</h4>
                    <p>Item ID: {connection.item_id}</p>
                    <p>Connected: {new Date(connection.created_at).toLocaleDateString()}</p>
                  </div>
                  <button 
                    className="btn btn-danger btn-sm"
                    onClick={() => deleteConnection(connection.id)}
                  >
                    Delete
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="accounts-tab">
          <h3>Accounts</h3>
          {accounts.length === 0 ? (
            <p>No accounts found.</p>
          ) : (
            <div className="accounts-list">
              {accounts.map((account) => (
                <div key={account.account_id} className="account-card">
                  <h4>{account.name}</h4>
                  <p>Type: {account.type} {account.subtype && `(${account.subtype})`}</p>
                  <p>Balance: ${account.balance.toFixed(2)} {account.currency}</p>
                </div>
              ))}
            </div>
          )}
        </div>
    </div>
  );
};

export default PlaidConnection;