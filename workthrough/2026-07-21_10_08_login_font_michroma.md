# 로그인 페이지 OHSUNG ERP 텍스트 및 Michroma 폰트 적용

## 개요
로그인 페이지의 메인 로고 텍스트를 기존 "OHSUNG"과 "ERP SYSTEM"에서 통합된 **"OHSUNG ERP"**로 변경하였으며, Google Fonts의 **Michroma** 폰트를 동적으로 로드 및 **BOLD** 처리하여 UI 디자인을 미래지향적이고 일관성 있는 세련된 스타일로 완성했습니다.

## 주요 변경사항
- **개발한 것**: `client/fonts/Michroma-Regular.ttf` 폰트 에셋 다운로드 및 저장
- **수정한 것**: `client/ui/login_window.py`에서 `QFontDatabase`를 이용한 Michroma 폰트 동적 로드 구현, 타이틀바(`OHSUNGERP` -> `OHSUNG ERP`) 및 중앙 로고 텍스트(`OHSUNG` + `ERP SYSTEM` -> `OHSUNG ERP`) 수정 및 스타일시트에 `font-family: 'Michroma'` 및 `font-weight: bold` 적용
- **개선한 것**: `version.txt` 버전을 `ver.20260721.001`로 업데이트

## 핵심 코드
```python
# client/ui/login_window.py
        # Load Michroma font dynamically
        font_path = os.path.join(PROJECT_ROOT, "client", "fonts", "Michroma-Regular.ttf")
        if os.path.exists(font_path):
            QFontDatabase.addApplicationFont(font_path)

# 스타일 적용부 예시
        lbl_sys_title = QLabel("OHSUNG ERP")
        lbl_sys_title.setStyleSheet("color: white; font-size: 18px; font-weight: bold; font-family: 'Michroma', 'Malgun Gothic', '맑은 고딕', 'Segoe UI', Arial, sans-serif; letter-spacing: 1px;")
```

## 결과
- ✅ 로그인 화면 캡처 이미지를 통해 Michroma 폰트 및 BOLD 스타일, 텍스트가 "OHSUNG ERP"로 정상 변경됨을 수동 확인 완료
- ✅ 버전 업데이트 스크립트 실행 완료 (`ver.20260721.001`)

## 다음 단계
- 메인 대화창 등 다른 화면 요소의 영문 타이틀이나 로고에도 Michroma 폰트를 부분 적용할 지 디자인 검토
