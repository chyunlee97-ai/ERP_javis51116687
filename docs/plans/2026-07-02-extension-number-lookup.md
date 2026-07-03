# 내선번호 조회 기능 추가 Implementation Plan

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** `6_내선번호 조회.sql` 파일의 검색 로직을 ERP 챗봇의 조건 선택 및 자연어 검색 기능에 추가하여 사용자가 공장별 임직원 내선번호를 조회할 수 있도록 합니다.

**Architecture:** 
1. **클라이언트 UI**: 조건 선택 탭의 콤보박스에 "📞 6. 내선번호 조회"를 추가하고, 데이터 조회 결과를 테이블에 동적으로 렌더링합니다.
2. **서버 의도 분류**: `intents.json`에 `phone_search` 의도를 신규 정의하고, `intent_matcher.py`에 "내선번호", "내선", "전화번호", "연락처" 등의 카테고리 매칭 키워드를 통합하여 자연어 검색을 지원합니다.
3. **데이터베이스 서비스**: `db_service.py`에 실제 동적 SQL 실행 구문을 탑재하고, 개발 환경을 위해 `baobot` 테이블의 실제 구조에 맞춘 Mock 데이터를 제공합니다.

**Tech Stack:** Python, PySide6, FastAPI, pyodbc (MS SQL Server)

---

### Task 1: intents.json 및 intent_matcher.py 의도 등록

**Files:**
- Modify: [server/intents/intents.json](file:///c:/project/ERP_javis/server/intents/intents.json)
- Modify: [server/services/intent_matcher.py](file:///c:/project/ERP_javis/server/services/intent_matcher.py)

**Step 1: Write intent configuration**
Add `phone_search` intent mapping to `intents.json`.

**Step 2: Add keyword parsing**
Add `"phone_search"` and its keywords to `search_order` in `intent_matcher.py`.

---

### Task 2: db_service.py Dynamic SQL 및 Mock 데이터 추가

**Files:**
- Modify: [server/services/db_service.py](file:///c:/project/ERP_javis/server/services/db_service.py)

**Step 1: Add Mock Data handler**
Add the `"baobot"` mock data mapping matching the Y6 factory and K1 factory schemas inside `get_mock_data`.

**Step 2: Update execute_query with nextset loop**
Update the pyodbc execute logic to skip empty/none metadata sets in order to correctly retrieve rows from dynamic SQL queries.

---

### Task 3: client/ui/main_window.py UI 수정

**Files:**
- Modify: [client/ui/main_window.py](file:///c:/project/ERP_javis/client/ui/main_window.py)

**Step 1: Add Dropdown option**
Add `"📞 6. 내선번호 조회"` option pointing to `phone_search` in the selective combo box list.

---

### Task 4: 검증 및 테스트 진행

**Files:**
- Create: [test_phone_matcher.py](file:///c:/project/ERP_javis/test_phone_matcher.py)

**Step 1: Run unit tests**
Write and run `test_phone_matcher.py` using `python -m pytest` or `python -X utf8 test_phone_matcher.py` to confirm the matcher and database service respond properly.
