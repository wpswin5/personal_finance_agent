import React, { useState, useCallback, useEffect } from 'react';
import { usePlaidLink } from 'react-plaid-link';

const PlaidLink = ({ onSuccess, onError, token }) => {
  const [linkToken, setLinkToken] = useState(null);
  const [loading, setLoading] = useState(false);
  const [hasConnections, setHasConnections] = useState(false);

  // Create link token
  const createLinkToken = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/plaid/create_link_token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          user_id: 'current_user' // This will be handled by the backend using the JWT token
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create link token');
      }

      const data = await response.json();
      setLinkToken(data.link_token);
    } catch (error) {
      console.error('Error creating link token:', error);
      onError && onError(error);
    } finally {
      setLoading(false);
    }
  };

  

  // Check backend for existing connections to adjust button label
  useEffect(() => {
    let mounted = true;
    const checkConnections = async () => {
      try {
        const idResp = await fetch('http://localhost:8000/user/id', {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!idResp.ok) return;
        const userId = await idResp.json();

        const resp = await fetch(`http://localhost:8000/accounts/${userId}/connections`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!resp.ok) return;
        const data = await resp.json();
        if (mounted) setHasConnections((data.plaid_users || []).length > 0);
      } catch (err) {
        // Non-fatal: leave hasConnections false if check fails
        console.warn('Failed to check existing connections:', err);
      }
    };

    if (token) checkConnections();
    return () => { mounted = false; };
  }, [token]);

  // Handle successful link
  const handleOnSuccess = useCallback(async (public_token, metadata) => {
    try {
      const response = await fetch('http://localhost:8000/plaid/exchange_public_token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ 
          public_token,
          user_id: 'current_user' // will be handled by backend
        }),
      });

      if (!response.ok) { throw new Error('Failed to exchange public token'); }

      const { item_id } = await response.json();

      await fetch(`http://localhost:8000/plaid/sync_item`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ item_id }),
      });

      onSuccess && onSuccess(item_id, metadata);
    } catch (error) {
      console.error('Error exchanging public token:', error);
      onError && onError(error);
    }
  }, [token, onSuccess, onError]);

  // Configure Plaid Link
  const config = {
    token: linkToken,
    onSuccess: handleOnSuccess,
    onError: (error) => {
      console.error('Plaid Link error:', error);
      onError && onError(error);
    },
    onExit: (error, metadata) => {
      if (error) {
        console.error('Plaid Link exit error:', error);
        onError && onError(error);
      }
    },
  };

  const { open, ready } = usePlaidLink(config);

  // When linkToken becomes available and Plaid Link is ready, open automatically
  useEffect(() => {
    if (linkToken && ready) {
      try {
        open();
      } catch (err) {
        console.error('Failed to open Plaid Link:', err);
      }
    }
  }, [linkToken, ready]);

  return (
    <div className="plaid-link-container">
      {!linkToken ? (
        <button
          onClick={createLinkToken}
          disabled={loading}
          className="btn btn-primary"
        >
          {loading ? 'Creating Link...' : (hasConnections ? 'Connect Another Account' : 'Connect Bank Account')}
        </button>
      ) : (
        <button 
          onClick={() => open()} 
          disabled={!ready}
          className="btn btn-success"
        >
          {ready ? 'Connect to Bank' : 'Loading...'}
        </button>
      )}
    </div>
  );
};

export default PlaidLink;