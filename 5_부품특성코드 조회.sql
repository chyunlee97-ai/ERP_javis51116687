declare @fact char(2),
        @as_find varchar(30)

set @fact = 'K1'
set @as_find = 'B'

-- 부품특성코드 조회
SELECT '특성명' = tcod_name,
       '특성코드' = tcod_tcod
  FROM mptcod
 WHERE tcod_fact = @fact and
       ( (tcod_name like '%'+@as_find+'%') or (tcod_tcod like '%'+@as_find+'%') )