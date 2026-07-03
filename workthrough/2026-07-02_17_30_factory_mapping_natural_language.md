# 자연어 검색 공장 구분 자동 매핑 구현

## 개요
자연어로 검색을 진행할 때, 입력한 문장 내에 포함된 공장 명칭(예: "창원공장", "오성사", "하이퐁모터" 등)을 `[자연어로 공장 구분 기준].md` 파일의 정의와 매핑하여 해당 공장 코드(`code_fact`)를 자동으로 분석 및 추출합니다. 또한 오타가 포함된 유사명칭("창온공장", "하공모터" 등)이 들어와도 `difflib.SequenceMatcher`를 이용해 유사 매칭하도록 하였습니다.

## 주요 변경사항
- **개발한 것**: `server/services/intent_matcher.py` 내에 `load_factory_mappings()`, `clean_postpositions_and_stop_words()`, `extract_factory_code()` 함수 추가.
- **개선한 것**: 자연어 검색 시 매핑된 공장명을 검색 키워드(`as_find`)에서 제외(정제)하여 검색 결과의 정확도 향상.
- **수정한 것**: 공장명이 지정되지 않은 경우, 라우터에서 전달된 기본값(`default_fact`, 현재 `'K1'`)으로 기본 자동 적용되도록 구현.
- **검증한 것**: `test_factory_matcher.py` 단위 테스트 및 `test_factory_intent_integration.py` 통합 매칭 테스트(11/11 케이스 패스)를 작성하여 정상 작동을 보증함.

## 핵심 코드
```python
# server/services/intent_matcher.py
def extract_factory_code(message: str, default_fact: str = "K1") -> tuple[str, str]:
    # 1. 공장 코드 직접 매칭 (K1, C1 등)
    # 2. 공백 제거 후 substring 매칭 및 토큰 경계 검증 (정밀 매치)
    # 3. difflib.SequenceMatcher를 활용한 단어 단위 유사값 매칭 (Fuzzy Match)
    # 4. 매치된 공장 명칭 및 불용어/조사를 정제한 최종 검색 메시지 반환
```

## 결과
- ✅ 단위 테스트 `test_factory_matcher.py` 11/11 케이스 통과
- ✅ 통합 테스트 `test_factory_intent_integration.py` 11/11 케이스 통과
- ✅ 기존 12건의 오리지널 자연어 검색 매칭 테스트(`test_matcher.py`) 역행(Regression) 없음 확인

## 다음 단계
- 추후 사용자 로그인 기능 추가 시 세션 또는 토큰 정보로부터 공장구분 코드를 기본값으로 자동 추출하도록 연동할 예정입니다.
