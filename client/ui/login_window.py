import os
import sys
import requests
from PySide6.QtCore import Qt, QPoint, QSettings, Signal, QRectF
from PySide6.QtGui import QPixmap, QIcon, QPainter, QPainterPath, QColor, QFont, QPen, QBrush, QFontDatabase
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QCheckBox, 
    QVBoxLayout, QHBoxLayout, QFrame, QGraphicsDropShadowEffect,
    QButtonGroup, QMessageBox, QGridLayout
)
from config import API_BASE_URL

# Find project root path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class LoginWindow(QWidget):
    # Signals to pass back factory, user id, and language after successful login
    login_success = Signal(str, str, str)

    def __init__(self):
        super().__init__()
        
        self.drag_position = None
        self.settings = QSettings("OHSUNG", "ERPBot")
        self.selected_lang = "KR"
        self.fact_code = "Y6"  # Factory is initialized to "Y6" by default
        
        # Load Michroma font dynamically
        font_path = os.path.join(PROJECT_ROOT, "client", "fonts", "Michroma-Regular.ttf")
        if os.path.exists(font_path):
            QFontDatabase.addApplicationFont(font_path)
            
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(310, 410)
        
        # Main shadow border wrapper
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        
        self.bg_frame = QFrame()
        self.bg_frame.setObjectName("MainFrame")
        self.bg_frame.setStyleSheet("""
            QFrame#MainFrame {
                background-color: #2E88D8;
                border-radius: 10px;
            }
        """)
        
        # Apply drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 2)
        self.bg_frame.setGraphicsEffect(shadow)
        
        frame_layout = QVBoxLayout(self.bg_frame)
        frame_layout.setContentsMargins(0, 0, 0, 12)
        frame_layout.setSpacing(0)
        
        # 1. Custom Frameless Title Bar
        title_bar = QFrame()
        title_bar.setFixedHeight(30)
        title_bar.setStyleSheet("""
            QFrame {
                background-color: #EFECE1;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                border-bottom: 1px solid #D8D4C7;
            }
        """)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        # Red circle logo -> ohsung_mark_256.png scaled down to 16x16
        logo_lbl = QLabel()
        logo_lbl.setFixedSize(16, 16)
        logo_lbl.setStyleSheet("background: transparent; border: none;")
        logo_path = os.path.join(PROJECT_ROOT, "image", "ohsung_mark_256.png")
        if os.path.exists(logo_path):
            logo_pix = QPixmap(logo_path)
            logo_lbl.setPixmap(logo_pix.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # Fallback drawing
            logo_pix = QPixmap(16, 16)
            logo_pix.fill(Qt.transparent)
            p = QPainter(logo_pix)
            p.setRenderHint(QPainter.Antialiasing)
            p.setBrush(QBrush(QColor("#D32F2F")))
            p.setPen(Qt.NoPen)
            p.drawEllipse(0, 0, 16, 16)
            p.end()
            logo_lbl.setPixmap(logo_pix)
            
        title_layout.addWidget(logo_lbl)
        
        title_text = QLabel("OHSUNG Bot")
        title_text.setStyleSheet("color: #333333; font-weight: bold; font-family: 'Michroma', 'Malgun Gothic', '맑은 고딕', 'Segoe UI', Arial, sans-serif; font-size: 10px; background: transparent; border: none;")
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        
        # Minimize / Close buttons
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(18, 18)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #555555;
                font-size: 11px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                color: #D32F2F;
            }
        """)
        btn_close.clicked.connect(self.close_app)
        title_layout.addWidget(btn_close)
        
        frame_layout.addWidget(title_bar)
        
        # 2. Main Content Body
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(18, 12, 18, 8)
        content_layout.setSpacing(10)
        
        # Middle OHSUNG Logo + ERP System title
        logo_container = QHBoxLayout()
        logo_container.setSpacing(10)
        logo_container.setAlignment(Qt.AlignCenter)
        
        big_logo = QLabel()
        big_logo.setFixedSize(42, 42)
        if os.path.exists(logo_path):
            big_logo_pix = QPixmap(logo_path)
            big_logo.setPixmap(big_logo_pix.scaled(42, 42, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # Fallback drawing
            big_logo_pix = QPixmap(42, 42)
            big_logo_pix.fill(Qt.transparent)
            p = QPainter(big_logo_pix)
            p.setRenderHint(QPainter.Antialiasing)
            p.setPen(QPen(QColor("#D32F2F"), 2))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(2, 2, 38, 38)
            p.end()
            big_logo.setPixmap(big_logo_pix)
            
        logo_container.addWidget(big_logo)
        
        title_txt_layout = QVBoxLayout()
        title_txt_layout.setSpacing(0)
        title_txt_layout.setAlignment(Qt.AlignVCenter)
        
        lbl_sys_title = QLabel("OHSUNG Bot")
        lbl_sys_title.setStyleSheet("color: white; font-size: 18px; font-weight: bold; font-family: 'Michroma', 'Malgun Gothic', '맑은 고딕', 'Segoe UI', Arial, sans-serif; letter-spacing: 1px;")
        title_txt_layout.addWidget(lbl_sys_title)
        
        logo_container.addLayout(title_txt_layout)
        content_layout.addLayout(logo_container)
        content_layout.addSpacing(4)
        
        # ID Field
        self.id_frame = QFrame()
        self.id_frame.setFixedHeight(38)
        self.id_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 5px;
            }
        """)
        id_layout = QHBoxLayout(self.id_frame)
        id_layout.setContentsMargins(10, 0, 10, 0)
        id_layout.setSpacing(8)
        
        lbl_id_icon = QLabel("👤")
        lbl_id_icon.setStyleSheet("color: #777777; font-size: 12px;")
        id_layout.addWidget(lbl_id_icon)
        
        divider_id = QFrame()
        divider_id.setFixedWidth(1)
        divider_id.setStyleSheet("background-color: #E0E0E0;")
        id_layout.addWidget(divider_id)
        
        self.txt_id = QLineEdit()
        self.txt_id.setPlaceholderText("USER ID")
        self.txt_id.setStyleSheet("""
            QLineEdit {
                border: none;
                background: transparent;
                color: #333333;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Malgun Gothic', '맑은 고딕', 'Segoe UI', Arial, sans-serif;
            }
        """)
        id_layout.addWidget(self.txt_id)
        content_layout.addWidget(self.id_frame)
        
        # PASSWORD Field
        self.psw_frame = QFrame()
        self.psw_frame.setFixedHeight(38)
        self.psw_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 5px;
            }
        """)
        psw_layout = QHBoxLayout(self.psw_frame)
        psw_layout.setContentsMargins(10, 0, 10, 0)
        psw_layout.setSpacing(8)
        
        lbl_psw_icon = QLabel("🔒")
        lbl_psw_icon.setStyleSheet("color: #777777; font-size: 12px;")
        psw_layout.addWidget(lbl_psw_icon)
        
        divider_psw = QFrame()
        divider_psw.setFixedWidth(1)
        divider_psw.setStyleSheet("background-color: #E0E0E0;")
        psw_layout.addWidget(divider_psw)
        
        self.txt_psw = QLineEdit()
        self.txt_psw.setPlaceholderText("PASSWORD")
        self.txt_psw.setEchoMode(QLineEdit.Password)
        self.txt_psw.setStyleSheet("""
            QLineEdit {
                border: none;
                background: transparent;
                color: #333333;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Malgun Gothic', '맑은 고딕', 'Segoe UI', Arial, sans-serif;
            }
        """)
        psw_layout.addWidget(self.txt_psw)
        content_layout.addWidget(self.psw_frame)
        
        # Checkboxes (Remember ID & Remember Psw) with custom white checkmark icon
        chk_layout = QHBoxLayout()
        chk_layout.setSpacing(12)
        
        svg_path = os.path.join(PROJECT_ROOT, "image", "check_v.svg").replace("\\", "/")
        chk_style = f"""
            QCheckBox {{
                color: white;
                font-weight: bold;
                font-size: 11px;
                font-family: 'Malgun Gothic', '맑은 고딕', 'Segoe UI', Arial, sans-serif;
            }}
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                border: 1px solid white;
                border-radius: 3px;
                background: transparent;
            }}
            QCheckBox::indicator:checked {{
                background-color: #D32F2F;
                border: 1px solid #D32F2F;
                image: url({svg_path});
            }}
        """
        
        self.chk_remember_id = QCheckBox("Remember ID")
        self.chk_remember_id.setStyleSheet(chk_style)
        
        self.chk_remember_psw = QCheckBox("Remember Psw")
        self.chk_remember_psw.setStyleSheet(chk_style)
        
        chk_layout.addWidget(self.chk_remember_id)
        chk_layout.addWidget(self.chk_remember_psw)
        chk_layout.addStretch()
        content_layout.addLayout(chk_layout)
        
        # LOGIN Button
        self.btn_login = QPushButton("LOGIN")
        self.btn_login.setFixedHeight(38)
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #1565C0;
                color: white;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
                border: 1px solid #0D47A1;
                font-family: 'Malgun Gothic', '맑은 고딕', 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #0D47A1;
            }
            QPushButton:pressed {
                background-color: #0A2F6C;
            }
        """)
        self.btn_login.clicked.connect(self.on_login_click)
        content_layout.addWidget(self.btn_login)
        
        # Languages layout (indonesian excluded) - 3 top, 2 bottom rows to avoid text cut
        lang_layout = QGridLayout()
        lang_layout.setContentsMargins(0, 4, 0, 0)
        lang_layout.setSpacing(8)
        
        self.lang_group = QButtonGroup(self)
        self.lang_group.setExclusive(True)
        
        self.langs_config = [
            ("Korean", "KR"),
            ("English", "EN"),
            ("Chinese", "CH"),
            ("Vietnamese", "VN"),
            ("Spanish", "SP")
        ]
        
        lang_cb_style = f"""
            QCheckBox {{
                color: white;
                font-weight: bold;
                font-size: 10px;
                font-family: 'Malgun Gothic', '맑은 고딕', 'Segoe UI', Arial, sans-serif;
            }}
            QCheckBox::indicator {{
                width: 12px;
                height: 12px;
                border: 1px solid white;
                border-radius: 2px;
                background: transparent;
            }}
            QCheckBox::indicator:checked {{
                background-color: #D32F2F;
                border: 1px solid #D32F2F;
                image: url({svg_path});
            }}
        """
        
        self.lang_checkboxes = {}
        for name, code in self.langs_config:
            cb = QCheckBox(name)
            cb.setStyleSheet(lang_cb_style)
            self.lang_group.addButton(cb)
            self.lang_checkboxes[code] = cb
            
            # Map click to updating selected_lang
            def make_click_handler(c=code):
                return lambda: self.set_lang_code(c)
            cb.clicked.connect(make_click_handler())
            
        # Select Korean as default
        self.lang_checkboxes["KR"].setChecked(True)
        
        # Add checkboxes to the grid layout in 2 rows: 3 on top, 2 on bottom
        lang_layout.addWidget(self.lang_checkboxes["KR"], 0, 0)
        lang_layout.addWidget(self.lang_checkboxes["EN"], 0, 1)
        lang_layout.addWidget(self.lang_checkboxes["CH"], 0, 2)
        lang_layout.addWidget(self.lang_checkboxes["VN"], 1, 0)
        lang_layout.addWidget(self.lang_checkboxes["SP"], 1, 1)
        
        content_layout.addLayout(lang_layout)
        frame_layout.addWidget(content_widget)
        
        main_layout.addWidget(self.bg_frame)

    def set_lang_code(self, code):
        self.selected_lang = code

    # Move window on drag
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_position = None

    def close_app(self):
        sys.exit(0)

    def load_settings(self):
        remember_id = self.settings.value("remember_id", False, type=bool)
        remember_psw = self.settings.value("remember_psw", False, type=bool)
        saved_id = self.settings.value("saved_id", "Y6", type=str)
        saved_psw = self.settings.value("saved_psw", "", type=str)
        saved_lang = self.settings.value("saved_lang", "KR", type=str)
        
        self.chk_remember_id.setChecked(remember_id)
        self.chk_remember_psw.setChecked(remember_psw)
        
        if remember_id:
            self.txt_id.setText(saved_id)
            
        if remember_psw:
            self.txt_psw.setText(saved_psw)
            
        if saved_lang in self.lang_checkboxes:
            self.lang_checkboxes[saved_lang].setChecked(True)
            self.selected_lang = saved_lang

    def save_settings(self):
        remember_id = self.chk_remember_id.isChecked()
        remember_psw = self.chk_remember_psw.isChecked()
        id_val = self.txt_id.text().strip()
        psw_val = self.txt_psw.text()
        
        self.settings.setValue("remember_id", remember_id)
        self.settings.setValue("remember_psw", remember_psw)
        
        if remember_id:
            self.settings.setValue("saved_id", id_val)
        else:
            self.settings.remove("saved_id")
            
        if remember_psw:
            self.settings.setValue("saved_psw", psw_val)
        else:
            self.settings.remove("saved_psw")
            
        self.settings.setValue("saved_lang", self.selected_lang)

    def on_login_click(self):
        id_val = self.txt_id.text().strip()
        psw_val = self.txt_psw.text()
        
        if not id_val:
            QMessageBox.warning(self, "Warning", "Please enter User ID.")
            return
            
        # Call Backend /login API
        url = f"{API_BASE_URL}/login"
        payload = {
            "fact": self.fact_code,
            "idno": id_val,
            "pasw": psw_val
        }
        
        try:
            resp = requests.post(url, json=payload, timeout=3.0)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success", False):
                    # Save credentials settings
                    self.save_settings()
                    # Emit success signal and close login window
                    self.login_success.emit(self.fact_code, id_val, self.selected_lang)
                    self.close()
                else:
                    self.show_error_popup()
            else:
                self.show_error_popup()
        except Exception as e:
            print(f"Login API request error: {e}")
            self.show_error_popup()

    def show_error_popup(self):
        # Styled warning messagebox mapping "Invaild ID & Psw"
        msg = QMessageBox(self)
        msg.setWindowTitle("Login Failed")
        msg.setText("Invaild ID & Psw")
        msg.setIcon(QMessageBox.Critical)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #F9F8F3;
            }
            QLabel {
                color: #333333;
                font-weight: bold;
                font-family: 'Outfit', sans-serif;
            }
            QPushButton {
                background-color: #D32F2F;
                color: white;
                border-radius: 4px;
                padding: 6px 14px;
                font-weight: bold;
            }
        """)
        msg.exec()
