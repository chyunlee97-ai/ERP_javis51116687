from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services import intent_matcher, db_service

router = APIRouter(prefix="", tags=["query"])

class QueryRequest(BaseModel):
    message: str = ""
    intent: str | None = None
    fact: str | None = None
    as_find: str | None = None
    limit: int = 50
    offset: int = 0

class QueryResponse(BaseModel):
    intent: str
    result: list[dict]
    count: int
    message: str
    query_script: str | None = None

def format_query_with_params(query: str, params: list) -> str:
    """
    SQL 템플릿의 ? 를 실제 파라미터로 치환하고,
    DECLARE/SET 변수 선언 블록을 제거한 뒤 @변수명을 값으로 직접 치환하여
    관리자가 보기 쉬운 최종 실행 SQL을 반환한다.
    """
    # 1단계: ? → 실제 값으로 순서대로 치환 (SET @fact = ?; 형태에서 값 추출)
    param_map = {}  # { '@변수명': '실제값' }
    formatted = query
    for param in params:
        if param is None:
            param_str = "NULL"
        elif isinstance(param, str):
            escaped = param.replace("'", "''")
            param_str = f"'{escaped}'"
        else:
            param_str = str(param)
        formatted = formatted.replace("?", param_str, 1)

    # 2단계: SET @변수명 = '값'; 행에서 변수명과 값을 매핑으로 추출
    import re
    set_pattern = re.compile(
        r"SET\s+(@\w+)\s*=\s*('(?:[^']|'')*'|NULL|-?\d+(?:\.\d+)?)\s*;?",
        re.IGNORECASE
    )
    for m in set_pattern.finditer(formatted):
        var_name = m.group(1).lower()
        var_value = m.group(2)
        param_map[var_name] = var_value

    # 3단계: DECLARE 행, SET 행 제거 (변수 선언/설정 블록 삭제)
    lines = formatted.splitlines()
    clean_lines = []
    for line in lines:
        stripped = line.strip().upper()
        # DECLARE @... 또는 SET @... 로 시작하는 행 제거
        if re.match(r'DECLARE\s+@', stripped) or re.match(r'SET\s+@', stripped):
            continue
        clean_lines.append(line)

    result = "\n".join(clean_lines)

    # 4단계: 남은 쿼리 본문의 @변수명을 실제 값으로 치환
    for var_name, var_value in param_map.items():
        # 대소문자 무관하게 @변수명 치환
        result = re.sub(re.escape(var_name), var_value, result, flags=re.IGNORECASE)

    # 5단계: 앞뒤 빈 줄 정리
    result = result.strip()

    return result


@router.post("/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    intent_item = None
    params = []
    
    # 1. If explicit intent is passed (Selective Mode)
    if request.intent:
        intents = intent_matcher.load_intents()
        # Find matching intent template
        for item in intents:
            if item.get("intent") == request.intent:
                intent_item = item
                break
                
        if intent_item:
            # Map parameters
            fact_val = request.fact if request.fact else "K1"
            as_find_val = request.as_find if request.as_find else ""
            
            # Reconstruct params list based on intent parameter configuration order
            params_config = intent_item.get("params", [])
            for p_cfg in params_config:
                p_name = p_cfg.get("name")
                if p_name == "fact":
                    params.append(fact_val)
                elif p_name == "as_find":
                    params.append(as_find_val)
                else:
                    params.append(p_cfg.get("default", ""))
    
    # 2. Otherwise fallback to Natural Language query (General Mode)
    if not intent_item and request.message:
        default_fact = request.fact if request.fact else "K1"
        intent_item, params = intent_matcher.match_intent(request.message, default_fact=default_fact)
        
    if not intent_item:
        return QueryResponse(
            intent="None",
            result=[],
            count=0,
            message="죄송해요, 어떤 정보인지 파악하지 못했어요. 일반 모드일 때는 'K1 공장 에이스 거래처' 또는 '에이스 거래처' 형식으로 입력하시거나, 선택 모드를 이용해 보세요!",
            query_script=None
        )
        
    # 3. Database Execution
    query_template = intent_item.get("query", "")
    intent_name = intent_item.get("intent", "알수없음")
    
    query_script_str = format_query_with_params(query_template, params)
    
    try:
        db_results = db_service.execute_query(
            query_template, 
            params,
            limit=request.limit,
            offset=request.offset
        )
        
        # Display appropriate user message
        if not db_results:
            if request.offset == 0:
                msg = "테스트용: 조건에 부합하는 데이터를 찾지 못했습니다."
            else:
                msg = "추가 데이터가 없습니다."
        else:
            if request.offset == 0:
                msg = f"'{intent_name}' 조회 결과 {len(db_results)}건을 찾았습니다."
            else:
                msg = f"추가로 {len(db_results)}건을 불러왔습니다."
            
        return QueryResponse(
            intent=intent_name,
            result=db_results,
            count=len(db_results),
            message=msg,
            query_script=query_script_str
        )
    except Exception as e:
        print(f"Error handling query request: {e}")
        return QueryResponse(
            intent=intent_name,
            result=[],
            count=0,
            message=f"데이터를 조회하는 중 오류가 발생했습니다: {str(e)}",
            query_script=query_script_str
        )
