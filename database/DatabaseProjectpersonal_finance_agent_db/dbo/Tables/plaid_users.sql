CREATE TABLE [dbo].[plaid_users] (
    [id]               INT            IDENTITY (1, 1) NOT NULL,
    [user_id]          INT            NULL,
    [access_token]     NVARCHAR (MAX) NULL,
    [item_id]          NVARCHAR (255) NULL,
    [institution_name] NVARCHAR (255) NULL,
    [created_at]       DATETIME2 (7)  DEFAULT (getdate()) NULL,
    [cursor]           VARCHAR (MAX)  NULL,
    PRIMARY KEY CLUSTERED ([id] ASC),
    FOREIGN KEY ([user_id]) REFERENCES [dbo].[users] ([id])
);


GO

CREATE NONCLUSTERED INDEX [IX_plaid_users_user_id]
    ON [dbo].[plaid_users]([user_id] ASC);


GO

