# SQL 실행 스크립트 관리자 표시 기능 개선 및 포트 설정 변경

## 개요
ERP 챗봇에서 [전송] 버튼 클릭 시, 조회 건수(0건 포함)에 관계없이 실제로 실행된 최종 SQL 스크립트를 하단의 [관리자 실행된 SQL 스크립트] 창에 항상 투명하게 표시하도록 기능을 개선하고, 로컬 개발 환경에서의 포트 충돌 문제를 해결하기 위해 API 서버 및 클라이언트 포트를 8002로 변경하여 검증을 완료했습니다.

## 주요 변경사항
- **SQL 치환 및 포맷터 개선** (`server/routers/query.py`):
  - SQL 템플릿의 변수 선언부(`DECLARE`, `SET` 블록)를 정규식으로 제거하고, `@변수명` 부분을 실제 매핑된 파라미터 값으로 치환하여 관리자가 바로 실행해볼 수 있는 형태의 가독성 높은 쿼리 스크립트를 생성하도록 구현했습니다.
- **포트 충돌 방지 및 포트 설정 변경** (`server/.env`, `client/.env`, `run.ps1`):
  - 8001번 포트가 시스템/WSL 등의 백그라운드 프로세스로 인해 해제되지 않는 문제를 우회하기 위해 전체 포트를 `8002`로 변경했습니다.
  - `run.ps1`에서 서버와 클라이언트를 재시작할 때 8001번과 8002번 포트를 모두 체크하여 종료하도록 스크립트를 보강했습니다.
- **클라이언트 UI 연동 보강** (`client/ui/main_window.py`):
  - 서버 응답에서 `intent` 매칭 여부를 판별하여, SQL이 없는 경우와 의도(Intent) 파악에 실패한 경우의 안내 메시지를 구분하여 관리자 패널에 표시하도록 로직을 정교화했습니다.

## 핵심 코드

### 1. SQL 가용성 보장을 위한 템플릿 파서
```python
# server/routers/query.py
def format_query_with_params(query: str, params: list) -> str:
    # 1단계: ? -> 실제 값으로 순서대로 치환
    # 2단계: DECLARE @변수 / SET @변수 선언부 줄 제거
    # 3단계: 최종적으로 @변수명을 실제 값(따옴표 포함)으로 치환
    ...
    return clean_query
```

### 2. 클라이언트 UI SQL 표시 및 예외 가이드
```python
# client/ui/main_window.py
query_script = response.get("query_script", "")
intent_found = response.get("intent", "None") != "None"
if hasattr(self, 'admin_panels'):
    self.admin_panels.set_sql_script(query_script, input_text=input_text, intent_found=intent_found)
```

## 결과
- ✅ FastAPI 서버 정상 구동 (Port: 8002)
- ✅ `test_gui_sql_display.py` 실행을 통한 PySide6 GUI 기능 검증 성공
- ✅ Y6 공장, 키워드 'Z' 입력 시 정확히 5건의 결과 데이터가 테이블에 출력됨을 확인
- ✅ [관리자 실행된 SQL 스크립트] 창에 치환 완료된 가독성 높은 실시간 SQL 스크립트 표출 확인

## 다음 단계
- 실제 DB 운영 환경 배포 시 방화벽 포트(8002) 오픈 확인
- 로그인 세션 연동 시 사용자의 소속 공장 코드(`fact`)가 클라이언트에 정상 주입되는지 연계 테스트
