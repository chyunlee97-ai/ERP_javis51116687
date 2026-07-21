declare @fact char(2),
        @as_find varchar(30)

set @fact = 'K1'
set @as_find = 'LG'

-- ???
SELECT '???' = CASE WHEN substring(pcod_fact,2,1) ='1'  THEN pcod_name ELSE pcod_nam3+'('+pcod_name+')' END,
       '????' = pcod_pcod
  FROM bupcod
 WHERE pcod_fact = @fact and
       ( (pcod_name like '%'+@as_find+'%') or (pcod_nam3 like '%'+@as_find+'%') )