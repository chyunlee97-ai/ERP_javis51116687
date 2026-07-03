"""
캐릭터 위젯용 배경 제거 스크립트
- 대상: 어두운(검정/회색) 단색 배경 이미지
- 출력: 알파 채널 PNG (PySide6 투명 위젯에 바로 사용 가능)

사용법:
  pip install opencv-python pillow
  python remove_background.py                         # 기본값 실행
  python remove_background.py input.jpg output.png    # 파일 직접 지정
"""

import sys
import numpy as np
import cv2
from PIL import Image


def remove_dark_background(
    input_path: str,
    output_path: str,
    bg_saturation_max: int = 40,   # 배경 채도 상한 (낮을수록 무채색에 가까움)
    bg_value_max: int = 60,        # 배경 명도 상한 (낮을수록 어두운 배경만 제거)
    grabcut_iter: int = 10,        # GrabCut 반복 횟수 (높을수록 정교, 느림)
    edge_blur: int = 7,            # 경계 페더링 강도 (홀수, 클수록 부드러움)
) -> None:
    """
    어두운 단색 배경을 제거하고 알파 채널 PNG로 저장한다.

    Parameters
    ----------
    input_path      : 원본 이미지 경로 (JPEG/PNG 모두 가능)
    output_path     : 저장할 PNG 경로
    bg_saturation_max : HSV 채도 기준 — 이 값 이하이면 배경 후보
    bg_value_max    : HSV 명도 기준 — 이 값 이하이면 배경 후보
    grabcut_iter    : GrabCut 알고리즘 반복 횟수
    edge_blur       : 경계 가우시안 블러 커널 크기 (홀수)
    """
    img = Image.open(input_path).convert("RGB")
    arr = np.array(img)
    h, w = arr.shape[:2]

    # ── 1. HSV 공간에서 어두운 배경 픽셀 마스킹 ──────────────────────────
    hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)
    bg_mask = (hsv[:, :, 1] < bg_saturation_max) & (hsv[:, :, 2] < bg_value_max)

    # ── 2. GrabCut — 중앙 원형 영역을 전경 힌트로 사용 ───────────────────
    gc_mask = np.zeros(arr.shape[:2], np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)

    margin = min(h, w) // 6
    rect = (margin, margin, w - margin * 2, h - margin * 2)
    cv2.grabCut(arr, gc_mask, rect, bgd_model, fgd_model,
                grabcut_iter, cv2.GC_INIT_WITH_RECT)
    gc_fg = np.where((gc_mask == 2) | (gc_mask == 0), False, True)

    # ── 3. 두 마스크 결합 ────────────────────────────────────────────────
    final_mask = (gc_fg & ~bg_mask).astype(np.uint8) * 255

    # ── 4. Morphology — 작은 노이즈 제거 + 구멍 메우기 ──────────────────
    k_close = np.ones((5, 5), np.uint8)
    k_open = np.ones((3, 3), np.uint8)
    final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_CLOSE, k_close)
    final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_OPEN, k_open)

    # ── 5. 경계 페더링 (자연스러운 엣지) ────────────────────────────────
    if edge_blur > 1:
        final_mask = cv2.GaussianBlur(final_mask, (edge_blur, edge_blur), 2)

    # ── 6. RGBA 합성 및 저장 ─────────────────────────────────────────────
    rgba = np.dstack([arr, final_mask])
    result = Image.fromarray(rgba, "RGBA")
    result.save(output_path, "PNG")

    # ── 결과 요약 출력 ───────────────────────────────────────────────────
    alpha = final_mask
    transparent_pct = np.sum(alpha == 0) / alpha.size * 100
    opaque_pct = np.sum(alpha == 255) / alpha.size * 100
    feather_pct = 100 - transparent_pct - opaque_pct

    print(f"[완료] {output_path} 저장됨")
    print(f"  크기        : {result.size[0]}×{result.size[1]} px")
    print(f"  투명(배경)  : {transparent_pct:.1f}%")
    print(f"  불투명(전경): {opaque_pct:.1f}%")
    print(f"  반투명(경계): {feather_pct:.1f}%")
    print()
    print("PySide6에서 사용하려면:")
    print("  self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)")
    print("  self.setAttribute(Qt.WA_TranslucentBackground)")
    print(f"  pixmap = QPixmap('{output_path}')")


# ── 파인튜닝 가이드 ──────────────────────────────────────────────────────────
# 배경이 너무 많이 남는다면:
#   bg_value_max 값을 높여보세요 (예: 60 → 80)
#   bg_saturation_max 값을 높여보세요 (예: 40 → 60)
#
# 전경(캐릭터)이 너무 잘려나간다면:
#   bg_value_max 값을 낮춰보세요 (예: 60 → 40)
#   grabcut_iter 를 높여보세요 (예: 10 → 15)
#
# 경계가 너무 딱딱하다면:
#   edge_blur 를 높여보세요 (예: 7 → 11, 반드시 홀수)
# ────────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    if len(sys.argv) == 3:
        inp, out = sys.argv[1], sys.argv[2]
    elif len(sys.argv) == 1:
        inp = "ERP_javis.jpeg"
        out = "ERP_javis_transparent2.png"
    else:
        print("사용법: python remove_background.py [입력파일] [출력파일]")
        sys.exit(1)

    remove_dark_background(inp, out)
