CREATE TABLE [dbo].[spending_goals] (
    [id]           INT             IDENTITY (1, 1) NOT NULL,
    [user_id]      INT             NULL,
    [household_id] INT             NULL,
    [category]     NVARCHAR (255)  NOT NULL,
    [amount_limit] DECIMAL (18, 2) NOT NULL,
    [period]       NVARCHAR (50)   NOT NULL,
    [testing]       BIT             DEFAULT ((0)) NOT NULL,
    [created_at]   DATETIME2 (7)   DEFAULT (sysutcdatetime()) NULL,
    PRIMARY KEY CLUSTERED ([id] ASC),
    CONSTRAINT [FK_spending_goals_households] FOREIGN KEY ([household_id]) REFERENCES [dbo].[households] ([id]) ON DELETE CASCADE,
    CONSTRAINT [FK_spending_goals_users] FOREIGN KEY ([user_id]) REFERENCES [dbo].[users] ([id]) ON DELETE CASCADE
);


GO

