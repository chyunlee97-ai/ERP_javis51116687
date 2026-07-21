"""
jarvis_widget_v2.py
====================
실제로 동작(회전/펄스/파동/스캔라인)하는 3종 아바타 위젯

1) ParticleHoloAvatar      - A2 "파티클/데이터그리드 링" 동작 버전
2) FloatingHologramAvatar  - B5 "플로팅 홀로그램" 동작 버전
3) A2B5ComboAvatar         - new A2 particle grid + B5 floating hologram combo

공통 기능
- set_state(JarvisState.IDLE/LISTENING/SPEAKING/THINKING)
- set_audio_level(0.0~1.0)  -> SPEAKING 중 실시간 반응
- 색상은 생성자 파라미터로 자유롭게 변경 가능

실행: python jarvis_widget_v2.py  (pip install PySide6 필요)
"""

import sys
import math
import random

from PySide6.QtCore import Qt, QTimer, QRectF, QPointF, Signal
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QPixmap, QRadialGradient, QLinearGradient,
    QConicalGradient, QPainterPath, QTransform
)
from PySide6.QtWidgets import (
    QWidget, QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QMainWindow, QSlider, QStackedWidget
)

from jarvis_widget import JarvisState  # 상태 enum 재사용


# ==========================================================================
# 공통 유틸
# ==========================================================================
def tinted(pixmap: QPixmap, overlay_fn) -> QPixmap:
    """pixmap의 알파 영역에만 overlay_fn이 그리는 내용을 합성(SourceAtop)"""
    result = QPixmap(pixmap.size())
    result.fill(Qt.transparent)
    p = QPainter(result)
    p.drawPixmap(0, 0, pixmap)
    p.setCompositionMode(QPainter.CompositionMode_SourceAtop)
    overlay_fn(p, result.rect())
    p.end()
    return result


class BaseAvatar(QWidget):
    """공통 상태/타이머/오디오 반응 로직을 담당하는 베이스 클래스"""

    stateChanged = Signal(JarvisState)

    def __init__(self, image_path="ohsung_mark_256.svg", diameter=220, parent=None, accent: QColor = None):
        super().__init__(parent)
        self._diameter = diameter
        pad = 100
        self.setFixedSize(diameter + pad, diameter + pad)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self._state = JarvisState.IDLE
        self._accent = accent or QColor(0, 230, 200)
        self._pixmap = None
        self._image_scale = 1.0
        if image_path is None:
            image_path = "ohsung_mark_256.svg"
        if image_path:
            self.set_image(image_path)

        self._t = 0.0
        self._rotation = 0.0
        self._audio_level = 0.0
        self._bar_levels = [0.0] * 28

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_frame)
        self._timer.start(22)

    # ---- public API ----
    def set_image(self, path):
        pm = QPixmap(path)
        if pm.isNull():
            raise FileNotFoundError(path)
        
        # 콘텐츠 자동 정렬 (오프셋/투명 여백 제거하여 중앙 정렬)
        image = pm.toImage()
        w, h = image.width(), image.height()
        min_x, min_y = w, h
        max_x, max_y = -1, -1
        for y in range(h):
            for x in range(w):
                if image.pixelColor(x, y).alpha() > 10:
                    if x < min_x: min_x = x
                    if x > max_x: max_x = x
                    if y < min_y: min_y = y
                    if y > max_y: max_y = y
        
        if max_x >= min_x and max_y >= min_y:
            cropped = pm.copy(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
            side = max(cropped.width(), cropped.height())
            squared = QPixmap(side, side)
            squared.fill(Qt.transparent)
            painter = QPainter(squared)
            px = (side - cropped.width()) / 2
            py = (side - cropped.height()) / 2
            painter.drawPixmap(px, py, cropped)
            painter.end()
            self._pixmap = squared
        else:
            self._pixmap = pm
            
        self.update()

    def set_image_scale(self, scale: float):
        """중앙 로고 이미지의 크기 배율(0.1 ~ 2.0)을 설정합니다."""
        self._image_scale = max(0.1, min(2.0, scale))
        self.update()

    def set_state(self, state: JarvisState):
        if state == self._state:
            return
        self._state = state
        self.stateChanged.emit(state)

    def set_audio_level(self, level: float):
        self._audio_level = max(0.0, min(1.0, level))

    # ---- 공통 애니메이션 계산 ----
    def _speed_factor(self):
        return {
            JarvisState.IDLE: 0.35,
            JarvisState.LISTENING: 0.75,
            JarvisState.THINKING: 1.0,
            JarvisState.SPEAKING: 1.5,
        }[self._state]

    def _pulse(self):
        speed = {
            JarvisState.IDLE: 0.035,
            JarvisState.LISTENING: 0.055,
            JarvisState.THINKING: 0.05,
            JarvisState.SPEAKING: 0.09,
        }[self._state]
        return 0.5 + 0.5 * math.sin(self._t * speed)

    def _on_frame(self):
        self._t += 1.0
        self._rotation = (self._rotation + self._speed_factor()) % 360

        n = len(self._bar_levels)
        for i in range(n):
            if self._state == JarvisState.SPEAKING:
                base = self._audio_level if self._audio_level > 0 else 0.5
                target = base * (0.3 + 0.7 * random.random())
            elif self._state == JarvisState.LISTENING:
                shimmer = abs(math.sin(self._t * 0.11 + i * 0.75))
                flicker = 0.18 * random.random()
                target = 0.22 + 0.34 * shimmer + flicker
            elif self._state == JarvisState.THINKING:
                target = 0.2 + 0.15 * abs(math.sin(self._t * 0.04 + i * 0.5))
            else:
                target = 0.05
            self._bar_levels[i] += (target - self._bar_levels[i]) * 0.25

        self.update()

    def _draw_mark(self, p, cx, cy, d, opacity=1.0):
        if self._pixmap is None:
            return
        p.setOpacity(opacity)
        d_scaled = d * self._image_scale
        p.drawPixmap(QRectF(cx - d_scaled / 2, cy - d_scaled / 2, d_scaled, d_scaled), self._pixmap, QRectF(self._pixmap.rect()))
        p.setOpacity(1.0)


# ==========================================================================
# 1) A2 - 파티클/데이터그리드 링 (동작 버전)
# ==========================================================================
class ParticleHoloAvatar(BaseAvatar):
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cx, cy = self.width() / 2, self.height() / 2
        base_r = self._diameter / 2
        accent = self._accent
        pulse = self._pulse()

        # 배경 그리드 (아주 은은하게 회전)
        p.save()
        p.translate(cx, cy)
        p.rotate(self._rotation * 0.08)
        grid_c = QColor(accent); grid_c.setAlpha(16)
        p.setPen(QPen(grid_c, 1))
        span = base_r + 60
        for gx in range(int(-span), int(span), 22):
            p.drawLine(QPointF(gx, -span), QPointF(gx, span))
        for gy in range(int(-span), int(span), 22):
            p.drawLine(QPointF(-span, gy), QPointF(span, gy))
        p.restore()

        # 파티클 두 겹 (반대 방향 회전, SPEAKING이면 오디오 바 크기에 반응)
        n_outer = 64
        n_inner = 40
        for ring_i, (radius, count, rot_mult, size_range) in enumerate([
            (base_r + 30, n_outer, 1.0, (0.9, 2.0)),
            (base_r + 14, n_inner, -1.6, (1.4, 3.0)),
        ]):
            for i in range(count):
                ang = (2 * math.pi / count) * i + math.radians(self._rotation * rot_mult)
                bar_idx = i % len(self._bar_levels)
                level = self._bar_levels[bar_idx]
                jitter = 1.0 + (0.6 * level if self._state == JarvisState.SPEAKING else 0.15 * pulse)
                r = radius * (1.0 if ring_i == 0 else 1.0)
                x = cx + r * math.cos(ang)
                y = cy + r * math.sin(ang)
                s = (size_range[0] + (size_range[1] - size_range[0]) * ((i * 37) % 10) / 10) * jitter
                c = QColor(accent)
                c.setAlpha(int(90 + 140 * (0.4 + 0.6 * level if self._state == JarvisState.SPEAKING else pulse)))
                p.setBrush(c); p.setPen(Qt.NoPen)
                p.drawEllipse(QPointF(x, y), s, s)

        # 중심 글로우
        glow_r = base_r + 34 + 8 * pulse
        radial = QRadialGradient(QPointF(cx, cy), glow_r)
        gc = QColor(accent); gc.setAlpha(int(60 * (0.4 + 0.6 * pulse)))
        radial.setColorAt(0.75, QColor(0, 0, 0, 0))
        radial.setColorAt(0.86, gc)
        radial.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(radial)); p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(cx, cy), glow_r, glow_r)

        # 마크 (살짝 숨쉬기)
        scale = 1.0 + 0.015 * pulse
        self._draw_mark(p, cx, cy, (base_r * 2 - 20) * scale)

        p.end()


# ==========================================================================
# 2) B5 - 플로팅 홀로그램 (동작 버전)
# ==========================================================================
class FloatingHologramAvatar(BaseAvatar):
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cx, cy = self.width() / 2, self.height() / 2
        base_r = self._diameter / 2
        accent = self._accent
        pulse = self._pulse()

        # 둥실둥실 떠 있는 느낌 (수직 보빙)
        bob = 6 * math.sin(self._t * 0.03)
        mcy = cy - 8 + bob

        # 배경 글로우
        glow_r = base_r + 40
        radial = QRadialGradient(QPointF(cx, mcy), glow_r)
        gc = QColor(accent); gc.setAlpha(int(55 * (0.5 + 0.5 * pulse)))
        radial.setColorAt(0.6, QColor(0, 0, 0, 0))
        radial.setColorAt(0.82, gc)
        radial.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(radial)); p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(cx, mcy), glow_r, glow_r)

        # 파동 바 (SPEAKING일 때 살아남)
        n = len(self._bar_levels)
        bar_base_r = base_r + 10
        for i in range(n):
            ang = (2 * math.pi / n) * i - math.radians(self._rotation * 0.6)
            level = self._bar_levels[i]
            bar_len = 3 + level * 20
            x1 = cx + bar_base_r * math.cos(ang); y1 = mcy + bar_base_r * math.sin(ang)
            x2 = cx + (bar_base_r + bar_len) * math.cos(ang); y2 = mcy + (bar_base_r + bar_len) * math.sin(ang)
            c = QColor(accent); c.setAlpha(int(80 + 160 * level))
            pen = QPen(c, 2.2); pen.setCapStyle(Qt.RoundCap)
            p.setPen(pen)
            p.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # 마크 본체 (미세 세로 압축으로 원근감)
        size = (base_r * 2 - 20) * self._image_scale
        if self._pixmap is not None:
            scaled = self._pixmap.scaled(int(size), int(size), Qt.KeepAspectRatio, Qt.SmoothTransformation)

            # 스캔라인 오버레이 (시간에 따라 위->아래로 스윕)
            def scanlines(pp, rect, t=self._t):
                pp.fillRect(rect, QColor(0, 0, 0, 0))
                line_c = QColor(accent.red(), accent.green(), accent.blue(), 70)
                pp.setPen(QPen(line_c, 1))
                offset = int(t * 1.6) % 8
                y = -8 + offset
                while y < rect.height():
                    pp.drawLine(0, y, rect.width(), y)
                    y += 4
                # 밝은 스윕 밴드
                sweep_y = (t * 2.2) % (rect.height() + 40) - 20
                band = QLinearGradient(0, sweep_y - 12, 0, sweep_y + 12)
                bc = QColor(accent.red(), accent.green(), accent.blue(), 0)
                bc2 = QColor(min(255, accent.red() + 80), min(255, accent.green() + 80),
                              min(255, accent.blue() + 80), 160)
                band.setColorAt(0, bc); band.setColorAt(0.5, bc2); band.setColorAt(1, bc)
                pp.fillRect(QRectF(0, sweep_y - 12, rect.width(), 24), band)

            layer = tinted(scaled, scanlines)

            p.save()
            transform = QTransform()
            transform.translate(cx, mcy)
            transform.scale(1.0, 0.96)
            transform.translate(-size / 2, -size / 2)
            p.setTransform(transform)
            p.setOpacity(0.97)
            p.drawPixmap(0, 0, scaled)
            p.setOpacity(0.55)
            p.drawPixmap(0, 0, layer)
            p.resetTransform()
            p.restore()

        # 얇은 궤도 링 (발밑, 떠 있는 느낌 강조)
        ring_c = QColor(accent); ring_c.setAlpha(140)
        pen = QPen(ring_c, 1.3)
        p.setPen(pen); p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, mcy + size / 2 - 4), size * 0.42, 11 + 3 * pulse)

        # 바닥 반사
        if self._pixmap is not None:
            p.save()
            p.setOpacity(0.15 + 0.05 * pulse)
            p.translate(cx, mcy + size / 2 + 8)
            p.scale(1, -1)
            p.drawPixmap(QRectF(-size / 2, 0, size, size * 0.35), self._pixmap,
                         QRectF(0, 0, self._pixmap.width(), self._pixmap.height() * 0.35))
            p.restore()

        p.end()


# ==========================================================================
# 데모 윈도우 - 3종을 탭으로 전환하며 상태/오디오 테스트
# ==========================================================================
class A2B5ComboAvatar(BaseAvatar):
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cx, cy = self.width() / 2, self.height() / 2
        base_r = self._diameter / 2
        accent = self._accent
        pulse = self._pulse()
        listening = self._state == JarvisState.LISTENING
        thinking = self._state == JarvisState.THINKING

        bob = (7 if listening else 4) * math.sin(self._t * (0.055 if listening else 0.03))
        mcy = cy - 8 + bob

        glow_r = base_r + (64 if listening else 48)
        radial = QRadialGradient(QPointF(cx, mcy), glow_r)
        gc = QColor(accent); gc.setAlpha(int(70 + 58 * pulse if listening else 44 + 28 * pulse))
        radial.setColorAt(0.48, QColor(0, 0, 0, 0))
        radial.setColorAt(0.78, gc)
        radial.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(radial)); p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(cx, mcy), glow_r, glow_r)

        p.save()
        p.translate(cx, mcy)
        p.rotate(self._rotation * (0.26 if listening else 0.14))
        grid_c = QColor(accent); grid_c.setAlpha(26 if listening else 14)
        p.setPen(QPen(grid_c, 1))
        span = base_r + 58
        step = 18 if listening else 24
        for gx in range(int(-span), int(span), step):
            p.drawLine(QPointF(gx, -span), QPointF(gx, span))
        for gy in range(int(-span), int(span), step):
            p.drawLine(QPointF(-span, gy), QPointF(span, gy))
        p.restore()

        n = 76 if listening else 56
        for i in range(n):
            ang = (2 * math.pi / n) * i + math.radians(self._rotation * (1.25 if listening else 0.75))
            level = self._bar_levels[i % len(self._bar_levels)]
            rr = base_r + 24 + (10 * level if listening else 3 * pulse)
            x = cx + rr * math.cos(ang)
            y = mcy + rr * math.sin(ang)
            dot = 1.4 + 3.2 * level if listening else 1.1 + 1.5 * pulse
            c = QColor(accent); c.setAlpha(int(95 + 150 * min(1.0, level + 0.2 * pulse)))
            p.setBrush(c); p.setPen(Qt.NoPen)
            p.drawEllipse(QPointF(x, y), dot, dot)

        ring_c = QColor(accent); ring_c.setAlpha(140 if listening else 95)
        p.setPen(QPen(ring_c, 1.2)); p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, mcy), base_r + 10 + 5 * pulse, base_r + 10 + 5 * pulse)
        p.drawEllipse(QPointF(cx, mcy), base_r + 32, 18 + 5 * pulse)

        if thinking:
            p.save()
            p.translate(cx, mcy)
            p.rotate(-self._rotation * 0.55)
            think_c = QColor(255, 215, 110, 155)
            p.setPen(QPen(think_c, 2.0))
            for i in range(6):
                a = math.radians(i * 60)
                r1 = base_r - 18
                r2 = base_r + 20 + 8 * pulse
                p.drawLine(
                    QPointF(r1 * math.cos(a), r1 * math.sin(a)),
                    QPointF(r2 * math.cos(a), r2 * math.sin(a)),
                )
            p.restore()

        size = (base_r * 2 - 28) * self._image_scale
        if self._pixmap is not None:
            scaled = self._pixmap.scaled(int(size), int(size), Qt.KeepAspectRatio, Qt.SmoothTransformation)

            def scanlines(pp, rect, t=self._t):
                line_c = QColor(accent.red(), accent.green(), accent.blue(), 80 if listening else 45)
                pp.setPen(QPen(line_c, 1))
                offset = int(t * (2.8 if listening else 1.6)) % 9
                y = -9 + offset
                while y < rect.height():
                    pp.drawLine(0, y, rect.width(), y)
                    y += 4 if listening else 6

                sweep_y = (t * (4.4 if listening else 2.2)) % (rect.height() + 44) - 22
                band = QLinearGradient(0, sweep_y - 14, 0, sweep_y + 14)
                bc = QColor(accent.red(), accent.green(), accent.blue(), 0)
                bc2 = QColor(min(255, accent.red() + 90), min(255, accent.green() + 90),
                              min(255, accent.blue() + 90), 210 if listening else 150)
                band.setColorAt(0, bc); band.setColorAt(0.5, bc2); band.setColorAt(1, bc)
                pp.fillRect(QRectF(0, sweep_y - 14, rect.width(), 28), band)

            layer = tinted(scaled, scanlines)
            p.drawPixmap(QRectF(cx - size / 2, mcy - size / 2, size, size), scaled, QRectF(scaled.rect()))
            p.setOpacity(0.72 if listening else 0.58)
            p.drawPixmap(QRectF(cx - size / 2, mcy - size / 2, size, size), layer, QRectF(layer.rect()))
            p.setOpacity(1.0)

            p.save()
            p.setOpacity(0.18 + 0.08 * pulse if listening else 0.12 + 0.04 * pulse)
            p.translate(cx, mcy + size / 2 + 8)
            p.scale(1, -1)
            p.drawPixmap(QRectF(-size / 2, 0, size, size * 0.32), self._pixmap,
                         QRectF(0, 0, self._pixmap.width(), self._pixmap.height() * 0.32))
            p.restore()

        p.end()


class DemoWindow(QMainWindow):
    def __init__(self, image_path):
        super().__init__()
        self.setWindowTitle("Jarvis Avatar v2 - A2 / B5 / A2+B5")
        self.setStyleSheet("background-color: #06080c;")

        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setAlignment(Qt.AlignCenter)

        self.stack = QStackedWidget()
        self.avatar_particle = ParticleHoloAvatar(image_path, diameter=220, accent=QColor(0, 230, 200))
        self.avatar_holo = FloatingHologramAvatar(image_path, diameter=220, accent=QColor(0, 210, 255))
        self.avatar_combo = A2B5ComboAvatar(image_path, diameter=220, accent=QColor(80, 240, 190))

        for w in self._avatars():
            holder = QWidget()
            lay = QVBoxLayout(holder)
            lay.setAlignment(Qt.AlignCenter)
            lay.addWidget(w, alignment=Qt.AlignCenter)
            self.stack.addWidget(holder)

        outer.addWidget(self.stack)

        self.status_label = QLabel("State: IDLE / Effect 1")
        self.status_label.setStyleSheet("color:#7fdfff; font-size:13px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        outer.addWidget(self.status_label)

        control_row = QHBoxLayout()
        self._current_state = JarvisState.IDLE
        state_specs = [
            (JarvisState.IDLE, "IDLE", "#71f2d2"),
            (JarvisState.LISTENING, "LISTENING", "#69b9ff"),
            (JarvisState.THINKING, "THINKING", "#ffd873"),
        ]
        for state, label, color in state_specs:
            col = QVBoxLayout()
            state_btn = QPushButton(label)
            state_btn.setStyleSheet(
                "QPushButton { background:#132030; color:%s; border:1px solid #2c4a5c;"
                " border-radius:6px; padding:8px 14px; font-weight:600;}"
                "QPushButton:hover{background:#1c3345;}" % color
            )
            state_btn.clicked.connect(lambda checked=False, s=state: self._select_state(s, None))
            col.addWidget(state_btn)

            variant_row = QHBoxLayout()
            for idx in range(3):
                mini = QPushButton(f"[{idx + 1}]")
                mini.setFixedWidth(42)
                mini.setStyleSheet(
                    "QPushButton { background:#0c131c; color:#d8fff8; border:1px solid #2c4a5c;"
                    " border-radius:5px; padding:5px 0; font-size:11px;}"
                    "QPushButton:hover{background:#203447; color:#fff;}"
                )
                mini.clicked.connect(lambda checked=False, s=state, i=idx: self._select_state(s, i))
                variant_row.addWidget(mini)
            col.addLayout(variant_row)
            control_row.addLayout(col)
        outer.addLayout(control_row)

        # 이미지 크기(배율)를 조절하는 슬라이더
        size_slider_row = QHBoxLayout()
        size_lbl = QLabel("이미지 크기 배율")
        size_lbl.setStyleSheet("color:#8fa; font-size:12px;")
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(10, 200)
        self.size_slider.setValue(100)
        self.size_slider.valueChanged.connect(self._set_scale_all)
        size_slider_row.addWidget(size_lbl)
        size_slider_row.addWidget(self.size_slider)
        outer.addLayout(size_slider_row)

        for w in self._avatars():
            w.stateChanged.connect(lambda s: self.status_label.setText(f"State: {s.name}"))

        self.resize(460, 560)

    def _avatars(self):
        return (self.avatar_particle, self.avatar_holo, self.avatar_combo)

    def _select_state(self, state, variant):
        self._current_state = state
        if variant is not None:
            self.stack.setCurrentIndex(variant)
        for w in self._avatars():
            w.set_state(state)
        self.status_label.setText(f"State: {state.name} / Effect {self.stack.currentIndex() + 1}")

    def _set_scale_all(self, v):
        scale = v / 100.0
        for w in self._avatars():
            w.set_image_scale(scale)


def main():
    image_path = sys.argv[1] if len(sys.argv) > 1 else "ohsung_mark_256.svg"
    app = QApplication(sys.argv)
    win = DemoWindow(image_path)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
