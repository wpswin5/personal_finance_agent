import React, { useState, useEffect } from "react";
import axios from "axios";
import "./AccountConnections.css";

const AccountConnections = ({ token, plaidConnected }) => {
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expanded, setExpanded] = useState({}); // Track open/closed connections

  // --- new nickname modal state ---
  const [nicknameModalOpen, setNicknameModalOpen] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [nicknameInput, setNicknameInput] = useState("");
  const [savingNickname, setSavingNickname] = useState(false);
  // --------------------------------

  // Fetch user ID
  const fetchUserId = async () => {
    const response = await axios.get("http://localhost:8000/user/id", {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (response.statusText !== "OK") throw new Error("Failed to fetch user info");
    return response.data;
  };

  // Fetch user connections
  const fetchConnections = async () => {
    setLoading(true);
    setError(null);
    try {
      const userId = await fetchUserId();
      const response = await fetch(`http://localhost:8000/accounts/${userId}/connections`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error("Failed to fetch connections");
      const data = await response.json();
      setConnections(data.plaid_users || []);
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

  // --- new nickname handlers ---
  const handleAddNicknameClick = (account) => {
    setSelectedAccount(account);
    setNicknameInput(account.nickname || "");
    setNicknameModalOpen(true);
  };

  const handleNicknameSubmit = async () => {
    if (!selectedAccount) return;
    setSavingNickname(true);
    try {
      const res = await fetch(`http://localhost:8000/accounts/${selectedAccount.id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ nickname: nicknameInput }),
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
            acc.account_id === selectedAccount.account_id
              ? { ...acc, nickname: nicknameInput }
              : acc
          ),
        }))
      );

      setNicknameModalOpen(false);
      setSelectedAccount(null);
      setNicknameInput("");
    } catch (err) {
      console.error("Failed to update nickname:", err);
      alert("Failed to update nickname. " + (err.message || "Please try again."));
    } finally {
      setSavingNickname(false);
    }
  };
  // --------------------------------

  const toggleExpand = (id) => {
    setExpanded((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  useEffect(() => {
    if (plaidConnected && token) fetchConnections();
  }, [plaidConnected, token]);

  if (!plaidConnected) {
    return <div className="alert alert-info">Connect a bank account to view your financial data.</div>;
  }

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
            {connections.map((connection) => {
              const isOpen = expanded[connection.id];
              return (
                <div key={connection.id} className="connection-block">
                  <div className="connection-card">
                    <div
                      className="connection-header"
                      onClick={() => toggleExpand(connection.id)}
                    >
                      <div className="connection-title">
                        <span className={`chevron ${isOpen ? "open" : ""}`}>▸</span>
                        <h4>{connection.institution_name || "Unknown Institution"}</h4>
                      </div>
                      <div className="connection-meta">
                        <p>Accounts: {connection.accounts?.length || 0}</p>
                        <button
                          className="btn btn-danger btn-sm"
                          onClick={(e) => {
                            e.stopPropagation(); // prevent collapsing when deleting
                            deleteConnection(connection.id);
                          }}
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>

                  <div className={`accounts-collapsible ${isOpen ? "expanded" : ""}`}>
                    {connection.accounts?.length > 0 ? (
                      connection.accounts.map((account) => (
                        <div key={account.account_id} className="account-card">
                          <h5>{account.nickname || account.name}</h5>
                          <p>
                            Type: {account.type}{" "}
                            {account.subtype && `(${account.subtype})`}
                          </p>
                          <p>
                            Balance: ${account.balance_current.toFixed(2)} {account.currency}
                          </p>
                          <button
                            className="btn btn-secondary btn-sm"
                            onClick={() => handleAddNicknameClick(account)}
                          >
                            Add Nickname
                          </button>
                        </div>
                      ))
                    ) : (
                      <p className="no-accounts">No accounts found.</p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* --- nickname modal --- */}
      {nicknameModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3>Add Nickname</h3>
            <p>
              Account: <strong>{selectedAccount?.name}</strong>
            </p>
            <input
              type="text"
              value={nicknameInput}
              onChange={(e) => setNicknameInput(e.target.value)}
              placeholder="Enter nickname"
              className="nickname-input"
            />
            <div className="modal-actions">
              <button
                type="button"
                onClick={() => {
                  setNicknameModalOpen(false);
                  setSelectedAccount(null);
                }}
                disabled={savingNickname}
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleNicknameSubmit}
                disabled={savingNickname}
              >
                {savingNickname ? "Saving..." : "Save"}
              </button>
            </div>
          </div>
        </div>
      )}
      {/* ---------------------- */}
    </div>
  );
};

export default AccountConnections;
