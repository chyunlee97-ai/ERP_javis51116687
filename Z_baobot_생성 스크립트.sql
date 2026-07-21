USE [OHSUNGERP]
GO

/****** Object:  Table [dbo].[baobot]    Script Date: 2026-07-02 ¿ÀÈÄ 3:52:01 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[baobot](
	[obot_fact] [char](2) NOT NULL,
	[obot_keyx] [numeric](18, 0) IDENTITY(1,1) NOT NULL,
	[obot_gubn] [char](3) NOT NULL,
	[obot_tex1] [varchar](50) NULL,
	[obot_tex2] [varchar](50) NULL,
	[obot_tex3] [varchar](50) NULL,
	[obot_tex4] [varchar](50) NULL,
	[obot_tex5] [varchar](50) NULL,
	[obot_tex6] [varchar](50) NULL,
	[obot_tex7] [varchar](50) NULL,
	[obot_tex8] [varchar](50) NULL,
	[obot_tex9] [varchar](50) NULL,
	[obot_corp] [char](2) NULL,
	[obot_saup] [varchar](2) NULL,
	[obot_setl] [varchar](2) NULL,
	[obot_divi] [varchar](2) NULL,
	[obot_crid] [varchar](20) NULL,
	[obot_crsy] [varchar](14) NULL,
	[obot_crip] [varchar](30) NULL,
	[obot_mdid] [varchar](20) NULL,
	[obot_mdsy] [varchar](14) NULL,
	[obot_mdip] [varchar](30) NULL,
 CONSTRAINT [PK_baobot] PRIMARY KEY CLUSTERED 
(
	[obot_fact] ASC,
	[obot_keyx] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO


