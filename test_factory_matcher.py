import os
import re
import difflib

def load_factory_mappings() -> list[dict]:
    mappings = []
    project_root = r"c:\project\ERP_javis"
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
    words = message.split()
    clean_words = []
    
    stop_words = {"조회", "검색", "찾기", "해줘", "알려줘", "부탁해", "조회해줘", "검색해줘"}
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
        
        # normalized 상태에서 존재 유무 확인
        if name_norm in msg_norm:
            # 경계(boundary) 검사: 단어의 일부(접두사 등)로 오매칭되는지 확인
            # 원래 정제된 메시지에서 해당 단어가 독립된 토큰(또는 기호 경계)으로 존재하는지 검사
            pattern = r"[\s\-/\\]*".join([re.escape(c) for c in name_norm])
            m_obj = re.search(pattern, cleaned_msg_for_match, re.IGNORECASE)
            if m_obj:
                start, end = m_obj.start(), m_obj.end()
                # 앞 글자가 알파벳/숫자/한글이면 경계가 아님
                boundary_ok = True
                if start > 0:
                    char_before = cleaned_msg_for_match[start - 1]
                    if char_before.isalnum():
                        boundary_ok = False
                # 뒷 글자가 알파벳/숫자/한글이면 경계가 아님
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

# Test Suite
test_cases = [
    ("창원공장 에이스 거래처", "C1", "에이스 거래처"),
    ("오성사 에이스 거래처", "C1", "에이스 거래처"),
    ("창온공장 에이스 거래처", "C1", "에이스 거래처"),
    ("에이스 거래처", "K1", "에이스 거래처"),
    ("C8 에이스 거래처", "C8", "에이스 거래처"),
    ("인도공장에서 에이스 거래처", "C8", "에이스 거래처"),
    ("베트남 M/T 에이스 거래처", "K4", "에이스 거래처"),
    ("베트남MT 에이스 거래처", "K4", "에이스 거래처"),
    ("베트남-MT 에이스 거래처", "K4", "에이스 거래처"),
    ("하공모터 에이스 거래처", "K4", "에이스 거래처"),
    ("추저우공잔 SE 제품코드 조회", "C9", "SE 제품코드 조회"),
]

print("=== Running Factory Matcher Tests ===")
passed = 0
for msg, expected_fact, expected_msg in test_cases:
    fact, clean = extract_factory_code(msg)
    clean = re.sub(r'\s+', ' ', clean).strip()
    expected_msg = clean_postpositions_and_stop_words(expected_msg)
    
    status = "PASS" if fact == expected_fact and clean == expected_msg else "FAIL"
    if status == "PASS":
        passed += 1
    print(f"[{status}] Input: '{msg}' => Fact: {fact} (Expected: {expected_fact}), Msg: '{clean}' (Expected: '{expected_msg}')")
    
print(f"Passed {passed}/{len(test_cases)} tests.")
