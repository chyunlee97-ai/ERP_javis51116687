USE [OHSUNGERPVN]
GO

/****** Object:  Table [dbo].[obuspr]    Script Date: 2026-07-03 ¿ÀÈÄ 5:11:57 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[obuspr](
	[uspr_fact] [char](2) NOT NULL,
	[uspr_idno] [char](10) NOT NULL,
	[uspr_meid] [char](4) NOT NULL,
	[uspr_name] [varchar](50) NULL,
	[uspr_corp] [char](2) NULL,
	[uspr_saup] [varchar](2) NULL,
	[uspr_setl] [varchar](2) NULL,
	[uspr_divi] [varchar](2) NULL,
	[uspr_crid] [varchar](20) NULL,
	[uspr_crsy] [varchar](14) NULL,
	[uspr_crip] [varchar](30) NULL,
	[uspr_mdid] [varchar](20) NULL,
	[uspr_mdsy] [varchar](14) NULL,
	[uspr_mdip] [varchar](30) NULL,
 CONSTRAINT [PK_obuspr] PRIMARY KEY CLUSTERED 
(
	[uspr_fact] ASC,
	[uspr_idno] ASC,
	[uspr_meid] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO


