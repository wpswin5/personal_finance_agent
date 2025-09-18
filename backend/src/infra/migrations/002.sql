-- 002.sql

-- ==========================================
-- Drop legacy tables (safe if they exist)
-- ==========================================
IF OBJECT_ID('dbo.transactions', 'U') IS NOT NULL
    DROP TABLE dbo.transactions;
	
IF OBJECT_ID('dbo.anomalies', 'U') IS NOT NULL
    DROP TABLE dbo.anomalies;

IF OBJECT_ID('dbo.categories', 'U') IS NOT NULL
    DROP TABLE dbo.categories;

IF OBJECT_ID('dbo.monthly_summaries', 'U') IS NOT NULL
    DROP TABLE dbo.monthly_summaries;


-- ==========================================
-- New Schema (retains dbo.users and dbo.plaid_users)
-- ==========================================

-- Accounts
IF OBJECT_ID('dbo.accounts', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.accounts (
        id INT IDENTITY(1,1) PRIMARY KEY,
        plaid_user_id INT NOT NULL,
        account_id NVARCHAR(255) NOT NULL UNIQUE,
        name NVARCHAR(255),
        mask NVARCHAR(4),
        official_name NVARCHAR(255),
        type NVARCHAR(50),
        subtype NVARCHAR(50),
        currency NVARCHAR(3),
        balance_available DECIMAL(18,2),
        balance_current DECIMAL(18,2),
        last_synced_at DATETIME2,
        CONSTRAINT FK_accounts_plaid_users FOREIGN KEY (plaid_user_id)
            REFERENCES dbo.plaid_users(id)
            ON DELETE CASCADE
    );
END

-- Transactions
IF OBJECT_ID('dbo.transactions', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.transactions (
        id INT IDENTITY(1,1) PRIMARY KEY,
        account_id INT NOT NULL,
        transaction_id NVARCHAR(255) NOT NULL UNIQUE,
        amount DECIMAL(18,2) NOT NULL,
        date_posted DATE NOT NULL,
        date_transacted DATE,
        description NVARCHAR(500),
        merchant_name NVARCHAR(255),
        iso_currency_code NVARCHAR(3),
        category NVARCHAR(255),
        manual_category NVARCHAR(255) NULL,
        is_pending BIT DEFAULT 0,
        created_at DATETIME2 DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_transactions_accounts FOREIGN KEY (account_id)
            REFERENCES dbo.accounts(id)
            ON DELETE CASCADE
    );
END

-- Households
IF OBJECT_ID('dbo.households', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.households (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(255) NOT NULL,
        created_at DATETIME2 DEFAULT SYSUTCDATETIME()
    );
END

-- Household Members
IF OBJECT_ID('dbo.household_members', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.household_members (
        id INT IDENTITY(1,1) PRIMARY KEY,
        household_id INT NOT NULL,
        user_id INT NOT NULL,
        role NVARCHAR(50) DEFAULT 'member',
        created_at DATETIME2 DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_household_members_households FOREIGN KEY (household_id)
            REFERENCES dbo.households(id)
            ON DELETE CASCADE,
        CONSTRAINT FK_household_members_users FOREIGN KEY (user_id)
            REFERENCES dbo.users(id)
            ON DELETE CASCADE
    );
END

-- Household Accounts
IF OBJECT_ID('dbo.household_accounts', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.household_accounts (
        id INT IDENTITY(1,1) PRIMARY KEY,
        household_id INT NOT NULL,
        account_id INT NOT NULL,
        shared_by_user_id INT NOT NULL,
        CONSTRAINT FK_household_accounts_households FOREIGN KEY (household_id)
            REFERENCES dbo.households(id)
            ON DELETE CASCADE,
        CONSTRAINT FK_household_accounts_accounts FOREIGN KEY (account_id)
            REFERENCES dbo.accounts(id)
            ON DELETE CASCADE,
        CONSTRAINT FK_household_accounts_users FOREIGN KEY (shared_by_user_id)
            REFERENCES dbo.users(id)
            ON DELETE CASCADE,
        CONSTRAINT UQ_household_accounts UNIQUE (household_id, account_id)
    );
END

-- Spending Goals
IF OBJECT_ID('dbo.spending_goals', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.spending_goals (
        id INT IDENTITY(1,1) PRIMARY KEY,
        user_id INT NULL,
        household_id INT NULL,
        category NVARCHAR(255) NOT NULL,
        amount_limit DECIMAL(18,2) NOT NULL,
        period NVARCHAR(50) NOT NULL, -- e.g. monthly, weekly
        created_at DATETIME2 DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_spending_goals_users FOREIGN KEY (user_id)
            REFERENCES dbo.users(id)
            ON DELETE CASCADE,
        CONSTRAINT FK_spending_goals_households FOREIGN KEY (household_id)
            REFERENCES dbo.households(id)
            ON DELETE CASCADE
    );
END

-- ==========================================
-- Indexes for performance
-- ==========================================
CREATE INDEX IX_transactions_account_id ON dbo.transactions(account_id);
CREATE INDEX IX_accounts_plaid_user_id ON dbo.accounts(plaid_user_id);
CREATE INDEX IX_household_members_user_id ON dbo.household_members(user_id);
CREATE INDEX IX_household_accounts_account_id ON dbo.household_accounts(account_id);
