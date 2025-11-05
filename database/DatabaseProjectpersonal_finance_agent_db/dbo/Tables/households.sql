CREATE TABLE [dbo].[households] (
    [id]         INT            IDENTITY (1, 1) NOT NULL,
    [name]       NVARCHAR (255) NOT NULL,
    [owner_id]   INT            NOT NULL,
    [created_at] DATETIME2 (7)  DEFAULT (sysutcdatetime()) NULL,
    PRIMARY KEY CLUSTERED ([id] ASC)
);


GO

