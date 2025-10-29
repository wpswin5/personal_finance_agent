import React, { useState, useEffect } from 'react';

const PlaidData = ({ token, plaidConnected, showTabs = true }) => {
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  // start on connections tab to avoid immediately attempting to fetch accounts
  // which may be unavailable for some users or endpoints.
  const [activeTab, setActiveTab] = useState('connections');

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
        // treat 404/204 as empty result rather than a hard failure
        if (response.status === 404 || response.status === 204) {
          setAccounts([]);
          return;
        }
        throw new Error('Failed to fetch accounts');
      }

      const data = await response.json();
      setAccounts(data.accounts || []);
    } catch (error) {
      console.error('Error fetching accounts:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Fetch transactions
  const fetchTransactions = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/plaid/transactions?count=50', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 404 || response.status === 204) {
          setTransactions([]);
          return;
        }
        throw new Error('Failed to fetch transactions');
      }

      const data = await response.json();
      setTransactions(data.transactions || []);
    } catch (error) {
      console.error('Error fetching transactions:', error);
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
        if (response.status === 404 || response.status === 204) {
          setConnections([]);
          return;
        }
        throw new Error('Failed to fetch connections');
      }

      const data = await response.json();
      setConnections(data || []);
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
    }
  }, [plaidConnected, token]);

  useEffect(() => {
    if (plaidConnected && token && activeTab === 'accounts') {
      fetchAccounts();
    } else if (plaidConnected && token && activeTab === 'transactions') {
      fetchTransactions();
    }
  }, [plaidConnected, token, activeTab]);

  // If embedded in the Accounts page we don't want the tabs to show at all.
  if (!showTabs) return null;

  if (!plaidConnected) {
    return (
      <div className="alert alert-info">
        Connect your bank account to view your financial data.
      </div>
    );
  }

  return (
    <div className="plaid-data-container">
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'connections' ? 'active' : ''}`}
          onClick={() => setActiveTab('connections')}
        >
          Connections
        </button>
        <button 
          className={`tab ${activeTab === 'accounts' ? 'active' : ''}`}
          onClick={() => setActiveTab('accounts')}
        >
          Accounts
        </button>
        <button 
          className={`tab ${activeTab === 'transactions' ? 'active' : ''}`}
          onClick={() => setActiveTab('transactions')}
        >
          Transactions
        </button>
      </div>

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

      {activeTab === 'connections' && (
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
      )}

      {activeTab === 'accounts' && (
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
      )}

      {activeTab === 'transactions' && (
        <div className="transactions-tab">
          <h3>Recent Transactions</h3>
          {transactions.length === 0 ? (
            <p>No transactions found.</p>
          ) : (
            <div className="transactions-list">
              {transactions.map((transaction) => (
                <div key={transaction.transaction_id} className="transaction-card">
                  <div className="transaction-info">
                    <h4>{transaction.name}</h4>
                    {transaction.merchant_name && (
                      <p>Merchant: {transaction.merchant_name}</p>
                    )}
                    <p>Date: {new Date(transaction.date).toLocaleDateString()}</p>
                    <p>Category: {transaction.category.join(', ')}</p>
                    {transaction.pending && <span className="badge">Pending</span>}
                  </div>
                  <div className="transaction-amount">
                    <span className={transaction.amount > 0 ? 'debit' : 'credit'}>
                      ${Math.abs(transaction.amount).toFixed(2)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PlaidData;