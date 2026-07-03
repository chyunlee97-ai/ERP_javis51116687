import os
import json
import re
import difflib

INTENTS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "intents", "intents.json")

def load_intents():
    try:
        with open(INTENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading intents: {e}")
        return []

def load_factory_mappings() -> list[dict]:
    """
    [자연어로 공장 구분 기준].md 파일을 읽어 공장 코드와 이름(별칭) 매핑 목록을 반환합니다.
    """
    mappings = []
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    factory_file = os.path.join(project_root, "[자연어로 공장 구분 기준].md")
    
    if not os.path.exists(factory_file):
        return mappings
        
    try:
        with open(factory_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line.startswith("|") or "code_fact" in line or "---" in line:
                    continue
                parts = [p.strip() for p in line.split("|")[1:-1]]
                if len(parts) < 2:
                    continue
                code_fact = parts[0]
                names = [n for n in parts[1:] if n]
                if code_fact:
                    mappings.append({
                        "code_fact": code_fact.upper(),
                        "names": names
                    })
    except Exception as e:
        print(f"Error loading factory mappings: {e}")
        
    return mappings

def clean_postpositions_and_stop_words(message: str) -> str:
    """
    검색 메시지에서 조사(접미사) 및 불용어를 제거합니다.
    """
    words = message.split()
    clean_words = []
    
    stop_words = {"조회", "검색", "찾기", "해줘", "알려줘", "부탁해", "조회해줘", "검색해줘", "공장"}
    postpositions = {"에서", "으로", "로", "과", "와", "하고", "랑", "은", "는", "이", "가", "을", "를", "의", "에", "대한"}
    
    for word in words:
        if word in stop_words or word in postpositions:
            continue
        
        w_clean = word
        changed = True
        while changed:
            changed = False
            for post in postpositions:
                if len(w_clean) > len(post) and w_clean.endswith(post):
                    w_clean = w_clean[:-len(post)]
                    changed = True
                    break
        
        if w_clean and w_clean not in stop_words and w_clean not in postpositions:
            clean_words.append(w_clean)
            
    return " ".join(clean_words).strip()

def extract_factory_code(message: str, default_fact: str = "K1") -> tuple[str, str]:
    """
    사용자 입력 메시지에서 공장 명칭을 찾아 code_fact로 변환하고
    해당 명칭과 불용어를 메시지에서 제거하여 반환합니다.
    """
    clean_msg = message.strip()
    fact = default_fact.upper()
    
    # 1단계: K1, C1 등 공장 코드가 직접 적혀있는지 정규식 매칭 (기존 로직 유지)
    fact_codes = ["K1", "K2", "Y1", "Y2", "C1", "C2", "G1", "G2", "C8", "C9", "G4", "G5", "G9", "K3", "K4", "K5", "Y4", "Y5", "Y6", "Y7"]
    codes_pattern = "|".join(fact_codes + [c.lower() for c in fact_codes])
    fact_match = re.search(rf'\b({codes_pattern})\b', clean_msg)
    if fact_match:
        fact = fact_match.group(1).upper()
        clean_msg = clean_msg.replace(fact_match.group(0), "").strip()
        clean_msg = clean_postpositions_and_stop_words(clean_msg)
        return fact, clean_msg

    # 공장 구분 매핑 파일 로드
    mappings = load_factory_mappings()
    if not mappings:
        clean_msg = clean_postpositions_and_stop_words(clean_msg)
        return fact, clean_msg
        
    # 모든 별칭들을 수집하여 정렬 (길이 기준 내림차순)
    name_to_code = []
    for m in mappings:
        code = m["code_fact"]
        for name in m["names"]:
            name_to_code.append((name, code))
            name_no_space = name.replace(" ", "")
            if name_no_space != name:
                name_to_code.append((name_no_space, code))
                
    name_to_code = sorted(list(set(name_to_code)), key=lambda x: len(x[0]), reverse=True)
    
    # 메시지를 먼저 정제하여 조사 등을 제거
    cleaned_msg_for_match = clean_postpositions_and_stop_words(clean_msg)
    
    # 2단계: 공백/특수문자 제거 상태에서 substring 매칭 시도
    def normalize(text: str) -> str:
        return re.sub(r'[\s\-/\\]', '', text).lower()
        
    msg_norm = normalize(cleaned_msg_for_match)
    matched_code = None
    matched_name_norm = None
    
    for name, code in name_to_code:
        name_norm = normalize(name)
        if not name_norm:
            continue
        
        if name_norm in msg_norm:
            # 경계(boundary) 검사: 단어의 일부(접두사 등)로 오매칭되는지 확인
            # 원래 정제된 메시지에서 해당 단어가 독립된 토큰(또는 기호 경계)으로 존재하는지 검사
            pattern = r"[\s\-/\\]*".join([re.escape(c) for c in name_norm])
            m_obj = re.search(pattern, cleaned_msg_for_match, re.IGNORECASE)
            if m_obj:
                start, end = m_obj.start(), m_obj.end()
                boundary_ok = True
                if start > 0:
                    char_before = cleaned_msg_for_match[start - 1]
                    if char_before.isalnum():
                        boundary_ok = False
                if end < len(cleaned_msg_for_match):
                    char_after = cleaned_msg_for_match[end]
                    if char_after.isalnum():
                        boundary_ok = False
                        
                if boundary_ok:
                    matched_code = code
                    matched_name_norm = name_norm
                    break
            
    if matched_code and matched_name_norm:
        fact = matched_code
        pattern = r"[\s\-/\\]*".join([re.escape(c) for c in matched_name_norm])
        m_obj = re.search(pattern, clean_msg, re.IGNORECASE)
        if m_obj:
            clean_msg = clean_msg.replace(m_obj.group(0), "").strip()
        clean_msg = clean_postpositions_and_stop_words(clean_msg)
        return fact, clean_msg
        
    # 3단계: 유사값 매칭 (Fuzzy Matching)
    words = clean_msg.split()
    best_ratio = 0.0
    best_code = None
    best_word_in_msg = None
    
    postpositions = {"에서", "으로", "로", "과", "와", "하고", "랑", "은", "는", "이", "가", "을", "를", "의", "에", "대한"}
    
    for word in words:
        # 조사 제거
        w_clean = word
        changed = True
        while changed:
            changed = False
            for post in postpositions:
                if len(w_clean) > len(post) and w_clean.endswith(post):
                    w_clean = w_clean[:-len(post)]
                    changed = True
                    break
                    
        if len(w_clean) < 2:
            continue
            
        w_norm = normalize(w_clean)
        for name, code in name_to_code:
            name_norm = normalize(name)
            if not name_norm:
                continue
                
            ratio = difflib.SequenceMatcher(None, w_norm, name_norm).ratio()
            
            # 단어 길이에 따른 동적 임계값 적용
            threshold = 0.8
            if len(name_norm) == 3:
                threshold = 0.65
            elif len(name_norm) >= 4:
                threshold = 0.66
                
            if ratio >= threshold and ratio > best_ratio:
                best_ratio = ratio
                best_code = code
                best_word_in_msg = word
                
    if best_code and best_word_in_msg:
        fact = best_code
        clean_msg = clean_msg.replace(best_word_in_msg, "").strip()
        
    clean_msg = clean_postpositions_and_stop_words(clean_msg)
    return fact, clean_msg

def match_intent(message: str, default_fact: str = "K1") -> tuple[dict | None, list]:
    intents = load_intents()
    message = message.strip()
    
    # 1. Advanced Category-based Substring matching (Option 2)
    # Search order designed to prevent substring overlap issues (e.g. "제품코드" matched before "제품")
    search_order = [
        ("phone_search", ["내선번호", "전화번호", "연락처", "내선"]),
        ("prod_code_search", ["제품코드"]),
        ("part_tcod_search", ["특성코드", "특성"]),
        ("part_detail_search", ["부품번호", "부품"]),
        ("model_search", ["영업모델", "모델", "제품"]),
        ("vend_search", ["거래처", "바이어", "고객사"])
    ]
    
    matched_intent = None
    matched_keyword = None
    
    for intent, keywords in search_order:
        for kw in keywords:
            if kw in message:
                matched_intent = intent
                matched_keyword = kw
                break
        if matched_intent:
            break
            
    if matched_intent:
        # Extract the search keyword (as_find) by clearing the category indicator
        clean_msg = message.replace(matched_keyword, "")
        
        # Extract factory code and clean the query
        fact, clean_msg = extract_factory_code(clean_msg, default_fact)
        as_find = clean_msg
        
        # Clean up potential brackets/quotes/icons
        as_find = re.sub(r'^[\'\"\[\(🔍\s]+|[\'\"\]\)\s]+$', '', as_find).strip()
        
        # Return matched intent and built parameters [fact, as_find]
        for item in intents:
            if item.get("intent") == matched_intent:
                params_config = item.get("params", [])
                mapped_params = []
                for p_cfg in params_config:
                    p_name = p_cfg.get("name")
                    if p_name == "fact":
                        mapped_params.append(fact)
                    elif p_name == "as_find":
                        mapped_params.append(as_find)
                    else:
                        mapped_params.append(p_cfg.get("default", ""))
                return item, mapped_params

    # 2. Backwards-compatible Fallback: Regex template matching
    for item in intents:
        for example in item.get("examples", []):
            placeholders = re.findall(r'\{([^}]+)\}', example)
            
            if placeholders:
                pattern = re.escape(example)
                for ph in placeholders:
                    pattern = pattern.replace(f'\\{{{ph}\\}}', f'(?P<{ph}>.*)')
                
                regex_str = f"^{pattern}$"
                match = re.match(regex_str, message, re.IGNORECASE)
                
                if match:
                    captured = {k: (v.strip() if v else "") for k, v in match.groupdict().items()}
                    params_config = item.get("params", [])
                    mapped_params = []
                    
                    for param_cfg in params_config:
                        name = param_cfg.get("name")
                        val = captured.get(name)
                        if val:
                            wrap_template = param_cfg.get("wrap", "{value}")
                            formatted_val = wrap_template.replace("{value}", val)
                            mapped_params.append(formatted_val)
                        else:
                            mapped_params.append(param_cfg.get("default", ""))
                    return item, mapped_params
            else:
                pattern = re.escape(example)
                pattern = pattern.replace(r'\*', r'(.*)')
                regex_str = f"^{pattern}$"
                match = re.match(regex_str, message, re.IGNORECASE)
                
                if match:
                    captured_values = [g.strip() for g in match.groups() if g]
                    params_config = item.get("params", [])
                    mapped_params = []
                    
                    for i, param_cfg in enumerate(params_config):
                        if param_cfg.get("from_input") and i < len(captured_values):
                            val = captured_values[i]
                            wrap_template = param_cfg.get("wrap", "{value}")
                            formatted_val = wrap_template.replace("{value}", val)
                            mapped_params.append(formatted_val)
                        else:
                            mapped_params.append(param_cfg.get("default", ""))
                    
                    return item, mapped_params
                
    return None, []
