# CLAUDE.md (Project-Specific Rules)

Project-specific guidelines and constraints for the **사내 캐릭터 챗봇 (ERP Javis)** project.
General guidelines (Think Before Coding, Simplicity, Surgical Changes, etc.) are applied globally via `~/.claude/CLAUDE.md` and should not be duplicated here.

## 1. Project-Specific Security Rules (보안 규칙)

**절대적인 보안 원칙을 준수하며 개발합니다.**

- **DB 정보 유출 금지**: 클라이언트 코드에 DB 서버 주소, 계정, 비밀번호 **절대 포함 금지** (DB 관련 설정은 반드시 환경 변수를 사용하여 `server/config.py`에서만 로드).
- **SQL 파라미터 바인딩 필수**: pyodbc 연결 시 반드시 **파라미터 바인딩**(`?` 플레이스홀더)을 사용하고, SQL 인젝션 취약점을 유발하는 f-string 또는 문자열 포맷팅 결합 SQL문 작성을 절대 금지.
- **임의 SQL 실행 금지**: API 서버는 오직 `intents.json`에 미리 정의된 쿼리 템플릿만 매칭하여 실행하며, 클라이언트로부터 임의의 Raw SQL을 전송받아 실행하는 기능 금지.
- **데이터 조회량 제한**: 성능 및 부하 분산을 위해 데이터베이스 조회 결과는 항상 **TOP 50 이하**로 행(Row) 제한을 둡니다.
- **민감 파일 노출 차단**: `.env` 파일 등 주요 접속 정보가 포함된 파일은 반드시 `.gitignore`에 추가되어 형상 관리에 올라가지 않도록 보장.

## 2. Project-Specific Execution Notes (에이전트 실행 시 주의사항)

- **캐릭터 이미지 누락 처리**: 클라이언트 GUI 개발 중 캐릭터 이미지(`client/assets/*.png`)가 준비되지 않았을 경우, 임시로 투명도(알파 채널)가 적용된 단색 원형 도형을 그린 임시 PNG 파일을 생성하여 대체 사용합니다.
- **Mock 데이터 모드 구현**: 사내 MS SQL DB에 연결할 수 없는 개발/로컬 테스트 환경에서도 온전한 클라이언트 UI 개발이 가능하도록, `server/services/db_service.py`에 Mock 데이터를 반환하는 테스트 모드를 구현합니다.
- **사내 DB 구조 변경 매핑**: `intents.json`에 예시로 선언된 테이블 및 뷰 이름(`V_거래처`, `V_모델`)은 사내 DB 구조의 플레이스홀더이며, 실제 연동 시 현장 스키마에 맞춰 재매핑이 필요함을 README.md에 명시합니다.

## 3. Communication & Planning Language (언어 및 작성 정책)

- **한국어 작성 강제**: 에이전트가 작성하는 모든 계획서(Implementation Plan), 태스크(Task tracker), Walkthrough 등 사용자에게 제공되는 **모든 문서는 반드시 한국어**로 작성해야 합니다. (예: "Search Pagination Implementation Plan" 대신 "검색 페이지네이션 구현 계획서" 등)

## 4. Port Uniqueness & Registry Policy (포트 고유성 관리 정책)

- **서버 포트 중복 방지**: 로컬 개발 환경에서 다수의 프로젝트가 동시에 실행될 때 포트 충돌을 피하기 위해, 사내 프로젝트 전체의 포트 할당 현황을 [ports.md](file:///c:/project/ports.md) 파일에 관리하고 있습니다.
- **포트 확인 및 대장 등록**: 새 프로젝트 생성 혹은 포트 변경 작업 시 반드시 [ports.md](file:///c:/project/ports.md)를 확인하여 다른 프로젝트와 중복되지 않는 포트를 할당하고 대장을 갱신해야 합니다.
- **현재 프로젝트의 할당 포트**: **`8002`** (FastAPI 백엔드 서버 및 클라이언트 API 연동 포트로 최종 확정 및 적용됨).

