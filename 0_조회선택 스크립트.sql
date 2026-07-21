

declare @fact char(2),         -- 공장구분
        @as_find varchar(30),  -- 조건
		@idno char(10),        -- 사용자 ID
		@lang char(2)          -- 언어  KR, EN, CH, VN, SP

set @fact = 'Y6'
set @as_find = '김'
set @as_find = '%'+ @as_find+ '%'
Set @lang ='KR'
Set @idno = 'Y6'

   SELECT '리스트'= CASE WHEN @lang = 'KR' THEN (case when isnull(code_name,'') <> '' then code_name else  code_code+'.'+code_engl end )
                         WHEN @lang = 'EN' THEN (case when isnull(code_engl,'') <> '' then code_engl else  code_code+'.'+code_engl end ) 
                         WHEN @lang = 'CH' THEN (case when isnull(code_chna,'') <> '' then code_chna else  code_code+'.'+code_engl end ) 
                         WHEN @lang = 'VN' THEN (case when isnull(code_vina,'') <> '' then code_vina else  code_code+'.'+code_engl end ) 
                         WHEN @lang = 'SP' THEN (case when isnull(code_span,'') <> '' then code_span else  code_code+'.'+code_engl end ) ELSE code_code+'.'+code_engl END
   
     FROM bacode
    WHERE code_gubn ='OBOT_PROG' and
          code_fact = @fact and
		  exists ( SELECT *
                     FROM obuspr
                    WHERE uspr_fact = code_fact and uspr_meid = code_code and
					      uspr_idno = @idno )

 ORDER BY code_sort
