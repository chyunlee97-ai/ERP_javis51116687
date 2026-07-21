"""
jarvis_widget_v0.py
====================
현재 ERP 챗봇의 기본 위젯(SciFiAvatarWidget)과 v2 디자인을 종합적으로 체크하는 테스트 파일.
- [0] : 원래 위젯
- [1, 2, 3] : v2 효과 (파티클, 홀로그램, 콤보)
- 각 상태별 색상 적용 가능
"""

import sys
import math
from PySide6.QtCore import Qt, QTimer, QRectF, QPoint, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QPen, QRadialGradient, QConicalGradient, QPixmap
from PySide6.QtWidgets import (
    QWidget, QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMainWindow, QLineEdit, QStackedWidget
)

# v2 위젯과 상태 Enum 가져오기
from jarvis_widget import JarvisState
from jarvis_widget_v2 import ParticleHoloAvatar, FloatingHologramAvatar, A2B5ComboAvatar

class SciFiAvatarWidget(QWidget):
    def __init__(self, parent=None, theme_color="#D32F2F", accent_color="#FFCDD2"):
        super().__init__(parent)
        self.setFixedSize(170, 170)
        self.state = "idle"  # idle, thinking, talking, listening
        
        self.pixmaps = {}
        
        # Animation variables
        self.angle_ring1 = 0
        self.angle_ring2 = 0
        self.angle_ring3 = 0
        self.radar_angle = 0
        self.pulse_radius = 0
        self.pulse_opacity = 255
        self.breath_scale = 1.0
        self.breath_time = 0
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16)
        
        self.theme_color = QColor(theme_color)
        self.accent_color = QColor(accent_color)
        self._image_scale = 1.0

    def set_color(self, hex_color):
        self.accent_color = QColor(hex_color)
        self.theme_color = QColor(hex_color).darker(150) # 테마 컬러도 어울리게 변경

    def set_image_scale(self, scale):
        self._image_scale = scale

    def set_pixmaps(self, pixmaps_dict):
        self.pixmaps = pixmaps_dict

    def set_state(self, state):
        if isinstance(state, JarvisState):
            state_map = {
                JarvisState.IDLE: "idle",
                JarvisState.LISTENING: "listening",
                JarvisState.THINKING: "thinking",
                JarvisState.SPEAKING: "talking",
            }
            self.state = state_map.get(state, "idle")
        else:
            self.state = state
        self.pulse_radius = 0
        self.pulse_opacity = 255
        self.breath_time = 0

    def set_audio_level(self, level):
        pass

    def update_frame(self):
        self.angle_ring1 = (self.angle_ring1 + 1) % 360
        self.angle_ring2 = (self.angle_ring2 - 1.5) % 360
        self.angle_ring3 = (self.angle_ring3 + 0.5) % 360
        
        if self.state in ["idle", "thinking", "listening"]:
            self.radar_angle = (self.radar_angle + 2) % 360
            
        if self.state == "idle":
            self.pulse_radius += 0.38
            self.pulse_opacity -= 3
            if self.pulse_opacity <= 0:
                self.pulse_opacity = 255
                self.pulse_radius = 0
                
        if self.state == "thinking":
            self.breath_time += 0.05
            self.breath_scale = 1.0 + 0.03 * math.sin(self.breath_time)
        elif self.state == "listening":
            self.breath_time += 0.08
            self.breath_scale = 1.0 + 0.05 * math.sin(self.breath_time)
        else:
            self.breath_scale = 1.0
            
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        cx, cy = self.width() / 2, self.height() / 2
        
        # 1. Pulse Glow
        if self.state == "idle" and self.pulse_opacity > 0:
            grad = QRadialGradient(cx, cy, self.pulse_radius + 51)
            c = QColor(self.accent_color)
            c.setAlpha(max(0, int(self.pulse_opacity * 0.5)))
            grad.setColorAt(0, Qt.transparent)
            grad.setColorAt(0.8, c)
            grad.setColorAt(1, Qt.transparent)
            painter.setPen(Qt.NoPen)
            painter.setBrush(grad)
            painter.drawEllipse(QPoint(int(cx), int(cy)), int(self.pulse_radius + 51), int(self.pulse_radius + 51))

        # 2. Radar Scan Beam
        if self.state in ["idle", "thinking", "listening"]:
            conical = QConicalGradient(cx, cy, -self.radar_angle)
            c_radar = QColor(self.theme_color)
            c_radar.setAlpha(100)
            conical.setColorAt(0, c_radar)
            conical.setColorAt(0.1, Qt.transparent)
            conical.setColorAt(1, Qt.transparent)
            painter.setBrush(conical)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPoint(int(cx), int(cy)), 77, 77)

        # 3. Rings
        pen = QPen(self.theme_color, 2.0)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        
        def draw_ring(radius, angle_offset, span_angles):
            rect = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)
            painter.save()
            painter.translate(cx, cy)
            painter.rotate(angle_offset)
            painter.translate(-cx, -cy)
            for start, span in span_angles:
                painter.drawArc(rect, int(start * 16), int(span * 16))
            painter.restore()

        draw_ring(72, self.angle_ring1, [(0, 120), (180, 120)])
        
        pen.setColor(self.accent_color)
        pen.setWidthF(1.5)
        painter.setPen(pen)
        draw_ring(66, self.angle_ring2, [(0, 60), (120, 60), (240, 60)])
        
        pen.setColor(self.theme_color.darker(150))
        pen.setWidthF(2.5)
        painter.setPen(pen)
        draw_ring(78, self.angle_ring3, [(0, 220), (260, 40)])

        # 4. Character Image
        pixmap = self.pixmaps.get(self.state)
        if not pixmap:
            pixmap = self.pixmaps.get("idle")
            
        if pixmap and not pixmap.isNull():
            painter.save()
            painter.translate(cx, cy)
            s = self.breath_scale * self._image_scale
            painter.scale(s, s)
            
            y_offset = 0
            if self.state == "talking":
                y_offset = -2.5 * math.sin(self.angle_ring1 * 0.2)
            painter.translate(-cx, -cy + y_offset)
            
            img_w, img_h = 93, 93
            target_rect = QRectF(cx - img_w/2, cy - img_h/2 - 2, img_w, img_h)
            painter.drawPixmap(target_rect, pixmap, QRectF(pixmap.rect()))
            painter.restore()

class DemoWindow(QMainWindow):
    def __init__(self, image_path):
        super().__init__()
        self.setWindowTitle("Jarvis Avatar v0/v2 Design Check")
        self.setStyleSheet("background-color: #06080c; color: white;")

        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setAlignment(Qt.AlignCenter)

        self.stack = QStackedWidget()
        
        self.avatar_v0 = SciFiAvatarWidget(theme_color="#D32F2F", accent_color="#FFCDD2")
        self.avatar_particle = ParticleHoloAvatar(image_path, diameter=220, accent=QColor(0, 230, 200))
        self.avatar_holo = FloatingHologramAvatar(image_path, diameter=220, accent=QColor(0, 210, 255))
        self.avatar_combo = A2B5ComboAvatar(image_path, diameter=220, accent=QColor(80, 240, 190))

        self.avatars = [self.avatar_v0, self.avatar_particle, self.avatar_holo, self.avatar_combo]
        
        pm = QPixmap(image_path)
        self.avatar_v0.set_pixmaps({"idle": pm, "thinking": pm, "talking": pm, "listening": pm})

        for w in self.avatars:
            holder = QWidget()
            lay = QVBoxLayout(holder)
            lay.setAlignment(Qt.AlignCenter)
            lay.addWidget(w, alignment=Qt.AlignCenter)
            self.stack.addWidget(holder)

        outer.addWidget(self.stack)

        self.status_label = QLabel("State: IDLE / Effect 0")
        self.status_label.setStyleSheet("color:#7fdfff; font-size:13px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        outer.addWidget(self.status_label)

        control_row = QHBoxLayout()
        state_specs = [
            (JarvisState.IDLE, "IDLE", "#71f2d2", "#71f2d2"),
            (JarvisState.THINKING, "THINKING", "#ffd873", "#ffd873"),
            (JarvisState.SPEAKING, "TALKING", "#69b9ff", "#69b9ff"),
            (JarvisState.LISTENING, "LISTENING", "#b388ff", "#b388ff"),
        ]
        
        self.color_inputs = {}

        for state, label, default_hex, btn_color in state_specs:
            col = QVBoxLayout()
            col.setAlignment(Qt.AlignTop)
            
            # 색상 입력부
            color_row = QHBoxLayout()
            color_input = QLineEdit(default_hex)
            color_input.setFixedWidth(65)
            color_input.setStyleSheet("background:#132030; color:#fff; border:1px solid #2c4a5c; border-radius:3px;")
            self.color_inputs[state] = color_input
            
            apply_btn = QPushButton("적용")
            apply_btn.setStyleSheet("background:#203447; color:#fff; border:1px solid #2c4a5c; border-radius:3px; padding:2px 4px; font-size:11px;")
            apply_btn.clicked.connect(lambda checked=False, s=state: self._apply_color(s))
            
            color_row.addWidget(color_input)
            color_row.addWidget(apply_btn)
            col.addLayout(color_row)
            
            # 상태 버튼
            state_btn = QPushButton(label)
            state_btn.setStyleSheet(
                "QPushButton { background:#132030; color:%s; border:1px solid #2c4a5c;"
                " border-radius:6px; padding:8px 14px; font-weight:600;}"
                "QPushButton:hover{background:#1c3345;}" % btn_color
            )
            state_btn.clicked.connect(lambda checked=False, s=state: self._select_state(s, None))
            col.addWidget(state_btn)

            # 이펙트 선택 버튼 (0, 1, 2, 3)
            variant_row = QHBoxLayout()
            variant_row.setSpacing(2)
            for idx in range(4):
                mini = QPushButton(f"[{idx}]")
                mini.setFixedWidth(28)
                mini.setStyleSheet(
                    "QPushButton { background:#0c131c; color:#d8fff8; border:1px solid #2c4a5c;"
                    " border-radius:3px; padding:5px 0; font-size:11px;}"
                    "QPushButton:hover{background:#203447; color:#fff;}"
                )
                mini.clicked.connect(lambda checked=False, s=state, i=idx: self._select_state(s, i))
                variant_row.addWidget(mini)
            col.addLayout(variant_row)
            
            control_row.addLayout(col)
            
        outer.addLayout(control_row)
        self.resize(650, 550)

    def _apply_color(self, state):
        hex_color = self.color_inputs[state].text().strip()
        c = QColor(hex_color)
        if not c.isValid():
            return
            
        idx = self.stack.currentIndex()
        target_avatar = self.avatars[idx]
        if hasattr(target_avatar, '_accent'):
            target_avatar._accent = c
        if hasattr(target_avatar, 'set_color'):
            target_avatar.set_color(hex_color)
            
        self._select_state(state, None)

    def _select_state(self, state, variant):
        if variant is not None:
            self.stack.setCurrentIndex(variant)
            
        for w in self.avatars:
            if hasattr(w, 'set_state'):
                w.set_state(state)
                
        state_name = state.name if hasattr(state, 'name') else state
        if state == JarvisState.SPEAKING:
            state_name = "TALKING"
            
        self.status_label.setText(f"State: {state_name} / Effect {self.stack.currentIndex()}")

def main():
    image_path = sys.argv[1] if len(sys.argv) > 1 else "ohsung_mark_256.svg"
    app = QApplication(sys.argv)
    win = DemoWindow(image_path)
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
