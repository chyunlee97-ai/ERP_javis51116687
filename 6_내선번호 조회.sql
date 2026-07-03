declare @fact char(2),
        @as_find varchar(30)

set @fact = 'Y6'
--set @as_find = '김'
set @as_find = '%'+ @as_find+ '%'


-- 1. 동적 쿼리를 담을 변수들을 선언합니다.
DECLARE @ColumnList NVARCHAR(MAX);
DECLARE @SQL NVARCHAR(MAX);

-- 2. [FOR XML PATH] 방식을 사용하여 하위 버전에서도 문자열을 가로로 결합합니다.
SET @ColumnList = STUFF((
    SELECT ', obot_' + code_code + ' AS [' + code_name + ']'
    FROM bacode WITH (NOLOCK)
    WHERE code_fact = @fact 
      AND code_gubn = 'OBOT_1'
    ORDER BY code_code
    FOR XML PATH(''), TYPE).value('.', 'NVARCHAR(MAX)'), 1, 2, '');

-- 🔍 [참고] STUFF 함수가 맨 앞의 ', ' (쉼표와 공백 2글자)를 제거하여 깔끔한 컬럼 리스트를 만듭니다.

-- 3. 완성된 컬럼 리스트를 메인 SQL 문장에 결합합니다.
SET @SQL = N'
SELECT ' + @ColumnList + N'
FROM baobot WITH (NOLOCK)
     INNER JOIN bacode WITH (NOLOCK) 
        ON ( obot_fact = code_fact 
             AND obot_gubn = code_code 
             AND code_gubn =''OBOT_GUBN'' )
WHERE obot_fact = @fact 
  and( (obot_tex1 like @as_find ) or (obot_tex2 like @as_find ) or (obot_tex3 like @as_find) or (obot_tex4 like @as_find) )
  AND obot_gubn = ''1''';

-- 4. 최종 동적 쿼리 실행
EXEC sp_executesql @SQL, 
                   N'@fact CHAR(2), @as_find VARCHAR(30)', 
                   @fact = @fact, 
                   @as_find = @as_find;