import sys
import os

# Ensure backend directory is in path
sys.path.append(os.path.abspath("server"))

from services.intent_matcher import match_intent

test_cases = [
    # 1. 거래처 조회 + 공장 조합
    ("창원공장 LG 거래처 조회", "vend_search", "C1", "LG"),
    ("오성사 LG 거래처", "vend_search", "C1", "LG"),
    ("창온공장 LG 거래처", "vend_search", "C1", "LG"),
    ("바이어 LG 조회해줘", "vend_search", "K1", "LG"),  # 공장 누락 시 기본값 K1
    ("C8 LG 거래처", "vend_search", "C8", "LG"),
    ("인도공장에서 LG 거래처 조회", "vend_search", "C8", "LG"),
    
    # 2. 모델정보 조회 + 공장 조합
    ("베트남 M/T A43 모델 조회", "model_search", "K4", "A43"),
    ("베트남MT A43 영업모델", "model_search", "K4", "A43"),
    ("하공모터 A43 제품 검색", "model_search", "K4", "A43"),
    
    # 3. 제품코드 조회 + 공장 조합
    ("구미공장 SE 제품코드", "prod_code_search", "G1", "SE"),
    ("추저우공잔 SE 제품코드 조회", "prod_code_search", "C9", "SE"),
]

print("="*80)
print(" 자연어 검색 + 공장 구분 통합 매칭 테스트")
print("="*80)

passed = 0
for msg, expected_intent, expected_fact, expected_keyword in test_cases:
    intent_item, params = match_intent(msg)
    if intent_item:
        intent = intent_item["intent"]
        fact, keyword = params[0], params[1]
        
        is_correct = (intent == expected_intent) and (fact == expected_fact) and (keyword == expected_keyword)
        status = "✅ PASS" if is_correct else "❌ FAIL"
        
        print(f"[{msg}] -> {status}")
        print(f"   Expected: Intent={expected_intent}, Fact={expected_fact}, Keyword={expected_keyword}")
        print(f"   Actual  : Intent={intent}, Fact={fact}, Keyword={keyword}")
        if is_correct:
            passed += 1
    else:
        print(f"[{msg}] -> ❌ FAIL (No Match)")
        print(f"   Expected: Intent={expected_intent}, Fact={expected_fact}, Keyword={expected_keyword}")

print("="*80)
print(f" 결과: {passed}/{len(test_cases)} 케이스 통과")
print("="*80)
sys.exit(0 if passed == len(test_cases) else 1)
