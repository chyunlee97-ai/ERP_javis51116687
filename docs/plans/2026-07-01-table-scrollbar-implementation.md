# 테이블 컬럼 너비 조정 및 가로 스크롤바 적용 구현 계획서

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** ERP 챗봇 결과 테이블에서 컬럼 헤더와 데이터 텍스트가 잘리지 않도록 길이에 맞게 컬럼 크기를 자동 조절하고, 테이블 너비를 초과할 경우 가로 스크롤바를 제공하여 조회 결과를 완벽하게 볼 수 있도록 개선합니다.

**Architecture:** PySide6 QTableWidget의 QHeaderView를 활용하여 `NO.` 컬럼은 40px 고정하고, 나머지 데이터 컬럼들은 `ResizeToContents` 모드를 적용하여 동적으로 너비를 자동 조절합니다. 가로 스크롤바 정책을 명시적으로 활성화합니다.

**Tech Stack:** Python 3, PySide6 (QTableWidget, QHeaderView, Qt)

---

## User Review Required

> [!IMPORTANT]
> 이번 변경사항은 클라이언트 UI (`main_window.py`) 파일만 수정합니다. 데이터 컬럼들의 최소 크기를 60px로 설정하여 너무 좁게 축소되는 것을 방지합니다.

## Open Questions

> [!NOTE]
> 사전에 확인 결과 `NO.` 컬럼은 40px 고정 너비로 유지하고 나머지 컬럼만 자동 정렬을 사용하는 것으로 결정되었습니다. 추가 미확정 요구사항은 없습니다.

## Proposed Changes

### Client UI Component

#### [MODIFY] [main_window.py](file:///c:/project/ERP_javis/client/ui/main_window.py)

- 테이블 레이아웃 초기화 영역(`init_ui`)에서 컬럼 사이즈 모드를 `ResizeToContents`로 변경하고, 가로 스크롤바 표시 조건 및 최소 컬럼 크기를 지정합니다.
- 데이터 로드 후 컬럼 속성을 설정하는 영역(`update_table_view`)에서 데이터 컬럼들의 크기 모드를 `QHeaderView.Stretch`에서 `QHeaderView.ResizeToContents`로 변경합니다.

---

### Task 1: QTableWidget 초기화 스타일 및 속성 변경
**Files:**
- Modify: `client/ui/main_window.py:548-553`

**Step 1: QTableWidget 레이아웃 속성 변경**
```python
        # 기존: self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 변경:
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_widget.horizontalHeader().setMinimumSectionSize(60)
```

**Step 2: 수동 검증**
이 단계에서는 수동 검증 단계에서 UI 정상 구동 여부를 확인합니다.

---

### Task 2: 데이터 갱신 시 테이블 컬럼 리사이즈 모드 수정
**Files:**
- Modify: `client/ui/main_window.py:753-755`

**Step 1: 데이터 로드 시 컬럼 리사이즈 모드 변경**
```python
            # 기존:
            # for c in range(1, len(columns) + 1):
            #     self.table_widget.horizontalHeader().setSectionResizeMode(c, QHeaderView.Stretch)
            # 변경:
            for c in range(1, len(columns) + 1):
                self.table_widget.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeToContents)
```

**Step 2: 수동 검증**
챗봇 서버 및 클라이언트를 구동하여 조회 결과를 실행해 봅니다.

---

## Verification Plan

### Manual Verification
1. `run.ps1`을 실행하여 챗봇 API 서버와 PySide6 클라이언트를 구동합니다.
2. 일반 모드 혹은 조건 선택 모드에서 모델 정보 조회 등 다양한 데이터 조회를 수행합니다.
3. 결과 테이블의 데이터 컬럼들이 데이터 길이 and 헤더 명칭의 크기에 맞춰 가변적으로 늘어나는지 확인합니다.
4. 가로 크기가 메인 테이블 영역을 초과할 때 가로 스크롤바가 정상 생성되며, 마우스 및 트랙패드로 스크롤하여 모든 내용을 확인할 수 있는지 검증합니다.
5. `NO.` 컬럼의 고정 너비(40px)가 계속 유지되는지 확인합니다.
