import math
from PySide6.QtCore import Qt, QTimer, QRectF, QPoint, QPointF, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QPen, QRadialGradient, QConicalGradient, QTransform, QPainterPath, QBrush
from PySide6.QtWidgets import QWidget, QLabel

class SciFiAvatarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(170, 170)
        self.state = "idle"  # idle, thinking, talking
        
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
        
        # Particle Holo Effect variables
        self._t = 0.0
        self._rotation = 0.0
        self._bar_levels = [0.0] * 28
        
        # Timer for 60fps rendering
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16) # ~60fps
        
        self.theme_color = QColor("#D32F2F")
        self.accent_color = QColor("#FFCDD2")
        
        # Mini Speech Bubble Overlay
        self.mini_bubble = MiniOverlayBubble(self)
        self.mini_bubble.setGeometry(35, 8, 100, 42)

    def set_pixmaps(self, pixmaps_dict):
        self.pixmaps = pixmaps_dict

    def set_state(self, state):
        self.state = state
        self.pulse_radius = 0
        self.pulse_opacity = 255
        self.breath_time = 0
        
    def show_mini_message(self, text, is_success=True, duration_ms=1000):
        self.mini_bubble.show_message(text, is_success, duration_ms)

    def update_frame(self):
        # Update angles
        self.angle_ring1 = (self.angle_ring1 + 1) % 360
        self.angle_ring2 = (self.angle_ring2 - 1.5) % 360
        self.angle_ring3 = (self.angle_ring3 + 0.5) % 360
        
        if self.state in ["idle", "thinking"]:
            self.radar_angle = (self.radar_angle + 2) % 360
            
        # Pulse update
        if self.state == "idle":
            self.pulse_radius += 0.38 # Grow slower to prevent clipping outside widget bounds (170x170)
            self.pulse_opacity -= 3
            if self.pulse_opacity <= 0:
                self.pulse_opacity = 255
                self.pulse_radius = 0
                
        # Breathing update
        if self.state == "thinking":
            self.breath_time += 0.05
            self.breath_scale = 1.0 + 0.03 * math.sin(self.breath_time)
        else:
            self.breath_scale = 1.0
            
        # Particle Holo Effect Update
        self._t += 1.0
        self._rotation = (self._rotation + (1.0 if self.state == "thinking" else 0.35)) % 360
        
        # Update bar levels for particle grid animation
        n = len(self._bar_levels)
        for i in range(n):
            if self.state == "thinking":
                target = 0.2 + 0.15 * math.sin(self._t * 0.04 + i * 0.5)
            else:
                target = 0.05
            self._bar_levels[i] += (target - self._bar_levels[i]) * 0.25
            
        self.update() # Trigger paintEvent

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        cx, cy = self.width() / 2, self.height() / 2
        
        # Determine colors based on state
        if self.state == "thinking":
            # [변경전]
            # theme_color = self.theme_color
            # accent_color = self.accent_color
            # ring3_color = QColor("#B71C1C")
            theme_color = QColor("#10a684")      # 메인 색상 (사용자 요청으로 왼쪽 색상에 맞춰 #71f2d2에서 변경)
            accent_color = QColor("#72e5c8")     # 연한 강조 색상 (사용자 요청으로 왼쪽 색상에 맞춰 #B6F9EE에서 변경)
            ring3_color = QColor("#085846")      # 어두운 색상 (사용자 요청으로 왼쪽 색상에 맞춰 #13856C에서 변경)
        else:
            theme_color = self.theme_color
            accent_color = self.accent_color
            ring3_color = QColor("#B71C1C")
        
        if self.state == "thinking":
            # --- [시작] ParticleHoloAvatar (Effect 1) 적용 ---
            base_r = 53.0 # 170x170 위젯 크기에 맞춰 최적화된 기준 반경 (idle 상태의 최대 반경 78과 맞춤)
            pulse_speed = 0.05
            pulse = 0.5 + 0.5 * math.sin(self._t * pulse_speed)
            accent = accent_color
            
            # (1) 배경 그리드 (아주 은은하게 회전) - 사용자 요청으로 제외 처리
            # painter.save()
            # painter.translate(cx, cy)
            # painter.rotate(self._rotation * 0.08)
            # grid_c = QColor(accent)
            # grid_c.setAlpha(32) # 라이트 배경에서의 시인성을 위해 기존 16에서 32로 상향 조정
            # painter.setPen(QPen(grid_c, 1))
            # span = base_r + 30 # 170x170 위젯 내부로 스팬 조절
            # for gx in range(int(-span), int(span), 18):
            #     painter.drawLine(QPointF(gx, -span), QPointF(gx, span))
            # for gy in range(int(-span), int(span), 18):
            #     painter.drawLine(QPointF(-span, gy), QPointF(span, gy))
            # painter.restore()

            # (2) 파티클 두 겹 (반대 방향 회전)
            n_outer = 64
            n_inner = 40
            for ring_i, (radius, count, rot_mult, size_range) in enumerate([
                (base_r + 25, n_outer, 1.0, (0.9, 1.8)),  # Outer ring radius: 78 (idle 외곽 원 범위와 일치)
                (base_r + 15, n_inner, -1.6, (1.2, 2.6)), # Inner ring radius: 68 (idle 내부 원 범위와 일치)
            ]):
                for i in range(count):
                    ang = (2 * math.pi / count) * i + math.radians(self._rotation * rot_mult)
                    bar_idx = i % len(self._bar_levels)
                    level = self._bar_levels[bar_idx]
                    jitter = 1.0 + 0.15 * pulse
                    r = radius
                    x = cx + r * math.cos(ang)
                    y = cy + r * math.sin(ang)
                    s = (size_range[0] + (size_range[1] - size_range[0]) * ((i * 37) % 10) / 10) * jitter
                    c = QColor(accent)
                    c.setAlpha(int(90 + 140 * pulse))
                    painter.setBrush(c)
                    painter.setPen(Qt.NoPen)
                    painter.drawEllipse(QPointF(x, y), s, s)

            # (3) 중심 글로우
            glow_r = base_r + 25 + 6 * pulse
            radial = QRadialGradient(QPointF(cx, cy), glow_r)
            gc = QColor(accent)
            gc.setAlpha(int(60 * (0.4 + 0.6 * pulse)))
            radial.setColorAt(0.75, QColor(0, 0, 0, 0))
            radial.setColorAt(0.86, gc)
            radial.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setBrush(QBrush(radial))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(cx, cy), glow_r, glow_r)
            # --- [끝] ParticleHoloAvatar (Effect 1) 적용 ---
        else:
            # 1. Pulse Glow (only in idle)
            if self.state == "idle" and self.pulse_opacity > 0:
                grad = QRadialGradient(cx, cy, self.pulse_radius + 51)
                # [변경전]
                # c = QColor(self.accent_color)
                c = QColor(accent_color)
                c.setAlpha(max(0, int(self.pulse_opacity * 0.5)))
                grad.setColorAt(0, Qt.transparent)
                grad.setColorAt(0.8, c)
                grad.setColorAt(1, Qt.transparent)
                painter.setPen(Qt.NoPen)
                painter.setBrush(grad)
                painter.drawEllipse(QPoint(int(cx), int(cy)), int(self.pulse_radius + 51), int(self.pulse_radius + 51))

            # 2. Radar Scan Beam (idle)
            # [변경전: thinking 상태 포함]
            # if self.state in ["idle", "thinking"]:
            if self.state == "idle":
                conical = QConicalGradient(cx, cy, -self.radar_angle)
                # [변경전]
                # c_radar = QColor(self.theme_color)
                c_radar = QColor(theme_color)
                c_radar.setAlpha(100)
                conical.setColorAt(0, c_radar)
                conical.setColorAt(0.1, Qt.transparent)
                conical.setColorAt(1, Qt.transparent)
                painter.setBrush(conical)
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(QPoint(int(cx), int(cy)), 77, 77)

            # 3. Rings (Solid Arcs)
            # [변경전]
            # pen = QPen(self.theme_color, 2.0)
            pen = QPen(theme_color, 2.0)
            pen.setCapStyle(Qt.RoundCap) # 둥근 끝처리
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            
            def draw_ring(radius, angle_offset, span_angles):
                rect = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)
                painter.save()
                painter.translate(cx, cy)
                painter.rotate(angle_offset)
                painter.translate(-cx, -cy)
                for start, span in span_angles:
                    # drawArc requires angles in 1/16th of a degree
                    painter.drawArc(rect, int(start * 16), int(span * 16))
                painter.restore()

            # Ring 1: 두 개의 긴 실선 아크
            draw_ring(72, self.angle_ring1, [(0, 120), (180, 120)])
            
            # Ring 2: 세 개의 짧은 실선 아크 (Accent Color)
            # [변경전]
            # pen.setColor(self.accent_color)
            pen.setColor(accent_color)
            pen.setWidthF(1.5)
            painter.setPen(pen)
            draw_ring(66, self.angle_ring2, [(0, 60), (120, 60), (240, 60)])
            
            # Ring 3: 한 개의 매우 긴 실선과 작은 조각 (Dark Color)
            # [변경전]
            # pen.setColor(QColor("#B71C1C"))
            pen.setColor(ring3_color)
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
            painter.scale(self.breath_scale, self.breath_scale)
            
            y_offset = 0
            if self.state == "talking":
                y_offset = -2.5 * math.sin(self.angle_ring1 * 0.2)
            painter.translate(-cx, -cy + y_offset)
            
            img_w, img_h = 93, 93 # Scaled to 70% of 133
            target_rect = QRectF(cx - img_w/2, cy - img_h/2 - 2, img_w, img_h)
            painter.drawPixmap(target_rect, pixmap, QRectF(pixmap.rect()))
            painter.restore()


class SpeechBubbleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 80)
        self.state = "idle"
        self.text = ""
        
        self.label = QLabel(self)
        self.label.setStyleSheet("color: #333333; font-size: 13px; font-weight: bold; font-family: 'Outfit', sans-serif;")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label.setGeometry(25, 10, 260, 60)
        
        self.dots = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_dots)
        
        self.anim = QPropertyAnimation(self.label, b"pos")
        
        self.hide() # Hidden by default
        
    def update_dots(self):
        self.dots = (self.dots + 1) % 4
        self.label.setText("데이터베이스 조회 중" + "·" * self.dots)
        
    def set_state(self, state, text=""):
        self.state = state
        self.text = text
        
        if state == "idle":
            self.timer.stop()
            self.hide()
            
        elif state == "thinking":
            self.show()
            self.timer.start(400)
            self.label.move(25, 10)
            self.update_dots()
            
        elif state == "talking":
            self.show()
            self.timer.stop()
            self.label.setText(text)
            
            # Slide in animation
            self.anim.stop()
            self.anim.setDuration(500)
            self.anim.setStartValue(QPoint(25, 80)) # from bottom
            self.anim.setEndValue(QPoint(25, 10))
            self.anim.setEasingCurve(QEasingCurve.OutBack)
            self.anim.start()
            
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        rect = QRectF(15, 5, 280, 70)
        path.addRoundedRect(rect, 15, 15)
        
        # Tail
        path.moveTo(15, 35)
        path.lineTo(0, 40)
        path.lineTo(15, 45)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#FFFFFF"))
        painter.drawPath(path)
        
        # Border
        painter.setPen(QColor("#FFCDD2"))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)


class MiniOverlayBubble(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 42)
        self.text = ""
        # [변경전]
        # self.bg_color = QColor("#10a684")
        self.bg_color = QColor("#FFFFFF")
        self.text_color = QColor("#10a684")
        self.hide()
        
    def show_message(self, text, is_success=True, duration_ms=1000):
        self.text = text
        if is_success:
            # [변경전]
            # self.bg_color = QColor("#10a684")
            self.bg_color = QColor("#FFFFFF")
            self.text_color = QColor("#10a684")
        else:
            self.bg_color = QColor("#D32F2F")
            self.text_color = QColor("#FFFFFF")
        self.show()
        self.raise_()
        self.update()
        QTimer.singleShot(duration_ms, self.hide)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        rect = QRectF(0, 0, 100, 30)
        path.addRoundedRect(rect, 15, 15)
        
        # Tail pointing downwards
        path.moveTo(45, 30)
        path.lineTo(50, 38)
        path.lineTo(55, 30)
        
        # Set border pen for white bubble to keep design clean
        from PySide6.QtGui import QPen
        if self.bg_color == QColor("#FFFFFF"):
            painter.setPen(QPen(QColor("#10a684"), 1))
        else:
            painter.setPen(Qt.NoPen)
            
        painter.setBrush(self.bg_color)
        painter.drawPath(path)
        
        # Text
        # [변경전]
        # painter.setPen(QColor("#FFFFFF"))
        painter.setPen(self.text_color)
        font = painter.font()
        font.setFamily("Outfit")
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignCenter, self.text)
