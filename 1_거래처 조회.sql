declare @fact char(2),
        @as_find varchar(30)

set @fact = 'K1'
set @as_find = 'LG'


SELECT '거래처명' = CASE WHEN substring(vend_fact,2,1) ='1'  THEN isnull(vend_name,'') ELSE ( case when isnull(vend_nam3,'') ='' then isnull(vend_name,'') else 'Insert Vend Name!' end ) END,
	   '거래처번호' = vend_keyx
  FROM acvend
 WHERE vend_fact = @fact and
       ( (vend_name like '%'+@as_find+'%') or (vend_nam3 like '%'+@as_find+'%') or (vend_keyx like '%'+@as_find+'%') ) -- # 거래처 조회시 거래처명 과 거래처번호 일부분을 가지고 조회 가능


	   select vend_name, vend_nam3,*
	   from acvend
	   where vend_fact ='Y6'
