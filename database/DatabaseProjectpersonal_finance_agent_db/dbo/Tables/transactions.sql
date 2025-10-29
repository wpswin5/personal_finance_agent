CREATE TABLE [dbo].[transactions] (
    [id]                INT             IDENTITY (1, 1) NOT NULL,
    [account_id]        NVARCHAR (255)  NOT NULL,
    [transaction_id]    NVARCHAR (255)  NOT NULL,
    [amount]            DECIMAL (18, 2) NOT NULL,
    [date_posted]       DATE            NOT NULL,
    [date_transacted]   DATE            NULL,
    [description]       NVARCHAR (500)  NULL,
    [merchant_name]     NVARCHAR (255)  NULL,
    [iso_currency_code] NVARCHAR (3)    NULL,
    [category]          NVARCHAR (255)  NULL,
    [manual_category]   NVARCHAR (255)  NULL,
    [is_pending]        BIT             DEFAULT ((0)) NULL,
    [created_at]        DATETIME2 (7)   DEFAULT (sysutcdatetime()) NULL,
    PRIMARY KEY CLUSTERED ([id] ASC),
    CONSTRAINT [FK_transactions_accountid] FOREIGN KEY ([account_id]) REFERENCES [dbo].[accounts] ([account_id]),
    UNIQUE NONCLUSTERED ([transaction_id] ASC)
);


GO

