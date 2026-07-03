# 챗봇 아바타 이미지 변경 및 크기 적용

## 개요
기존 챗봇 아바타 이미지(`mark_512.png`)를 사용자가 요청한 SVG 이미지(`ohsung_mark_256.svg`)로 변경하였습니다. 해당 SVG 이미지는 192x192 픽셀 해상도로 정상적으로 로드되며, UI 내에서 133x133 픽셀로 알맞게 축소되어 정상적으로 표시됩니다.

## 주요 변경사항
- **수정한 것**: `client/ui/main_window.py`에서 챗봇 이미지 소스 경로를 `image/ohsung_mark_256.svg`로 변경

## 핵심 코드
```python
# client/ui/main_window.py
        # Load character images
        img_path = os.path.join(PROJECT_ROOT, "image", "ohsung_mark_256.svg")
        self.pixmaps = {
            "idle": QPixmap(img_path),
            "thinking": QPixmap(img_path),
            "talking": QPixmap(img_path),
        }
```

## 결과
- ✅ PySide6 SVG 파일 정상 로드 확인 및 이미지 렌더링 검증 완료
- ✅ 기존 실행 중인 백그라운드 프로세스 종료 및 재구동을 통해 변경사항 반영 확인

## 다음 단계
- 챗봇 아바타 이미지의 고대비 및 다크 모드 일관성 확인
