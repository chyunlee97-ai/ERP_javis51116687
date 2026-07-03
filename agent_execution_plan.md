# 사내 캐릭터 챗봇 — AI 에이전트 실행 계획서
> 대상: AI 코딩 에이전트 (Antigravity /goal)  
> 아키텍처: 방식 B (클라이언트 → 사내 API 서버 → MS SQL)  
> 언어: Python + PySide6 (클라이언트) / FastAPI (API 서버)  
> OS: Windows 10/11 전용

---

## 🎯 Goal (최종 목표)

사내 MS SQL DB의 데이터를 조회할 수 있는 **데스크톱 캐릭터 챗봇**을 만든다.  
- 바탕화면에 투명 배경 캐릭터 위젯이 항상 떠 있음  
- 캐릭터 클릭 → 말풍선 입력창 → 자연어 질의 → 사내 API 서버를 통해 DB 조회 → 말풍선 응답  
- 클라이언트는 DB 접속 정보를 전혀 알 수 없음 (보안 핵심)  
- 미리 정의된 질의 템플릿(JSON)만 실행, 자유 SQL 금지

---

## 📁 프로젝트 구조 (생성할 파일/폴더)

```
project-root/
├── server/                         # FastAPI API 서버
│   ├── main.py                     # FastAPI 앱 진입점
│   ├── routers/
│   │   └── query.py                # /query 엔드포인트
│   ├── services/
│   │   ├── intent_matcher.py       # 질의 템플릿 매칭 로직
│   │   └── db_service.py           # MS SQL 조회 (pyodbc, 읽기전용)
│   ├── intents/
│   │   └── intents.json            # 질의 템플릿 정의 파일
│   ├── config.py                   # DB 접속정보 (환경변수에서 읽음)
│   └── requirements.txt
│
├── client/                         # PySide6 데스크톱 앱
│   ├── main.py                     # 앱 진입점
│   ├── ui/
│   │   ├── character_window.py     # 투명 캐릭터 위젯
│   │   └── bubble_widget.py        # 말풍선 입력/응답 위젯
│   ├── services/
│   │   └── api_client.py           # API 서버 HTTP 호출
│   ├── assets/
│   │   ├── character_idle.png      # 대기 상태 캐릭터 이미지 (알파 채널 PNG)
│   │   ├── character_thinking.png  # 로딩 상태
│   │   └── character_talking.png   # 응답 상태
│   ├── config.py                   # API 서버 URL 등 클라이언트 설정
│   └── requirements.txt
│
├── .env.example                    # 환경변수 예시 (실제 값 미포함)
└── README.md
```

---

## 🔧 Step 1 — 서버: FastAPI 기본 구조 세팅

### 1-1. `server/requirements.txt`
```
fastapi
uvicorn[standard]
pyodbc
python-dotenv
pydantic
```

### 1-2. `server/config.py`
- `python-dotenv`로 `.env` 파일에서 읽음
- 포함할 변수: `DB_SERVER`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_DRIVER`
- **절대 하드코딩 금지**, 코드에 접속 문자열 직접 작성 금지

### 1-3. `server/main.py`
- FastAPI 앱 생성
- `/health` GET 엔드포인트 (서버 상태 확인용, 인증 불필요)
- `/query` POST 엔드포인트 라우터 등록
- CORS는 사내 클라이언트 IP만 허용 (개발 중엔 localhost 허용)

---

## 🔧 Step 2 — 서버: 질의 템플릿(Intent) 시스템

### 2-1. `server/intents/intents.json` 구조
```json
[
  {
    "intent": "거래처검색",
    "examples": ["* 거래처", "거래처 * 알려줘", "* 들어가는 거래처"],
    "query": "SELECT TOP 50 거래처번호, 거래처명 FROM V_거래처 WHERE 거래처명 LIKE @kw",
    "params": [{"name": "kw", "from_input": true, "wrap": "%{value}%"}]
  },
  {
    "intent": "거래처코드조회",
    "examples": ["거래처번호 * 누구야", "* 번호 거래처"],
    "query": "SELECT 거래처명, 담당자, 상태 FROM V_거래처 WHERE 거래처번호 = @code",
    "params": [{"name": "code", "from_input": true, "wrap": "{value}"}]
  },
  {
    "intent": "모델검색",
    "examples": ["* 모델 뭐 있어", "* 모델 알려줘"],
    "query": "SELECT TOP 50 모델번호, 모델명 FROM V_모델 WHERE 모델명 LIKE @kw",
    "params": [{"name": "kw", "from_input": true, "wrap": "%{value}%"}]
  }
]
```

### 2-2. `server/services/intent_matcher.py`
- `intents.json` 로드 함수
- 입력 문장에서 와일드카드(`*`) 패턴 기반으로 intent 매칭
- 매칭된 intent와 추출된 파라미터 반환
- 매칭 실패 시 `None` 반환 (알 수 없는 질문 처리)

### 2-3. `server/services/db_service.py`
- `pyodbc`로 MS SQL 연결 (읽기전용 계정)
- 함수 시그니처: `execute_query(query: str, params: dict) -> list[dict]`
- **파라미터 바인딩 필수** (`?` 플레이스홀더 사용), f-string SQL 금지
- 결과는 딕셔너리 리스트로 반환
- 연결 풀링 적용 (Connection Pool)

### 2-4. `server/routers/query.py`
- POST `/query` 엔드포인트
- Request Body: `{"message": "에이스 들어가는 거래처 알려줘"}`
- 처리 흐름:
  1. `intent_matcher`로 intent + 파라미터 추출
  2. 매칭 실패 → `{"result": [], "message": "죄송해요, 모르는 질문이에요."}`
  3. 매칭 성공 → `db_service.execute_query()` 실행
  4. 결과 반환: `{"intent": "거래처검색", "result": [...], "count": N}`

---

## 🔧 Step 3 — 클라이언트: API 통신 모듈

### 3-1. `client/requirements.txt`
```
PySide6
requests
python-dotenv
```

### 3-2. `client/config.py`
- `API_BASE_URL` 환경변수에서 읽음 (예: `http://사내서버IP:8000`)
- **DB 관련 정보 일절 포함 금지**

### 3-3. `client/services/api_client.py`
- 함수: `ask(message: str) -> dict`
- `requests.post(API_BASE_URL + "/query", json={"message": message})` 호출
- 타임아웃 5초 설정
- 오류 시 `{"result": [], "message": "서버에 연결할 수 없어요."}` 반환

---

## 🔧 Step 4 — 클라이언트: 캐릭터 위젯 UI

### 4-1. `client/ui/character_window.py` — 메인 캐릭터 윈도우
**반드시 구현해야 할 속성:**
```python
# 프레임리스 + 투명 배경
self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
self.setAttribute(Qt.WA_TranslucentBackground)
```

**기능 목록:**
- PNG 이미지(`character_idle.png`) 표시 (알파 채널 유지)
- 드래그로 창 이동 (`mousePressEvent`, `mouseMoveEvent` 구현)
- 더블클릭 → 말풍선 위젯 토글 (`mouseDoubleClickEvent`)
- 상태별 이미지 전환 메서드: `set_state(state: str)` — `"idle"` / `"thinking"` / `"talking"`
- 시스템 트레이 아이콘 연동 (트레이 우클릭 → 종료 메뉴)

### 4-2. `client/ui/bubble_widget.py` — 말풍선 입력/응답 위젯
**UI 구성:**
- 캐릭터 윈도우 옆에 붙어서 표시 (위치는 캐릭터 창 기준 오른쪽 or 왼쪽 자동 계산)
- 입력창 (`QLineEdit`) + 전송 버튼
- 응답 표시 영역 (`QLabel` 또는 `QTextEdit`, 읽기 전용)
- 응답이 표 형태면 `QTableWidget`으로 표시

**동작 흐름:**
1. 사용자 입력 → 엔터 or 버튼 클릭
2. 캐릭터 상태 → `"thinking"` 으로 변경
3. 별도 스레드(`QThread`)에서 `api_client.ask()` 호출 (UI 블로킹 방지)
4. 응답 수신 → 캐릭터 상태 → `"talking"` 으로 변경
5. 응답 내용 말풍선에 표시
6. 3초 후 캐릭터 상태 → `"idle"` 복귀

---

## 🔧 Step 5 — 클라이언트: 앱 진입점

### `client/main.py`
- `QApplication` 생성
- `CharacterWindow` 인스턴스화 및 표시
- 시스템 트레이 아이콘 등록
- 트레이 우클릭 메뉴: `보이기/숨기기`, `종료`
- `app.exec()` 실행

---

## 🔧 Step 6 — 환경변수 및 설정

### `.env.example` (서버용, 실제 값은 별도 `.env`에 보관)
```
DB_SERVER=사내DB서버IP
DB_NAME=사내DB명
DB_USER=읽기전용계정명
DB_PASSWORD=비밀번호
DB_DRIVER=ODBC Driver 17 for SQL Server
API_PORT=8000
```

### `client/.env.example`
```
API_BASE_URL=http://사내서버IP:8000
```

---

## 🔧 Step 7 — README.md 작성

다음 항목을 포함한 `README.md` 생성:

1. **서버 실행 방법**
   ```bash
   cd server
   pip install -r requirements.txt
   cp .env.example .env  # .env 편집 후
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. **클라이언트 실행 방법**
   ```bash
   cd client
   pip install -r requirements.txt
   cp .env.example .env  # API_BASE_URL 편집 후
   python main.py
   ```

3. **새 질의 유형 추가 방법** (비개발자용)
   - `server/intents/intents.json`에 항목 추가 후 서버 재시작

---

## ✅ 구현 완료 체크리스트

에이전트는 아래 항목이 모두 충족되도록 구현한다:

- [ ] 서버 `GET /health` 호출 시 `{"status": "ok"}` 반환
- [ ] 서버 `POST /query {"message": "에이스 들어가는 거래처"}` 시 intent 매칭 및 결과 반환
- [ ] SQL은 반드시 파라미터 바인딩 사용, f-string 또는 문자열 포맷 SQL 금지
- [ ] DB 접속 정보가 클라이언트 코드 어디에도 없음
- [ ] 클라이언트 실행 시 투명 배경 + 프레임리스 캐릭터 창 표시
- [ ] 캐릭터 더블클릭 시 말풍선 위젯 토글
- [ ] 말풍선에서 질의 입력 → API 호출 → 응답 표시
- [ ] API 호출 중 UI가 멈추지 않음 (QThread 사용)
- [ ] 시스템 트레이 아이콘 + 우클릭 종료 메뉴 동작

---

## ⚠️ 보안 규칙 (절대 위반 금지)

1. 클라이언트 코드에 DB 서버 주소, 계정, 비밀번호 **절대 포함 금지**
2. SQL은 **파라미터 바인딩**만 사용 (`?` 플레이스홀더)
3. API 서버는 `intents.json`에 정의된 쿼리만 실행, 임의 SQL 실행 금지
4. 결과는 항상 **TOP 50 이하**로 제한
5. `.env` 파일은 `.gitignore`에 추가

---

## 📌 에이전트 실행 시 주의사항

- 캐릭터 이미지(`assets/*.png`)는 **알파 채널(투명도)이 있는 PNG**를 가정한다.  
  실제 이미지가 없으면 임시로 단색 원형 도형을 그린 PNG를 생성해서 사용할 것.
- DB가 없는 개발 환경에서는 `db_service.py`에 **Mock 데이터 반환 모드**를 추가하여  
  서버 없이도 클라이언트 UI 개발/테스트가 가능하게 할 것.
- `intents.json`의 DB 테이블/뷰 이름(`V_거래처`, `V_모델`)은 **실제 사내 DB 구조에 맞게 수정** 필요.  
  현재 예시 값은 플레이스홀더임을 README에 명시할 것.
