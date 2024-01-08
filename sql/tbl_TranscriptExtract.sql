USE [MarketResearch]
GO

CREATE TABLE [dbo].[TranscriptExtract](
	[ID] [int] IDENTITY(1,1) NOT NULL,
	[Company_Name] [varchar](255) NOT NULL,
	[Concall_Date] [date] NOT NULL,
	[Moderator] [varchar](255) NULL,
	[CEO] [varchar](255) NULL,
	[CFO] [varchar](255) NULL,
	[Relations] [varchar](255) NULL,
	[QNA_1] [varchar](max) NULL,
	[QNA_2] [varchar](max) NULL,
	[QNA_3] [varchar](max) NULL,
	[QNA_4] [varchar](max) NULL,
	[QNA_5] [varchar](max) NULL,
	[QNA_6] [varchar](max) NULL,
	[QNA_7] [varchar](max) NULL,
	[QNA_8] [varchar](max) NULL,
	[QNA_9] [varchar](max) NULL,
	[QNA_10] [varchar](max) NULL,
	[QNA_11] [varchar](max) NULL,
	[QNA_12] [varchar](max) NULL,
 CONSTRAINT [pk_TranscriptExtract] PRIMARY KEY CLUSTERED 
(
	[Company_Name] ASC,
	[Concall_Date] ASC
)
) ON [PRIMARY]
GO


