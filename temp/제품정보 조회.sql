declare @fact char(2),
        @as_find varchar(30)

set @fact = 'Y1'
set @as_find = '4'

-- TITLE: 모델정보 조회, 제품정보 조회, 제품 조회
IF substring(@fact,1,1) <> 'Y'
   BEGIN
      SELECT '당사모델번호' = modl_modl,
	         '영업모델' = modl_key2,
             '제품명' = modl_name
        FROM bumodl
       WHERE modl_fact = @fact and
             ( (modl_key2 like '%'+@as_find+'%') or (modl_modl like '%'+@as_find+'%') )
    ORDER BY modl_modl ASC
   END

IF substring(@fact,1,1) = 'Y'  -- DNE는 영업모델=당사모델 동일
   BEGIN
      SELECT '영업모델' = modl_key2,
             '제품명' = modl_name			 
        FROM bumodl
       WHERE modl_fact = @fact and
             ( (modl_key2 like '%'+@as_find+'%') or (modl_modl like '%'+@as_find+'%') )
    ORDER BY modl_modl ASC
   END