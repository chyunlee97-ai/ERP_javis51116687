import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append('c:/project/ERP_javis/server')
from services.db_service import get_connection_string, get_mock_data
import pyodbc
import config

conn_str = get_connection_string()
print('Connecting...')
conn = pyodbc.connect(conn_str)
conn.setdecoding(pyodbc.SQL_CHAR, encoding='cp949')
conn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-16')
print('Connected')
cursor = conn.cursor()

query = """DECLARE @fact char(2);
DECLARE @as_find varchar(30);
SET @fact = ?;
SET @as_find = ?;

SELECT '거래처번호' = vend_keyx,
       '거래처명' = CASE WHEN substring(vend_fact,2,1) ='1'  THEN vend_name ELSE vend_nam3+'('+vend_name+')' END
  FROM acvend
 WHERE vend_fact = @fact and
       ( (vend_name like '%'+@as_find+'%') or (vend_nam3 like '%'+@as_find+'%') or (vend_keyx like '%'+@as_find+'%') )"""

print('Executing query...')
try:
    cursor.execute(query, ['K1', 'LG'])
    print('Fetching...')
    columns = [column[0] for column in cursor.description]
    for row in cursor.fetchall():
        print(dict(zip(columns, row)))
except Exception as e:
    print(f"Error: {e}")
