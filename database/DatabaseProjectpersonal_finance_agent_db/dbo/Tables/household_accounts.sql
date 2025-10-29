CREATE TABLE [dbo].[household_accounts] (
    [id]                INT IDENTITY (1, 1) NOT NULL,
    [household_id]      INT NOT NULL,
    [account_id]        INT NOT NULL,
    [shared_by_user_id] INT NOT NULL,
    PRIMARY KEY CLUSTERED ([id] ASC),
    CONSTRAINT [FK_household_accounts_accounts] FOREIGN KEY ([account_id]) REFERENCES [dbo].[accounts] ([id]) ON DELETE CASCADE,
    CONSTRAINT [FK_household_accounts_households] FOREIGN KEY ([household_id]) REFERENCES [dbo].[households] ([id]) ON DELETE CASCADE,
    CONSTRAINT [FK_household_accounts_users] FOREIGN KEY ([shared_by_user_id]) REFERENCES [dbo].[users] ([id]) ON DELETE CASCADE,
    CONSTRAINT [UQ_household_accounts] UNIQUE NONCLUSTERED ([household_id] ASC, [account_id] ASC)
);


GO

CREATE NONCLUSTERED INDEX [IX_household_accounts_account_id]
    ON [dbo].[household_accounts]([account_id] ASC);


GO

