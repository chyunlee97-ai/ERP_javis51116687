import sys
import os

# Ensure backend directory is in path
sys.path.append(os.path.abspath("server"))

from services.intent_matcher import match_intent

test_cases = [
    # 1. 거래처 조회 (vend_search)
    ("LG 거래처 조회", "vend_search", "LG"),
    ("거래처 LG", "vend_search", "LG"),
    ("바이어 LG 조회해줘", "vend_search", "LG"),
    
    # 2. 모델정보 조회 (model_search)
    ("A43 모델 조회", "model_search", "A43"),
    ("A43 영업모델 조회", "model_search", "A43"),
    ("제품 A43 검색", "model_search", "A43"),
    
    # 3. 제품코드 조회 (prod_code_search)
    ("SE 제품코드 조회", "prod_code_search", "SE"),
    ("제품코드 SE", "prod_code_search", "SE"),
    
    # 4. 부품정보 조회 (part_detail_search)
    ("A1 부품 조회", "part_detail_search", "A1"),
    ("A1 부품번호 조회", "part_detail_search", "A1"),
    
    # 5. 부품특성코드 조회 (part_tcod_search)
    ("C 특성 조회", "part_tcod_search", "C"),
    ("C 특성코드 조회", "part_tcod_search", "C")
]

print("="*60)
print(" 자연어 검색 매칭 알고리즘 검증 테스트")
print("="*60)

passed = 0
for msg, expected_intent, expected_keyword in test_cases:
    intent_item, params = match_intent(msg)
    if intent_item:
        intent = intent_item["intent"]
        fact, keyword = params[0], params[1]
        
        is_correct = (intent == expected_intent) and (keyword == expected_keyword)
        status = "✅ PASS" if is_correct else "❌ FAIL"
        
        print(f"[{msg}] -> {status}")
        print(f"   Expected: Intent={expected_intent}, Keyword={expected_keyword}")
        print(f"   Actual  : Intent={intent}, Keyword={keyword}, Fact={fact}")
        if is_correct:
            passed += 1
    else:
        print(f"[{msg}] -> ❌ FAIL (No Match)")
        print(f"   Expected: Intent={expected_intent}, Keyword={expected_keyword}")

print("="*60)
print(f" 결과: {passed}/{len(test_cases)} 케이스 통과")
print("="*60)
sys.exit(0 if passed == len(test_cases) else 1)
