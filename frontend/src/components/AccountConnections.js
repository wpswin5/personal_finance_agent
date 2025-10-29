import React, { useState, useEffect } from "react";
import axios from "axios";
import { Edit } from 'lucide-react';
import "./AccountConnections.css";

const AccountConnections = ({ token, plaidConnected, setPlaidConnected, connectionsRefreshKey }) => {
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  // static display: no collapse state needed

  // Inline edit state
  const [editingAccountId, setEditingAccountId] = useState(null);
  const [editingNickname, setEditingNickname] = useState("");
  const [editingSaving, setEditingSaving] = useState(false);
  // --------------------------------

  // Fetch user ID
  const fetchUserId = async () => {
    try {
      const response = await axios.get("http://localhost:8000/user/id", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.status !== 200) {
        throw new Error(`Failed to fetch user id (status ${response.status})`);
      }
      return response.data;
    } catch (err) {
      // Bubble up a clearer message for the UI
      const msg = err?.response?.data?.detail || err.message || "Failed to fetch user id";
      throw new Error(msg);
    }
  };

  // Fetch user connections
  const fetchConnections = async () => {
    setLoading(true);
    setError(null);
    try {
      const userId = await fetchUserId();
      const resp = await axios.get(`http://localhost:8000/accounts/${userId}/connections`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (resp.status !== 200) throw new Error(`Failed to fetch connections (status ${resp.status})`);
      const data = resp.data;
      const users = data.plaid_users || [];
      setConnections(users);

      // Notify parent that we have existing connections so other components
      // (which rely on `plaidConnected`) can update their UI accordingly.
      if (typeof setPlaidConnected === 'function') {
        setPlaidConnected(users.length > 0);
      }
    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Delete a connection
  const deleteConnection = async (connectionId) => {
    if (!window.confirm("Are you sure you want to delete this connection?")) return;
    try {
      const response = await fetch(`http://localhost:8000/plaid/connections/${connectionId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error("Failed to delete connection");
      fetchConnections();
    } catch (err) {
      setError(err.message);
    }
  };

  // --- inline nickname handlers ---
  const startEditing = (account) => {
    setEditingAccountId(account.account_id);
    setEditingNickname(account.nickname || account.name || "");
  };

  const cancelEditing = () => {
    setEditingAccountId(null);
    setEditingNickname("");
  };

  const saveNickname = async (account) => {
    if (!account) return;
    setEditingSaving(true);
    try {
      const res = await fetch(`http://localhost:8000/accounts/${account.id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ nickname: editingNickname }),
      });

      if (!res.ok) {
        const text = await res.text().catch(() => null);
        throw new Error(text || res.statusText || `HTTP ${res.status}`);
      }

      // Update the account locally
      setConnections((prev) =>
        prev.map((conn) => ({
          ...conn,
          accounts: conn.accounts.map((acc) =>
            acc.account_id === account.account_id ? { ...acc, nickname: editingNickname } : acc
          ),
        }))
      );

      // Clear editing state
      setEditingAccountId(null);
      setEditingNickname("");
    } catch (err) {
      console.error("Failed to update nickname:", err);
      alert("Failed to update nickname. " + (err.message || "Please try again."));
    } finally {
      setEditingSaving(false);
    }
  };
  // --------------------------------


  // Fetch connections on mount when we have a token so existing
  // connections are visible even before a new Plaid flow occurs.
  useEffect(() => {
    if (token) fetchConnections();
  }, [token]);

  // Re-fetch when parent signals a refresh (e.g. after a new Plaid connection)
  useEffect(() => {
    if (token && typeof connectionsRefreshKey !== 'undefined') {
      fetchConnections();
    }
  }, [connectionsRefreshKey]);

  // Also re-fetch when a new Plaid connection is established elsewhere
  useEffect(() => {
    if (plaidConnected && token) fetchConnections();
  }, [plaidConnected, token]);

  return (
    <div className="plaid-data-container">
      {error && <div className="alert alert-danger">Error: {error}</div>}
      {loading && <div className="loading">Loading...</div>}

      <div className="connections-tab">
        <h3>Existing Bank Connections</h3>

        {connections.length === 0 ? (
          <p>No bank connections found.</p>
        ) : (
          <div className="connections-list-vertical">
            {connections.map((connection) => (
              <div key={connection.id} className="connection-block">
                <div className="connection-card">
                  <div className="connection-header">
                    <div className="connection-title">
                      <h4>{connection.institution_name || "Unknown Institution"}</h4>
                    </div>
                    <div className="connection-meta">
                      <p>Accounts: {connection.accounts?.length || 0}</p>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => deleteConnection(connection.id)}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>

                <div className="accounts-list">
                  {connection.accounts?.length > 0 ? (
                    connection.accounts.map((account) => (
                      <div key={account.account_id} className="account-row">
                        <div className="account-left">
                          <h5 className="account-name">
                            {editingAccountId === account.account_id ? (
                              <div className="inline-edit">
                                <input
                                  className="inline-edit-input"
                                  value={editingNickname}
                                  onChange={(e) => setEditingNickname(e.target.value)}
                                />
                                <div className="inline-edit-actions">
                                  <button
                                    className="btn btn-sm"
                                    onClick={() => saveNickname(account)}
                                    disabled={editingSaving}
                                  >
                                    {editingSaving ? "Saving..." : "Save"}
                                  </button>
                                  <button
                                    className="btn btn-sm"
                                    onClick={cancelEditing}
                                    disabled={editingSaving}
                                    style={{ background: 'transparent' }}
                                  >
                                    Cancel
                                  </button>
                                </div>
                              </div>
                            ) : (
                              <>
                                {account.nickname || account.name}
                                <button
                                  className="edit-nickname"
                                  title="Edit nickname"
                                  onClick={() => startEditing(account)}
                                  aria-label={`Edit nickname for ${account.nickname || account.name}`}
                                >
                                  <Edit size={16} />
                                </button>
                              </>
                            )}
                          </h5>
                          <p className="account-meta">Type: {account.type} {account.subtype && `(${account.subtype})`}</p>
                        </div>

                        <div className="account-right">
                          <p className="account-balance">${account.balance_current.toFixed(2)} {account.currency}</p>
                          <button
                            className="btn btn-danger btn-sm"
                            onClick={() => {
                              if (window.confirm('Are you sure you want to delete this account?')) {
                                deleteConnection(connection.id);
                              }
                            }}
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="no-accounts">No accounts found.</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* inline editing — modal removed */}
    </div>
  );
};

export default AccountConnections;
