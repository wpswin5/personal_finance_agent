CREATE TABLE [dbo].[accounts] (
    [id]                INT             IDENTITY (1, 1) NOT NULL,
    [plaid_user_id]     INT             NOT NULL,
    [account_id]        NVARCHAR (255)  NOT NULL,
    [name]              NVARCHAR (255)  NULL,
    [mask]              NVARCHAR (4)    NULL,
    [official_name]     NVARCHAR (255)  NULL,
    [type]              NVARCHAR (50)   NULL,
    [subtype]           NVARCHAR (50)   NULL,
    [currency]          NVARCHAR (3)    NULL,
    [balance_available] DECIMAL (18, 2) NULL,
    [balance_current]   DECIMAL (18, 2) NULL,
    [last_synced_at]    DATETIME2 (7)   NULL,
    [nickname]          VARCHAR (100)   NULL,
    PRIMARY KEY CLUSTERED ([id] ASC),
    CONSTRAINT [FK_accounts_plaid_users] FOREIGN KEY ([plaid_user_id]) REFERENCES [dbo].[plaid_users] ([id]) ON DELETE CASCADE,
    UNIQUE NONCLUSTERED ([account_id] ASC)
);


GO

CREATE NONCLUSTERED INDEX [IX_accounts_plaid_user_id]
    ON [dbo].[accounts]([plaid_user_id] ASC);


GO

