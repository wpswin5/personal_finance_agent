# Plaid Integration Setup Guide

This guide explains how to set up and use the Plaid integration for secure financial data access in your Personal Finance Agent application.

## Overview

The Plaid integration provides:
- Secure bank account connection via Plaid Link
- Encrypted storage of access tokens
- Real-time account and transaction data
- Support for multiple bank connections per user

## Backend Components

### 1. Configuration (`app/config.py`)
- Added Plaid client credentials
- Added encryption key for sensitive data storage

### 2. Encryption Service (`app/security/encryption.py`)
- AES-256 encryption for access tokens
- Secure key derivation using PBKDF2
- Base64 encoding for database storage

### 3. Plaid Service (`app/services/plaid_service.py`)
- Plaid API client configuration
- Link token creation
- Public token exchange
- Account and transaction retrieval
- Institution name lookup

### 4. Database Service (`app/services/plaid_db_service.py`)
- Encrypted access token storage
- User-Plaid connection management
- CRUD operations for plaid_users table

### 5. API Routes (`app/routers/plaid.py`)
- `POST /plaid/create_link_token` - Create Plaid Link token
- `POST /plaid/exchange_public_token` - Exchange public token for access token
- `GET /plaid/accounts` - Get user's bank accounts
- `GET /plaid/transactions` - Get user's transactions
- `GET /plaid/connections` - Get user's Plaid connections
- `DELETE /plaid/connections/{id}` - Delete a Plaid connection

## Frontend Components

### 1. PlaidLink Component (`components/PlaidLink.js`)
- Handles Plaid Link initialization
- Creates link tokens
- Exchanges public tokens

### 2. PlaidData Component (`components/PlaidData.js`)
- Displays accounts, transactions, and connections
- Manages connection deletion
- Tabbed interface for different data views

### 3. PlaidIntegration Component (`components/PlaidIntegration.js`)
- Main integration component
- Combines PlaidLink and PlaidData
- Handles success/error states

## Setup Instructions

### 1. Environment Variables

Add the following to your `.env` file:

```env
# Plaid Configuration
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret
PLAID_ENV=sandbox  # or development/production

# Encryption Key (32 bytes for AES-256)
ENCRYPTION_KEY=your-super-secret-32-byte-key-here-change-this-in-production
```

### 2. Database Schema

Ensure your database has the required tables:

```sql
-- Users table (should already exist)
CREATE TABLE users (
    id INT PRIMARY KEY IDENTITY(1,1),
    sub NVARCHAR(255) UNIQUE NOT NULL, -- from Auth0 "sub"
    email NVARCHAR(255),
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);

-- Plaid users table (should already exist)
CREATE TABLE plaid_users (
    id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT FOREIGN KEY REFERENCES [dbo].[users](id),
    access_token NVARCHAR(MAX), -- encrypted before storage
    item_id NVARCHAR(255),
    institution_name NVARCHAR(255),
    created_at DATETIME2 DEFAULT GETDATE()
);
```

### 3. Install Dependencies

Backend:
```bash
cd backend
pip install -r requirements.txt
```

Frontend:
```bash
cd frontend
npm install react-plaid-link
```

### 4. Start the Application

Backend:
```bash
cd backend
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:
```bash
cd frontend
npm start
```

## Usage Examples

### 1. Basic Integration

```jsx
import React from 'react';
import PlaidIntegration from './components/PlaidIntegration';

function App() {
  const [authToken, setAuthToken] = useState(null);

  return (
    <div className="App">
      {authToken && (
        <PlaidIntegration token={authToken} />
      )}
    </div>
  );
}
```

### 2. API Usage

#### Create Link Token
```javascript
const response = await fetch('/api/plaid/create_link_token', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  },
  body: JSON.stringify({
    user_id: 'current_user'
  }),
});
```

#### Exchange Public Token
```javascript
const response = await fetch('/api/plaid/exchange_public_token', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  },
  body: JSON.stringify({
    public_token: publicToken,
    user_id: 'current_user'
  }),
});
```

#### Get Accounts
```javascript
const response = await fetch('/api/plaid/accounts', {
  headers: {
    'Authorization': `Bearer ${token}`,
  },
});
```

#### Get Transactions
```javascript
const response = await fetch('/api/plaid/transactions?count=50&start_date=2024-01-01', {
  headers: {
    'Authorization': `Bearer ${token}`,
  },
});
```

## Security Features

### 1. Access Token Encryption
- All Plaid access tokens are encrypted using AES-256 before database storage
- Encryption key is derived using PBKDF2 with 100,000 iterations
- Tokens are automatically decrypted when making Plaid API calls

### 2. User Authentication
- All endpoints require valid JWT authentication
- User access is restricted to their own data only
- Auth0 integration for secure user management

### 3. Data Protection
- No sensitive data is logged
- Access tokens are never returned in API responses
- Secure HTTPS communication with Plaid APIs

## Error Handling

The integration includes comprehensive error handling:

- **Link Token Creation**: Handles Plaid API errors and invalid user states
- **Token Exchange**: Validates public tokens and handles exchange failures
- **Data Retrieval**: Manages API rate limits and connection issues
- **Database Operations**: Handles SQL errors and connection issues

## Testing

### 1. Sandbox Environment
The integration is configured to use Plaid's sandbox environment by default. This allows testing with fake bank credentials:

- Username: `user_good`
- Password: `pass_good`

### 2. Test Institutions
Plaid sandbox provides several test institutions:
- First Platypus Bank
- Tartan Bank
- Houndstooth Bank

## Production Considerations

### 1. Environment Configuration
- Change `PLAID_ENV` to `production`
- Use production Plaid credentials
- Generate a secure 32-byte encryption key
- Enable HTTPS for all communications

### 2. Security Hardening
- Rotate encryption keys regularly
- Implement key management system
- Add rate limiting to API endpoints
- Monitor for suspicious activity

### 3. Compliance
- Ensure PCI DSS compliance if handling payment data
- Implement data retention policies
- Add audit logging for sensitive operations
- Regular security assessments

## Troubleshooting

### Common Issues

1. **Link Token Creation Fails**
   - Check Plaid credentials in `.env`
   - Verify user exists in database
   - Check Auth0 token validity

2. **Public Token Exchange Fails**
   - Ensure public token is valid and not expired
   - Check Plaid environment configuration
   - Verify database connection

3. **Data Retrieval Issues**
   - Check if access token is properly encrypted/decrypted
   - Verify Plaid API permissions
   - Check for expired or revoked access tokens

4. **Frontend Integration Issues**
   - Ensure `react-plaid-link` is properly installed
   - Check API endpoint URLs
   - Verify CORS configuration

### Debugging

Enable debug logging by setting log level to DEBUG in your application configuration. This will provide detailed information about:
- Plaid API requests and responses
- Encryption/decryption operations
- Database queries
- Authentication flows

## Support

For additional support:
1. Check Plaid documentation: https://plaid.com/docs/
2. Review Plaid API status: https://status.plaid.com/
3. Contact Plaid support for API-related issues
4. Review application logs for detailed error information