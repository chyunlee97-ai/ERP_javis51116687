declare @fact char(2),
        @as_find varchar(30)

set @fact = 'K1'
set @as_find = '4'

-- TITLE: 부품상세정보 조회, 제품상세정보 조회, 제품상세 조회, 부품정보상세 조회, 제품정보상세 조회
      SELECT '부품번호' = part_part,
             '부품명' = part_name,
			 '단위' = isnull(part_unix,''),
			 '규격' = isnull(part_spec,''),
			 '특성코드' = part_tcod,			 
			 '구분' =  CASE WHEN isnull(tcod_assy,'1') = '1' THEN '원재료' ELSE '재공품' END
        FROM mppart_v	     
       WHERE part_fact = @fact and
             ( (part_part like '%'+@as_find+'%') or (part_name like '%'+@as_find+'%') )
    ORDER BY part_part ASC