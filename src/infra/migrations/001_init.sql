-- Drop tables if re-running (for dev only, remove in prod!)
IF OBJECT_ID('dbo.transactions', 'U') IS NOT NULL DROP TABLE dbo.transactions;
IF OBJECT_ID('dbo.categories', 'U') IS NOT NULL DROP TABLE dbo.categories;
IF OBJECT_ID('dbo.anomalies', 'U') IS NOT NULL DROP TABLE dbo.anomalies;
IF OBJECT_ID('dbo.monthly_summaries', 'U') IS NOT NULL DROP TABLE dbo.monthly_summaries;

-- Categories (master table of spending categories)
CREATE TABLE categories (
    id INT IDENTITY PRIMARY KEY,
    name NVARCHAR(100) NOT NULL UNIQUE
);

-- Transactions (raw + enriched)
CREATE TABLE transactions (
    id INT IDENTITY PRIMARY KEY,
    user_id NVARCHAR(100) NOT NULL,
    posted_at DATE NOT NULL,
    amount DECIMAL(18,2) NOT NULL,
    currency NVARCHAR(10) DEFAULT 'USD',
    merchant_name NVARCHAR(255),
    description NVARCHAR(500),
    category_id INT NULL,
    category_pred NVARCHAR(50),
    category_conf FLOAT,
    source NVARCHAR(50) DEFAULT 'upload',
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Anomalies (flag unusual spending)
CREATE TABLE anomalies (
    id INT IDENTITY PRIMARY KEY,
    transaction_id INT NOT NULL,
    anomaly_score FLOAT NOT NULL,
    detected_at DATETIME DEFAULT GETDATE(),
    notes NVARCHAR(500),
    FOREIGN KEY (transaction_id) REFERENCES transactions(id)
);

-- Monthly summaries (pre-computed rollups for faster insights)
CREATE TABLE monthly_summaries (
    id INT IDENTITY PRIMARY KEY,
    user_id NVARCHAR(100) NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    total_spend DECIMAL(18,2),
    avg_daily_spend DECIMAL(18,2),
    highest_category NVARCHAR(100),
    created_at DATETIME DEFAULT GETDATE()
);

-- Seed categories
INSERT INTO categories (name) VALUES
('Groceries'),
('Rent'),
('Subscriptions'),
('Dining'),
('Transportation'),
('Utilities'),
('Shopping'),
('Entertainment'),
('Travel'),
('Healthcare');
