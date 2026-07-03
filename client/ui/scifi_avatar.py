import math
from PySide6.QtCore import Qt, QTimer, QRectF, QPoint, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QPen, QRadialGradient, QConicalGradient, QTransform, QPainterPath
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
        
        # Timer for 60fps rendering
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16) # ~60fps
        
        self.theme_color = QColor("#D32F2F")
        self.accent_color = QColor("#FFCDD2")

    def set_pixmaps(self, pixmaps_dict):
        self.pixmaps = pixmaps_dict

    def set_state(self, state):
        self.state = state
        self.pulse_radius = 0
        self.pulse_opacity = 255
        self.breath_time = 0

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
            
        self.update() # Trigger paintEvent

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        cx, cy = self.width() / 2, self.height() / 2
        
        # 1. Pulse Glow (only in idle)
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

        # 2. Radar Scan Beam (idle, thinking)
        if self.state in ["idle", "thinking"]:
            conical = QConicalGradient(cx, cy, -self.radar_angle)
            c_radar = QColor(self.theme_color)
            c_radar.setAlpha(100)
            conical.setColorAt(0, c_radar)
            conical.setColorAt(0.1, Qt.transparent)
            conical.setColorAt(1, Qt.transparent)
            painter.setBrush(conical)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPoint(int(cx), int(cy)), 77, 77)

        # 3. Rings (Solid Arcs)
        pen = QPen(self.theme_color, 2.0)
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
        pen.setColor(self.accent_color)
        pen.setWidthF(1.5)
        painter.setPen(pen)
        draw_ring(66, self.angle_ring2, [(0, 60), (120, 60), (240, 60)])
        
        # Ring 3: 한 개의 매우 긴 실선과 작은 조각 (Dark Color)
        pen.setColor(QColor("#B71C1C"))
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
