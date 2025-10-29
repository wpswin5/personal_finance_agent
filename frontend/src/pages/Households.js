import React from 'react';
import '../styles/shared.css';

const Households = () => {
  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Households</h1>
        <p className="muted">API endpoints are in progress — this is a placeholder for now.</p>
      </div>

      <div className="card">
        <p>
          Households will surface family/linked accounts and aggregated balances. For now
          this page is intentionally lightweight while backend endpoints are being prepared.
        </p>
      </div>
    </div>
  );
};

export default Households;
