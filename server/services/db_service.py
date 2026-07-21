import pyodbc
import config

# Connection string helper
def get_connection_string():
    return (
        f"DRIVER={{{config.DB_DRIVER}}};"
        f"SERVER={config.DB_SERVER};"
        f"DATABASE={config.DB_NAME};"
        f"UID={config.DB_USER};"
        f"PWD={config.DB_PASSWORD};"
        "Connection Timeout=5;"
    )

def get_mock_data(query: str, params: list) -> list[dict]:
    """
    Returns mock data in developer environments where MS SQL is not available.
    """
    print(f"[Mock DB] Executing query: {query} with params: {params}")
    
    # 0. 사용자 조회 (bauser)
    if "bauser" in query.lower():
        fact_val = params[0] if len(params) > 0 else "Y6"
        idno_val = params[1] if len(params) > 1 else ""
        pasw_val = params[2] if len(params) > 2 else ""
        
        # Valid user combos: (fact, idno, pasw)
        valid_users = [
            ("Y6", "Y6", "q"),
            ("Y1", "Y1", "q"),
            ("Y5", "Y5", "q"),
            ("K1", "K1", "q"),
            ("K1", "000005", "12345"),
            ("K1", "000006", "12345")
        ]
        
        is_valid = False
        for f, i, p in valid_users:
            if fact_val == f and idno_val == i and pasw_val == p:
                is_valid = True
                break
        
        # General backup rule: if ID equals Fact and Password is 'q'
        if idno_val == fact_val and pasw_val == "q":
            is_valid = True
            
        cnt = 1 if is_valid else 0
        return [{"cnt": cnt}]

    # Extract fact and search term (as_find) from params
    fact = params[0] if len(params) > 0 else "K1"
    as_find = params[1] if len(params) > 1 else ""
    
    # Normalize search term
    as_find_val = as_find.replace("%", "").strip()
    
    # 1. 거래처 조회 (acvend)
    if "acvend" in query.lower():
        mock_clients = [
            {"vend_fact": "K1", "vend_keyx": "V0001", "vend_name": "에이스전자", "vend_nam3": "ACE"},
            {"vend_fact": "K1", "vend_keyx": "V0002", "vend_name": "LG디스플레이", "vend_nam3": "LG"},
            {"vend_fact": "K1", "vend_keyx": "V0003", "vend_name": "삼성에스디아이", "vend_nam3": "SAMSUNG"},
            {"vend_fact": "K1", "vend_keyx": "V0008", "vend_name": None, "vend_nam3": "NULL_TEST"}, # NULL 이름 테스트용
            {"vend_fact": "Y1", "vend_keyx": "V0004", "vend_name": "베트남테크", "vend_nam3": "VIETNAM"},
            {"vend_fact": "Y1", "vend_keyx": "V0005", "vend_name": "현대모비스", "vend_nam3": "HYUNDAI"},
            {"vend_fact": "C1", "vend_keyx": "V0006", "vend_name": "LG이노텍", "vend_nam3": "LG"},
            {"vend_fact": "G1", "vend_keyx": "V0007", "vend_name": "LG화학", "vend_nam3": "LG"},
            {"vend_fact": "Y6", "vend_keyx": "V0009", "vend_name": "베트남법인", "vend_nam3": "VN_FACT"}, # Y6 테스트 (vend_nam3 존재)
            {"vend_fact": "Y6", "vend_keyx": "V0010", "vend_name": "하노이테크", "vend_nam3": ""},      # Y6 테스트 (vend_nam3 없음)
        ]
        
        # Filter by fact
        filtered = [c for c in mock_clients if c["vend_fact"] == fact]
        
        # Filter by search term
        if as_find_val:
            filtered = [
                c for c in filtered 
                if (as_find_val.lower() in (c["vend_name"] or "").lower() or 
                    as_find_val.lower() in (c["vend_nam3"] or "").lower() or 
                    as_find_val.lower() in (c["vend_keyx"] or "").lower())
            ]
            
        # Map to final output columns: 거래처번호, 거래처명
        results = []
        for c in filtered:
            is_fact_2_1 = len(c["vend_fact"]) >= 2 and c["vend_fact"][1] == '1'
            # 변경전: vend_name_display = c["vend_name"] if is_fact_2_1 else f"{c['vend_nam3']}({c['vend_name']})"
            if is_fact_2_1:
                vend_name_display = c["vend_name"] if c["vend_name"] is not None else ""
            else:
                is_nam3_empty = c["vend_nam3"] is None or c["vend_nam3"].strip() == ""
                if is_nam3_empty:
                    vend_name_display = c["vend_name"] if c["vend_name"] is not None else ""
                else:
                    vend_name_display = "Insert Vend Name!"
            results.append({
                "거래처명": vend_name_display,
                "거래처번호": c["vend_keyx"]
            })
        return results
        
    # 2. 모델정보 조회 (bumodl)
    elif "bumodl" in query.lower():
        mock_models = [
            {"modl_fact": "K1", "modl_modl": "M-ACE-01", "modl_key2": "ACE-PAD", "modl_name": "에이스 태블릿 패드", "modl_spec": "10인치, Black", "modl_pcod": "P001", "pcod_name": "태블릿"},
            {"modl_fact": "K1", "modl_modl": "M-LG-99", "modl_key2": "LG-MONITOR", "modl_name": "LG 4K 모니터", "modl_spec": "32인치, IPS", "modl_pcod": "P002", "pcod_name": "모니터"},
            {"modl_fact": "Y1", "modl_modl": "M-SAM-11", "modl_key2": "355-TV", "modl_name": "삼성 355 QLED TV", "modl_spec": "65인치, NeoQLED", "modl_pcod": "P003", "pcod_name": "TV"},
            {"modl_fact": "Y1", "modl_modl": "M-ACE-02", "modl_key2": "ACE-PHONE-4", "modl_name": "에이스 폰 4", "modl_spec": "128GB, Silver", "modl_pcod": "P004", "pcod_name": "스마트폰"},
            {"modl_fact": "C1", "modl_modl": "M-ACQ-01", "modl_key2": "ACQ-PRO", "modl_name": "차량용 ACQ 센서", "modl_spec": "12V, Waterproof", "modl_pcod": "P005", "pcod_name": "센서"},
            {"modl_fact": "G1", "modl_modl": "M-EBR-01", "modl_key2": "EBR-MODULE", "modl_name": "산업용 EBR 보드", "modl_spec": "24V, HighSpeed", "modl_pcod": "P006", "pcod_name": "제어기"},
        ]
        
        filtered = [m for m in mock_models if m["modl_fact"] == fact]
        if as_find_val:
            filtered = [
                m for m in filtered
                if as_find_val.lower() in m["modl_key2"].lower() or as_find_val.lower() in m["modl_modl"].lower()
            ]
            
        results = []
        is_y_fact = fact.startswith("Y")
        for m in filtered:
            if not is_y_fact:
                results.append({
                    "당사모델번호": m["modl_modl"],
                    "영업모델": m["modl_key2"],
                    "제품명": m["modl_name"],
                    "규격": m["modl_spec"],
                    "제품코드": m["modl_pcod"],
                    "제품코드명": m["pcod_name"]
                })
            else:
                # DNE는 영업모델=당사모델 동일하여 당사모델번호를 뺌
                results.append({
                    "영업모델": m["modl_key2"],
                    "제품명": m["modl_name"],
                    "규격": m["modl_spec"],
                    "제품코드": m["modl_pcod"],
                    "제품코드명": m["pcod_name"]
                })
        return results
        
    # 3. 제품코드 조회 (bupcod)
    elif "bupcod" in query.lower():
        mock_codes = [
            {"pcod_fact": "K1", "pcod_pcod": "P001", "pcod_name": "태블릿PC", "pcod_nam3": "TAB"},
            {"pcod_fact": "K1", "pcod_pcod": "P002", "pcod_name": "모니터디스플레이", "pcod_nam3": "MON"},
            {"pcod_fact": "Y1", "pcod_pcod": "C100", "pcod_name": "텔레비전", "pcod_nam3": "TV"},
            {"pcod_fact": "Y1", "pcod_pcod": "P004", "pcod_name": "스마트폰기기", "pcod_nam3": "PHN"},
            {"pcod_fact": "C1", "pcod_pcod": "WS-01", "pcod_name": "무선충전모듈", "pcod_nam3": "WS"},
            {"pcod_fact": "G1", "pcod_pcod": "A004", "pcod_name": "어댑터", "pcod_nam3": "ADP"},
        ]
        
        filtered = [c for c in mock_codes if c["pcod_fact"] == fact]
        if as_find_val:
            filtered = [
                c for c in filtered
                if as_find_val.lower() in c["pcod_name"].lower() or as_find_val.lower() in c["pcod_nam3"].lower()
            ]
            
        results = []
        for c in filtered:
            is_fact_2_1 = len(c["pcod_fact"]) >= 2 and c["pcod_fact"][1] == '1'
            pcod_name_display = c["pcod_name"] if is_fact_2_1 else f"{c['pcod_nam3']}({c['pcod_name']})"
            results.append({
                "제품명": pcod_name_display,
                "제품코드": c["pcod_pcod"]
            })
        return results
        
    # 4. 부품정보 상세 조회 (mppart_v)
    elif "mppart_v" in query.lower():
        mock_parts = [
            {"part_fact": "K1", "part_part": "PT-001", "part_name": "LCD 패널 4인치", "part_unix": "PCS", "part_spec": "4inch TFT", "part_tcod": "T01", "tcod_assy": "1"},
            {"part_fact": "K1", "part_part": "PT-002", "part_name": "메인보드 회로", "part_unix": "PCS", "part_spec": "Rev 1.0", "part_tcod": "T02", "tcod_assy": "0"},
            {"part_fact": "K1", "part_part": "PT-004", "part_name": "리튬 배터리 4000mAh", "part_unix": "PCS", "part_spec": "3.7V", "part_tcod": "T01", "tcod_assy": "1"},
            {"part_fact": "Y1", "part_part": "33-01", "part_name": "강화유리 커버 33", "part_unix": "PCS", "part_spec": "Gorilla Glass 5", "part_tcod": "T03", "tcod_assy": "1"},
            {"part_fact": "C1", "part_part": "MAZ-01", "part_name": "마그네슘 케이스 MAZ", "part_unix": "PCS", "part_spec": "Alloy Grade A", "part_tcod": "T04", "tcod_assy": "1"},
            {"part_fact": "G1", "part_part": "OFE-01", "part_name": "구리 코일 OFE", "part_unix": "PCS", "part_spec": "Pure 99.9%", "part_tcod": "T05", "tcod_assy": "1"},
        ]
        
        filtered = [p for p in mock_parts if p["part_fact"] == fact]
        if as_find_val:
            filtered = [
                p for p in filtered
                if as_find_val.lower() in p["part_part"].lower() or as_find_val.lower() in p["part_name"].lower()
            ]
            
        results = []
        for p in filtered:
            results.append({
                "부품번호": p["part_part"],
                "부품명": p["part_name"],
                "단위": p["part_unix"],
                "규격": p["part_spec"],
                "특성코드": p["part_tcod"],
                "구분": "원재료" if p["tcod_assy"] == '1' else "재공품"
            })
        return results
        
    # 5. 부품특성코드 조회 (mptcod)
    elif "mptcod" in query.lower():
        mock_tcodes = [
            {"tcod_fact": "K1", "tcod_tcod": "T01", "tcod_name": "배터리부품류"},
            {"tcod_fact": "K1", "tcod_tcod": "T02", "tcod_name": "회로기판보드"},
            {"tcod_fact": "Y1", "tcod_tcod": "D1", "tcod_name": "디스플레이글라스"},
            {"tcod_fact": "C1", "tcod_tcod": "CL", "tcod_name": "화학케이스코팅류"},
            {"tcod_fact": "G1", "tcod_tcod": "A01", "tcod_name": "전원도체도금류"},
        ]
        
        filtered = [t for t in mock_tcodes if t["tcod_fact"] == fact]
        if as_find_val:
            filtered = [
                t for t in filtered
                if as_find_val.lower() in t["tcod_name"].lower() or as_find_val.lower() in t["tcod_tcod"].lower()
            ]
            
        results = []
        for t in filtered:
            results.append({
                "특성명": t["tcod_name"],
                "특성코드": t["tcod_tcod"]
            })
        return results
        
    elif "baobot" in query.lower():
        mock_phones = [
            # Y6 공장 임직원 정보 (실제 DB 데이터 기준)
            {"obot_fact": "Y6", "부서": "법인장", "직급": "전무", "이름": "곽상기", "내선번호": "6735"},
            {"obot_fact": "Y6", "부서": "공용", "직급": "V3 회의실", "이름": "V3 회의실", "내선번호": "6739"},
            {"obot_fact": "Y6", "부서": "공용", "직급": "V1 회의실", "이름": "V1 회의실", "내선번호": "6477"},
            {"obot_fact": "Y6", "부서": "관리팀", "직급": "수석부장", "이름": "김윤태", "내선번호": "6740"},
            {"obot_fact": "Y6", "부서": "영업팀", "직급": "수석부장", "이름": "윤일영", "내선번호": "6711"},
            {"obot_fact": "Y6", "부서": "품질팀", "직급": "차장", "이름": "권기원", "내선번호": "6712"},
            {"obot_fact": "Y6", "부서": "생산팀", "직급": "금형실장", "이름": "김종수", "내선번호": "6713"},
            {"obot_fact": "Y6", "부서": "개발팀", "직급": "과장", "이름": "전용호", "내선번호": "6750"},
            {"obot_fact": "Y6", "부서": "생산팀", "직급": "부장", "이름": "김진만", "내선번호": "6714"},
            {"obot_fact": "Y6", "부서": "자재팀", "직급": "부장", "이름": "권현태", "내선번호": "6490"},
            {"obot_fact": "Y6", "부서": "생산팀", "직급": "생기실장", "이름": "이문희", "내선번호": "6758"},
            # K1 공장 기본 Mock 데이터
            {"obot_fact": "K1", "부서": "인사팀", "직급": "대리", "이름": "이민준", "내선번호": "1001"},
            {"obot_fact": "K1", "부서": "총무팀", "직급": "사원", "이름": "박서준", "내선번호": "1002"},
        ]
        
        filtered = [p for p in mock_phones if p["obot_fact"] == fact]
        if as_find_val:
            filtered = [
                p for p in filtered
                if (as_find_val.lower() in p["부서"].lower() or 
                    as_find_val.lower() in p["직급"].lower() or 
                    as_find_val.lower() in p["이름"].lower() or 
                    as_find_val.lower() in p["내선번호"].lower())
            ]
        
        results = []
        for p in filtered:
            results.append({
                "부서": p["부서"],
                "직급": p["직급"],
                "이름": p["이름"],
                "내선번호": p["내선번호"]
            })
        return results
        
    elif "obot_prog" in query.lower() or "obuspr" in query.lower():
        # Handle selective programs check query
        lang_val = "KR"
        for p in params:
            if isinstance(p, str) and p.strip() in ["KR", "EN", "CH", "VN", "SP"]:
                lang_val = p.strip()
                break
                
        names_map = {
            "KR": {
                "1": "거래처 조회",
                "2": "모델정보 조회",
                "3": "제품코드 조회",
                "4": "부품정보 조회",
                "5": "부품특성코드 조회",
                "6": "내선번호 조회"
            },
            "EN": {
                "1": "Vender Select",
                "2": "Model Information",
                "3": "Product Code",
                "4": "Part Number Select",
                "5": "Part Property",
                "6": "Extension Select"
            }
        }
        
        lang_dict = names_map.get(lang_val, names_map["KR"])
        results = []
        for code, name in lang_dict.items():
            results.append({
                "code_code": code,
                "조회시트": name
            })
        return results
        
    return []

def execute_query(query: str, params: list, limit: int = None, offset: int = 0) -> list[dict]:
    # If connection details are defaults or empty, default to Mock mode
    if config.DB_SERVER in ["127.0.0.1", ""] or config.DB_USER == "readonly_user":
        print("[DB Service] Default config detected. Running in Mock Data Mode.")
        results = get_mock_data(query, params)
        if offset > 0 or limit is not None:
            start = offset
            end = offset + limit if limit is not None else None
            return results[start:end]
        return results
        
    conn = None
    try:
        conn_str = get_connection_string()
        conn = pyodbc.connect(conn_str)
        
        # Enforce pyodbc connection encoding/decoding for Korean character set (CP949 / UTF-16)
        conn.setdecoding(pyodbc.SQL_CHAR, encoding='cp949')
        conn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-16')
        if hasattr(pyodbc, 'SQL_WMETADATA'):
            conn.setdecoding(pyodbc.SQL_WMETADATA, encoding='utf-16')
        
        cursor = conn.cursor()
        
        # Execute query using parameters binding (safely protected from SQL injection)
        cursor.execute(query, params)
        
        # dynamic SQL로 인한 선행 빈 결과 집합을 건너뜀 (nextset 루프)
        while cursor.description is None:
            if not cursor.nextset():
                break
                
        if cursor.description:
            # Get column names
            columns = [column[0] for column in cursor.description]
            
            # Format results as a list of dicts
            results = []
            row_count = 0
            while True:
                row = cursor.fetchone()
                if not row:
                    break
                row_count += 1
                if offset > 0 and row_count <= offset:
                    continue
                results.append(dict(zip(columns, row)))
                if limit is not None and len(results) >= limit:
                    break
                
            return results
        return []
        
    except Exception as e:
        print(f"[DB Service] Error executing real SQL query: {e}. Falling back to Mock Data Mode.")
        results = get_mock_data(query, params)
        if offset > 0 or limit is not None:
            start = offset
            end = offset + limit if limit is not None else None
            return results[start:end]
        return results
        
    finally:
        if conn:
            conn.close()
