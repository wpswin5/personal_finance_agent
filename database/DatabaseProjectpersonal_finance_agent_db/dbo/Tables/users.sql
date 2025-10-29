CREATE TABLE [dbo].[users] (
    [id]         INT            IDENTITY (1, 1) NOT NULL,
    [sub]        NVARCHAR (255) NOT NULL,
    [email]      NVARCHAR (255) NOT NULL,
    [name]       NVARCHAR (255) NULL,
    [created_at] DATETIME2 (7)  DEFAULT (getutcdate()) NULL,
    [updated_at] DATETIME2 (7)  DEFAULT (getutcdate()) NULL,
    PRIMARY KEY CLUSTERED ([id] ASC),
    UNIQUE NONCLUSTERED ([email] ASC),
    UNIQUE NONCLUSTERED ([sub] ASC)
);


GO

