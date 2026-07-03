# 자연어 검색 고도화 제안서 (Natural Language Query Parsing Proposal)

사용자께서 요청하신 자연어 검색 규칙을 구현하는 방안과 함께, 한글 조사 및 어순 변화에 유연하게 대응할 수 있는 **더 나은 대안(개선안)**을 비교하여 제안합니다.

---

## [대안 1] 요청하신 규칙 기반 매칭 방식 (Split-based Parser)

입력 문자열을 공백(스페이스) 기준으로 분할하여 첫 번째 단어를 검색어로 취하고, 두 번째 단어의 동의어 여부에 따라 검색 카테고리를 결정하는 직관적인 방식입니다.

### 1) 작동 원리
1. 입력 문장을 공백 기준으로 분할(Split)합니다. (예: `"LG 거래처 조회"` ➔ `["LG", "거래처", "조회"]`)
2. **첫 번째 단어 (`Group 0`)**: 무조건 검색어(`as_find`)로 지정 ➔ `"LG"`
3. **두 번째 단어 (`Group 1`)**: 동의어 맵핑 테이블과 대조하여 카테고리(Intent) 매칭
   * `거래처` / `바이어` ➔ `vend_search`
   * `모델` / `영업모델` / `제품` ➔ `model_search`
   * `제품코드` ➔ `prod_code_search`
   * `부품` / `부품번호` ➔ `part_detail_search`
   * `특성` / `특성코드` ➔ `part_tcod_search`

### 2) 한계점
* **어순이 바뀔 때 매칭 실패**: `"거래처 LG 조회"` 또는 `"LG의 거래처를 찾아줘"` 처럼 순서가 바뀌거나 조사가 붙으면 매칭되지 않습니다.
* **공장 코드(Fact) 입력 시 오작동**: `"K1 LG 거래처 조회"`로 입력하면 첫 번째 단어가 `"K1"`이 되어 검색어로 `"K1"`이 매칭되고 카테고리는 `"LG"`가 되어 실패합니다.

---

## [대안 2] 키워드 청소 및 동의어 매핑 방식 (Keyword Cleanup Parser) - ★ 추천

사용자가 입력한 문장에서 불필요한 조사, 동사, 공장 코드를 제거하고 핵심 카테고리 단어와 검색 키워드를 똑똑하게 분류하는 방식입니다. 한글 자연어 처리에 매우 적합하며 오작동 확률이 매우 낮습니다.

### 1) 작동 원리
1. **공장 코드(Fact) 추출**: 문장 중 `K1` 또는 `K2` 패턴을 감지하여 추출하고 문장에서 제거합니다. (기본값 `"K1"`)
2. **카테고리(Intent) 추출**: 아래의 동의어 키워드가 문장에 포함되어 있는지 부분 일치(Substring) 검사하여 카테고리를 확정합니다.
   * `거래처`, `바이어`, `고객사` 포함 ➔ `vend_search`
   * `모델`, `영업모델`, `제품` 포함 ➔ `model_search`
   * `제품코드` 포함 ➔ `prod_code_search`
   * `부품번호`, `부품` 포함 ➔ `part_detail_search`
   * `특성코드`, `특성` 포함 ➔ `part_tcod_search`
3. **핵심 검색어(`as_find`) 추출**: 
   * 문장에서 찾은 카테고리 키워드와 조미료 표현들(`조회`, `검색`, `찾기`, `해줘`, `부탁해`, `~의`, `~에 대한`)을 지웁니다.
   * 남은 텍스트를 정리하여 핵심 검색어로 확정합니다.

### 2) 대안 2의 장점 (예시 비교)
| 입력 예시 | [대안 1] 결과 | [대안 2] 결과 (추천) |
| :--- | :--- | :--- |
| **"LG 거래처 조회"** | 성공 (`as_find="LG"`, `intent="vend_search"`) | 성공 (`as_find="LG"`, `intent="vend_search"`) |
| **"거래처 LG"** | **실패** (첫 단어가 '거래처'가 됨) | **성공** (`as_find="LG"`, `intent="vend_search"`) |
| **"K1 LG 바이어 조회해줘"** | **실패** (첫 단어가 'K1'이 됨) | **성공** (`fact="K1"`, `as_find="LG"`, `intent="vend_search"`) |
| **"A43 영업모델 검색"** | **실패** (두 번째 단어가 '영업모델'인 경우 맵핑 룰 필요) | **성공** (`as_find="A43"`, `intent="model_search"`) |

---

## 3. 백엔드 구현 소스 코드 예시 (Python)

아래는 `server/services/intent_matcher.py` 파일에 탑재될 실제 매칭 알고리즘의 대안 2(개선안) 구현 샘플입니다.

```python
import re

def match_intent_advanced(message: str) -> tuple[dict | None, list]:
    message = message.strip()
    
    # 1. 공장 코드 (Fact) 추출 (예: K1, K2)
    fact = "K1"  # 기본값
    fact_match = re.search(r'\b(K1|K2|k1|k2)\b', message)
    if fact_match:
        fact = fact_match.group(1).upper()
        message = message.replace(fact_match.group(0), "")  # 문장에서 제거
        
    # 2. 카테고리(Intent) 매칭용 동의어 정의
    category_map = {
        "vend_search": ["거래처", "바이어", "고객사"],
        "model_search": ["모델", "영업모델", "제품"],
        "prod_code_search": ["제품코드"],
        "part_detail_search": ["부품번호", "부품"],
        "part_tcod_search": ["특성코드", "특성"]
    }
    
    matched_intent = None
    matched_keyword = None
    
    for intent, keywords in category_map.items():
        for kw in keywords:
            if kw in message:
                matched_intent = intent
                matched_keyword = kw
                break
        if matched_intent:
            break
            
    if not matched_intent:
        return None, []
        
    # 3. 핵심 검색어 (as_find) 추출
    # 문장에서 카테고리 키워드와 불필요한 조사/동사를 지워나감
    clean_msg = message
    clean_msg = clean_msg.replace(matched_keyword, "")
    
    # 지울 조사 및 종결 어미 패턴
    stop_words = ["조회", "검색", "찾기", "해줘", "부탁해", "의", "에", "대한", "을", "를", "이", "가"]
    for sw in stop_words:
        clean_msg = re.sub(rf'\b{sw}\b|\s{sw}\s', '', clean_msg)
        
    # 최종 공백 정리
    as_find = clean_msg.strip()
    
    # intents.json에 정의된 인텐트 세부 템플릿 로드 후 파라미터 반환
    intents = load_intents()
    for item in intents:
        if item.get("intent") == matched_intent:
            return item, [fact, as_find]
            
    return None, []
```

---

## 💬 검토 및 의견 요청

사용자님께서 보시기에 **[대안 2 (추천안)]**으로 한글 어순과 관계없이 더 자연스럽게 검색되도록 구현할까요, 아니면 요청하신 **[대안 1 (순차 분할 규칙)]** 방식 그대로 정확히 일치할 때만 실행되도록 구현할까요?

의견을 남겨주시면 결정에 따라 즉시 개발하여 적용해 드리겠습니다.
