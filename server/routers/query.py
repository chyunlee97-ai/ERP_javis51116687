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
                elif p_name == "setl":
                    params.append(fact_val)
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

class ProgramsRequest(BaseModel):
    fact: str | None = None
    lang: str = "KR"
    idno: str = "Y6"

class ProgramItem(BaseModel):
    code_code: str
    name: str
    intent: str

@router.post("/selective-programs", response_model=list[ProgramItem])
def get_selective_programs(request: ProgramsRequest):
    import re
    fact_val = request.fact if request.fact else "Y6"
    lang_val = request.lang if request.lang else "KR"
    idno_val = request.idno if request.idno else "Y6"
    
    query_template = """
    DECLARE @fact CHAR(2),
            @idno CHAR(10),
            @lang CHAR(2);

    SET @fact = ?;
    SET @lang = ?;
    SET @idno = ?;

    SELECT 'code_code' = code_code,
           '조회시트' = CASE WHEN @lang = 'KR' THEN (case when isnull(code_name,'') <> '' then code_name else  code_code+'.'+code_engl end )
                         WHEN @lang = 'EN' THEN (case when isnull(code_engl,'') <> '' then code_engl else  code_code+'.'+code_engl end ) 
                         WHEN @lang = 'CH' THEN (case when isnull(code_chna,'') <> '' then code_chna else  code_code+'.'+code_engl end ) 
                         WHEN @lang = 'VN' THEN (case when isnull(code_vina,'') <> '' then code_vina else  code_code+'.'+code_engl end ) 
                         WHEN @lang = 'SP' THEN (case when isnull(code_span,'') <> '' then code_span else  code_code+'.'+code_engl end ) ELSE code_code+'.'+code_engl END,
           'code_engl' = isnull(code_engl, '')
      FROM bacode
     WHERE code_gubn ='OBOT_PROG' and
           code_fact = @fact and
           exists ( SELECT *
                      FROM obuspr
                     WHERE uspr_fact = code_fact and uspr_meid = code_code and
                           uspr_idno = @idno )
    """
    
    try:
        db_results = db_service.execute_query(
            query_template,
            [fact_val, lang_val, idno_val]
        )
        
        code_to_intent = {
            "1": "vend_search",
            "2": "model_search",
            "3": "prod_code_search",
            "4": "part_detail_search",
            "5": "part_tcod_search",
            "6": "phone_search"
        }
        
        formatted_programs = []
        for row in db_results:
            code = str(row.get("code_code", "")).strip()
            name = str(row.get("조회시트", "")).strip()
            engl = str(row.get("code_engl", "")).strip()
            
            intent = code_to_intent.get(code)
            if not intent:
                if engl:
                    cleaned = re.sub(r'[^a-zA-Z0-9\s_]', '', engl)
                    words = cleaned.lower().split()
                    if words:
                        name_str = "_".join(words)
                        if not name_str.endswith("_search") and not name_str.endswith("_select"):
                            name_str = name_str + "_search"
                        name_str = name_str.replace("vender", "vend").replace("product", "prod").replace("part_number", "part_detail")
                        intent = name_str
                if not intent:
                    intent = f"program_{code}_search"
                    
            formatted_programs.append(ProgramItem(
                code_code=code,
                name=name,
                intent=intent
            ))
            
        return formatted_programs
    except Exception as e:
        print(f"Error executing programs query: {e}")
        fallback_programs = [
            ProgramItem(code_code="1", name="거래처 조회" if lang_val == "KR" else "Vender Select", intent="vend_search"),
            ProgramItem(code_code="2", name="모델정보 조회" if lang_val == "KR" else "Model Information", intent="model_search"),
            ProgramItem(code_code="3", name="제품코드 조회" if lang_val == "KR" else "Product Code", intent="prod_code_search"),
            ProgramItem(code_code="4", name="부품정보 조회" if lang_val == "KR" else "Part Number Select", intent="part_detail_search"),
            ProgramItem(code_code="5", name="부품특성코드 조회" if lang_val == "KR" else "Part Property", intent="part_tcod_search"),
            ProgramItem(code_code="6", name="내선번호 조회" if lang_val == "KR" else "Extension Select", intent="phone_search")
        ]
        return fallback_programs


class LoginRequest(BaseModel):
    fact: str = "Y6"
    idno: str
    pasw: str

class LoginResponse(BaseModel):
    success: bool
    message: str

@router.post("/login", response_model=LoginResponse)
def handle_login(request: LoginRequest):
    query_template = """
    DECLARE @fact CHAR(2),
            @idno VARCHAR(20),
            @pasw VARCHAR(20),
            @count INT;

    SET @fact = ?;
    SET @idno = ?;
    SET @pasw = ?;

    SELECT @count = COUNT(*)
      FROM bauser
     WHERE user_fact = @fact and
           user_idno = @idno and
           user_pasw = @pasw;

    SET @count = ISNULL(@count, 0);

    SELECT 'cnt' = @count;
    """
    try:
        db_results = db_service.execute_query(
            query_template,
            [request.fact, request.idno, request.pasw]
        )
        if db_results and int(db_results[0].get("cnt", 0)) > 0:
            return LoginResponse(success=True, message="Connect OK!")
        else:
            return LoginResponse(success=False, message="Invaild ID & Psw")
    except Exception as e:
        print(f"Error handling login request: {e}")
        return LoginResponse(success=False, message="Invaild ID & Psw")

