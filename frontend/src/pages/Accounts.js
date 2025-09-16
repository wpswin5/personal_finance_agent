import React, { useState, useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import PlaidIntegration from '../components/PlaidIntegration';
import './Accounts.css';

const Accounts = () => {
  const { getAccessTokenSilently, isAuthenticated } = useAuth0();
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const getToken = async () => {
      if (isAuthenticated) {
        try {
          const accessToken = await getAccessTokenSilently({
            audience: "https://fastapiexample.com",
            scope: "test:read"
          });
          setToken(accessToken);
        } catch (error) {
          console.error('Error getting access token:', error);
        } finally {
          setLoading(false);
        }
      }
    };

    getToken();
  }, [isAuthenticated, getAccessTokenSilently]);

  if (loading) {
    return (
      <div className="accounts-container">
        <div className="loading-spinner">Loading...</div>
      </div>
    );
  }

  if (!token) {
    return (
      <div className="accounts-container">
        <div className="error-message">
          Unable to authenticate. Please try refreshing the page.
        </div>
      </div>
    );
  }

  return (
    <div className="accounts-container">
      <PlaidIntegration token={token} />
    </div>
  );
};

export default Accounts;