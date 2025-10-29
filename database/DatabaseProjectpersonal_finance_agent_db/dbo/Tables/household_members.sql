CREATE TABLE [dbo].[household_members] (
    [id]           INT           IDENTITY (1, 1) NOT NULL,
    [household_id] INT           NOT NULL,
    [user_id]      INT           NOT NULL,
    [role]         NVARCHAR (50) DEFAULT ('member') NULL,
    [created_at]   DATETIME2 (7) DEFAULT (sysutcdatetime()) NULL,
    PRIMARY KEY CLUSTERED ([id] ASC),
    CONSTRAINT [FK_household_members_households] FOREIGN KEY ([household_id]) REFERENCES [dbo].[households] ([id]) ON DELETE CASCADE,
    CONSTRAINT [FK_household_members_users] FOREIGN KEY ([user_id]) REFERENCES [dbo].[users] ([id]) ON DELETE CASCADE
);


GO

CREATE NONCLUSTERED INDEX [IX_household_members_user_id]
    ON [dbo].[household_members]([user_id] ASC);


GO

