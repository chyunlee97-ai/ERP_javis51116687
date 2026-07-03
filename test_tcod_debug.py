import sys
sys.path.insert(0, 'server')

from services import intent_matcher

# 1. intents.json 로딩 확인
intents = intent_matcher.load_intents()
print(f"로드된 intent 수: {len(intents)}")
print()

# 2. part_tcod_search intent 찾기
found = None
for item in intents:
    intent_name = item.get("intent")
    print(f"  - {intent_name}")
    if intent_name == "part_tcod_search":
        found = item

print()
if found:
    print("=== part_tcod_search 발견 ===")
    print(f"params: {found.get('params')}")
    
    # 3. 파라미터 매핑 시뮬레이션
    fact_val = "Y6"
    as_find_val = "Z"
    params = []
    params_config = found.get("params", [])
    for p_cfg in params_config:
        p_name = p_cfg.get("name")
        if p_name == "fact":
            params.append(fact_val)
        elif p_name == "as_find":
            params.append(as_find_val)
        else:
            params.append(p_cfg.get("default", ""))
    
    print(f"매핑된 params: {params}")
    print()
    
    # 4. format_query_with_params 실행
    from routers.query import format_query_with_params
    query_template = found.get("query", "")
    result = format_query_with_params(query_template, params)
    print("=== 최종 SQL 스크립트 ===")
    print(result)
    
    print("\n=== DB 실행 결과 ===")
    from services import db_service
    try:
        db_results = db_service.execute_query(query_template, params)
        print(f"조회 성공! 건수: {len(db_results)}")
        for i, row in enumerate(db_results):
            print(f"Row {i+1}: {row}")
    except Exception as e:
        print(f"실행 오류: {e}")
else:
    print("!!! part_tcod_search를 찾지 못했습니다 !!!")
