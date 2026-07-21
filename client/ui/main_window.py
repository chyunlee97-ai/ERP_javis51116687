import os
from PySide6.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve, QPoint, QParallelAnimationGroup, QPointF, QRectF
from PySide6.QtGui import QPixmap, QIcon, QCursor, QFontMetrics, QPainter, QPainterPath, QPen, QColor
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QComboBox, 
    QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, 
    QFrame, QHeaderView, QGraphicsDropShadowEffect, QSizePolicy,
    QTabWidget, QScrollArea
)
from ui.api_thread import ApiQueryThread, ApiProgramsThread
from ui.scifi_avatar import SciFiAvatarWidget, SpeechBubbleWidget
from ui.admin_panels import AdminPanelsWidget


# Get project root absolute path for loading images
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_version():
    version_file = os.path.join(PROJECT_ROOT, "version.txt")
    if os.path.exists(version_file):
        try:
            with open(version_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass
    return "ver.20260720.001"

class MarqueeRecommendWidget(QScrollArea):
    def __init__(self, parent=None, items=None, on_item_clicked=None, button_style=None):
        super().__init__(parent)
        self.on_item_clicked = on_item_clicked
        self.button_style = button_style
        
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.container_layout = QHBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(15)
        
        self.base_items = items or []
        # Triple the items to ensure seamless wrapping on wider screens
        self.display_items = self.base_items + self.base_items + self.base_items
        
        self.buttons = []
        for i, text in enumerate(self.display_items):
            btn = QPushButton(f"🔍 {text}")
            btn.setCursor(Qt.PointingHandCursor)
            if self.button_style:
                btn.setStyleSheet(self.button_style)
            
            base_text = self.base_items[i % len(self.base_items)]
            btn.clicked.connect(lambda checked=False, txt=base_text: self.handle_clicked(txt))
            self.container_layout.addWidget(btn)
            self.buttons.append(btn)
            
        self.setWidget(self.container)
        
        self.scroll_timer = QTimer(self)
        self.scroll_timer.timeout.connect(self.scroll_step)
        self.scroll_timer.start(30) # Tick every 30ms for smooth motion
        
        self.single_set_width = 0
        
    def set_items(self, items):
        # Clear existing buttons from layout
        for btn in self.buttons:
            self.container_layout.removeWidget(btn)
            btn.deleteLater()
        self.buttons.clear()
        
        self.base_items = items or []
        self.display_items = self.base_items + self.base_items + self.base_items
        
        for i, text in enumerate(self.display_items):
            btn = QPushButton(f"🔍 {text}")
            btn.setCursor(Qt.PointingHandCursor)
            if self.button_style:
                btn.setStyleSheet(self.button_style)
            
            base_text = self.base_items[i % len(self.base_items)]
            btn.clicked.connect(lambda checked=False, txt=base_text: self.handle_clicked(txt))
            self.container_layout.addWidget(btn)
            self.buttons.append(btn)
            
        self.single_set_width = 0
        hbar = self.horizontalScrollBar()
        if hbar:
            hbar.setValue(0)
            
    def handle_clicked(self, txt):
        if self.on_item_clicked:
            self.on_item_clicked(txt)
            
    def enterEvent(self, event):
        self.scroll_timer.stop()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.scroll_timer.start(30)
        super().leaveEvent(event)
        
    def scroll_step(self):
        hbar = self.horizontalScrollBar()
        if not hbar:
            return
            
        if self.single_set_width <= 0:
            width = 0
            count = len(self.base_items)
            for j in range(count):
                if j < len(self.buttons):
                    width += self.buttons[j].sizeHint().width() + 15
            self.single_set_width = width
            
        curr = hbar.value()
        next_val = curr + 1
        
        if self.single_set_width > 0 and next_val >= self.single_set_width:
            hbar.setValue(0)
        else:
            hbar.setValue(next_val)

class ToggleTriangleButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_collapsed = True
        self.setFixedSize(30, 20)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("background: transparent; border: none;")

    def set_collapsed(self, collapsed):
        self.is_collapsed = collapsed
        self.update()

    def enterEvent(self, event):
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        is_hovered = self.underMouse()
        color = QColor("#10a684") if is_hovered else QColor("#D32F2F")
        
        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        size = 11.0
        
        path = QPainterPath()
        if self.is_collapsed:  # Inverted triangle (pointing down)
            p1 = QPointF(cx - size/2, cy - size/3)
            p2 = QPointF(cx + size/2, cy - size/3)
            p3 = QPointF(cx, cy + 2*size/3)
        else:  # Regular triangle (pointing up)
            p1 = QPointF(cx - size/2, cy + size/3)
            p2 = QPointF(cx + size/2, cy + size/3)
            p3 = QPointF(cx, cy - 2*size/3)
            
        path.moveTo(p1)
        path.lineTo(p2)
        path.lineTo(p3)
        path.closeSubpath()
        
        pen = QPen(color, 2)
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        if is_hovered:
            fill_color = QColor(color)
            fill_color.setAlpha(40)
            painter.setBrush(fill_color)
        else:
            painter.setBrush(Qt.NoBrush)
            
        painter.drawPath(path)

class MainWindow(QWidget):
    def __init__(self, fact="Y6", idno="Y6", lang="KR"):
        super().__init__()
        
        # Load character images
        img_path = os.path.join(PROJECT_ROOT, "image", "ohsung_mark_256.png")
        self.pixmaps = {
            "idle": QPixmap(img_path),
            "thinking": QPixmap(img_path),
            "talking": QPixmap(img_path),
        }
        
        # [설정] 챗봇의 텍스트명 문구 (이후에 수동으로 변경 가능)
        self.bot_name = "OHSUNG"
        
        # Fallback to single colors if image doesn't exist (safety mechanism)
        for state, pixmap in self.pixmaps.items():
            if pixmap.isNull():
                print(f"[Warning] Image not found for state '{state}', generating dummy pixmap.")
                dummy = QPixmap(150, 150)
                dummy.fill(Qt.transparent)
                self.pixmaps[state] = dummy
                
        self.query_thread = None
        self.drag_position = None
        
        # Recommendations mapped by factory code prefix
        self.recommendations_map = {
            'K': ['LG 거래처 조회', 'A43 모델 조회', 'SE 제품코드 조회', 'A1 부품 조회', 'C 특성 조회','김해 영업 내선'],
            'Y': ['VIETNAM 거래처 조회', '355 모델 조회', 'C100 제품코드 조회', '33 부품 조회', 'D1 특성 조회', '양주 영업 내선'],
            'C': ['LG 거래처 조회', 'ACQ 모델 조회', 'WS 제품코드 조회', 'MAZ 부품 조회', 'CL 특성 조회','창원 영업 내선'],
            'G': ['LG 거래처 조회', 'EBR 모델 조회', 'A004 제품코드 조회', 'OFE 부품 조회', 'A01 특성 조회','구미 영업 내선']
        }
        
        # [변경전]
        # self.current_fact = "K1"
        # self.lang = "KR"
        # self.idno = "Y6"
        self.current_fact = fact
        self.lang = lang
        self.idno = idno
        self.programs_thread = None
        
        self.current_offset = 0
        self.has_more_data = False
        self.search_results = []
        self.current_search_params = {}
        
        # Setup UI layout
        self.init_ui()
        
        # Set initial state
        self.set_state("idle")
        
        # [변경전]
        # self.set_current_fact("K1")
        self.set_current_fact(fact)
        
    @property
    def current_mode(self):
        if hasattr(self, 'tab_widget'):
            return "general" if self.tab_widget.currentIndex() == 0 else "selective"
        return "general"
        
    def init_ui(self):
        # 1. Window styling: Frameless, transparent background, always on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumWidth(450)
        self.resize(495, 462)
        
        # Main Layout (Vertical)
        main_vbox = QVBoxLayout(self)
        main_vbox.setContentsMargins(10, 10, 10, 10)
        main_vbox.setSpacing(10)
        
        # ==========================================
        # TOP AREA: Character (Left) + Question Window (Right)
        # ==========================================
        top_hbox = QHBoxLayout()
        top_hbox.setSpacing(10)
        
        # A. Character Widget (Left)
        self.char_container = QWidget(self)
        self.char_container.setFixedSize(170, 170) # Sci-Fi Avatar size
        self.char_container.setCursor(QCursor(Qt.SizeAllCursor)) # Show drag cursor
        
        self.char_avatar = SciFiAvatarWidget(self.char_container)
        self.char_avatar.set_pixmaps(self.pixmaps)
        
        top_hbox.addWidget(self.char_container, 0, Qt.AlignVCenter)
        
        # Speech Bubble excluded per request
        # self.speech_bubble = SpeechBubbleWidget(self)
        # self.speech_bubble.move(160, 10)
        # self.speech_bubble.raise_()
        
        # B. Question Window (Right)
        self.q_frame = QFrame(self)
        self.q_frame.setObjectName("QuestionFrame")
        self.q_frame.setStyleSheet("""
            QFrame#QuestionFrame {
                background-color: #F9F8F3;
                border: 2px solid #D32F2F;
                border-radius: 15px;
            }
        """)
        
        # Question Frame Shadow Effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(Qt.black)
        shadow.setOffset(0, 4)
        self.q_frame.setGraphicsEffect(shadow)
        
        q_vbox = QVBoxLayout(self.q_frame)
        q_vbox.setContentsMargins(0, 0, 0, 6)
        q_vbox.setSpacing(4)
        
        # B-1. Purple Header Bar
        header_bar = QFrame(self.q_frame)
        header_bar.setObjectName("HeaderBar")
        header_bar.setFixedHeight(30)
        header_bar.setStyleSheet("""
            QFrame#HeaderBar {
                background-color: #D32F2F;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                border-bottom: 1px solid #B71C1C;
            }
        """)
        header_hbox = QHBoxLayout(header_bar)
        header_hbox.setContentsMargins(15, 0, 15, 0)
        
        title_label = QLabel(f"{self.bot_name} ERP Bot", header_bar)
        title_label.setStyleSheet("color: white; font-weight: bold; font-family: 'Outfit', 'Inter', sans-serif; font-size: 13px;")
        header_hbox.addWidget(title_label, 1) # stretch title to push rest to right
        
        # Drag indicator inside header bar
        drag_hint = QLabel("⋮⋮ Drag to Move", header_bar)
        drag_hint.setStyleSheet("color: #FFCDD2; font-size: 11px; font-family: sans-serif; margin-right: 5px;")
        header_hbox.addWidget(drag_hint, 0)
        
        # Minimize to Tray [v] Button
        self.btn_minimize = QPushButton("[v]", header_bar)
        self.btn_minimize.setToolTip("시스템 트레이로 내려 숨기기")
        self.btn_minimize.setCursor(Qt.PointingHandCursor)
        self.btn_minimize.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #FFCDD2;
                border: none;
                font-weight: bold;
                font-size: 12px;
                padding: 2px 6px;
            }
            QPushButton:hover {
                color: white;
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 4px;
            }
        """)
        self.btn_minimize.clicked.connect(self.minimize_to_tray)
        header_hbox.addWidget(self.btn_minimize, 0)
        
        q_vbox.addWidget(header_bar)
        
        # Padding content container for QBox content
        content_vbox = QVBoxLayout()
        content_vbox.setContentsMargins(12, 3, 12, 3)
        content_vbox.setSpacing(4)
        
        # B-2. Mode Selection Segment via QTabWidget (Delay-free native tabs)
        self.tab_widget = QTabWidget(self.q_frame)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: transparent;
            }
            QTabBar::tab {
                background-color: #EFECE1;
                color: #555555;
                font-family: 'Outfit', 'Inter', sans-serif;
                font-size: 12px;
                font-weight: bold;
                padding: 5px 12px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 4px;
                border: 1px solid #CBC8B8;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #D32F2F;
                border-bottom: 2px solid white;
            }
            QTabBar::tab:hover {
                background-color: #E3DFD2;
            }
        """)

        # ------------------
        # Tab 1: General Mode (자연어)
        # ------------------
        general_tab = QWidget()
        gen_layout = QVBoxLayout(general_tab)
        gen_layout.setContentsMargins(0, 6, 0, 0)
        gen_layout.setSpacing(6)

        # Input & Send Row
        input_hbox_gen = QHBoxLayout()
        input_hbox_gen.setSpacing(6)
        
        self.input_field_gen = QLineEdit(general_tab)
        self.input_field_gen.setPlaceholderText(f"{self.bot_name} -   [예시]처럼 자연어 검색.")
        self.input_field_gen.setStyleSheet("""
            QLineEdit {
                border: 1px solid #CBC8B8;
                border-radius: 8px;
                padding: 7px 12px;
                background-color: white;
                font-size: 13px;
                color: #333333;
            }
            QLineEdit:focus {
                border: 2px solid #D32F2F;
            }
        """)
        self.input_field_gen.returnPressed.connect(self.on_send)
        
        self.btn_send_gen = QPushButton("전송", general_tab)
        self.btn_send_gen.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_send_gen.setStyleSheet("""
            QPushButton {
                background-color: #D32F2F;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 7px 15px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #B71C1C;
            }
            QPushButton:pressed {
                background-color: #961414;
            }
        """)
        self.btn_send_gen.clicked.connect(self.on_send)
        
        input_hbox_gen.addWidget(self.input_field_gen, 1)
        input_hbox_gen.addWidget(self.btn_send_gen)
        gen_layout.addLayout(input_hbox_gen)
        
        # Add spacing to align bottom margin with selective tab
        gen_layout.addSpacing(11)
        
        # Quick Queries Row (Marquee Scroll)
        quick_hbox_gen = QHBoxLayout()
        quick_hbox_gen.setSpacing(5)
        self.lbl_hint_gen = QLabel("추천:", general_tab)
        self.lbl_hint_gen.setStyleSheet("color: #666666; font-size: 11px; font-weight: bold;")
        quick_hbox_gen.addWidget(self.lbl_hint_gen)

        hints_gen = self.recommendations_map['K']
        
        def on_recommend_clicked(text):
            self.input_field_gen.setText(text)
            self.input_field_gen.setFocus()
            
        self.marquee_widget = MarqueeRecommendWidget(
            parent=general_tab,
            items=hints_gen,
            on_item_clicked=on_recommend_clicked,
            button_style=self.get_quick_btn_style()
        )
        self.marquee_widget.setFixedHeight(30)
        quick_hbox_gen.addWidget(self.marquee_widget, 1)
        gen_layout.addLayout(quick_hbox_gen)
        
        self.tab_widget.addTab(general_tab, "일반(자연어)")

        # ------------------
        # Tab 2: Selective Mode (SQL 지정)
        # ------------------
        selective_tab = QWidget()
        sel_layout = QVBoxLayout(selective_tab)
        sel_layout.setContentsMargins(0, 6, 0, 0)
        sel_layout.setSpacing(6)

        self.cb_sql_list = QComboBox(selective_tab)
        self.cb_sql_list.addItem("📁 1. 거래처 조회", "vend_search")
        self.cb_sql_list.addItem("📊 2. 모델정보 조회", "model_search")
        self.cb_sql_list.addItem("🔑 3. 제품코드 조회", "prod_code_search")
        self.cb_sql_list.addItem("⚙️ 4. 부품정보 조회", "part_detail_search")
        self.cb_sql_list.addItem("🏷️ 5. 부품특성코드 조회", "part_tcod_search")
        self.cb_sql_list.addItem("📞 6. 내선번호 조회", "phone_search")
        self.cb_sql_list.setStyleSheet("""
            QComboBox {
                border: 1px solid #CBC8B8;
                border-radius: 8px;
                padding: 5px 30px 5px 12px;
                background-color: white;
                font-size: 13px;
                color: #333333;
            }
            QComboBox:hover {
                border-color: #D32F2F;
            }
            QComboBox:focus {
                border: 2px solid #D32F2F;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border: none;
            }
            QComboBox::down-arrow {
                image: url(client/arrow_down.svg);
                width: 12px;
                height: 12px;
            }
        """)

        # SQL Dropdown row
        sql_hbox = QHBoxLayout()
        sql_hbox.setSpacing(6)
        
        lbl_query = QLabel("선택 :", selective_tab)
        lbl_query.setStyleSheet("font-size: 13px; font-weight: bold; color: #555555;")
        sql_hbox.addWidget(lbl_query)
        sql_hbox.addWidget(self.cb_sql_list, 1)
        sel_layout.addLayout(sql_hbox)

        self.cb_sql_list.currentIndexChanged.connect(self.on_selective_item_changed)

        # Input & Send Row
        input_hbox_sel = QHBoxLayout()
        input_hbox_sel.setSpacing(6)

        self.input_field_sel = QLineEdit(selective_tab)
        self.input_field_sel.setPlaceholderText("검색 조건에 해당할 키워드(@as_find)를 입력하세요. (예: LG, 에이스)")
        self.input_field_sel.setStyleSheet("""
            QLineEdit {
                border: 1px solid #CBC8B8;
                border-radius: 8px;
                padding: 7px 12px;
                background-color: white;
                font-size: 13px;
                color: #333333;
            }
            QLineEdit:focus {
                border: 2px solid #D32F2F;
            }
        """)
        self.input_field_sel.returnPressed.connect(self.on_send)

        self.btn_send_sel = QPushButton("전송", selective_tab)
        self.btn_send_sel.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_send_sel.setStyleSheet("""
            QPushButton {
                background-color: #D32F2F;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 7px 15px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #B71C1C;
            }
            QPushButton:pressed {
                background-color: #961414;
            }
        """)
        self.btn_send_sel.clicked.connect(self.on_send)

        input_hbox_sel.addWidget(self.input_field_sel, 1)
        input_hbox_sel.addWidget(self.btn_send_sel)
        sel_layout.addLayout(input_hbox_sel)



        self.tab_widget.addTab(selective_tab, "조건 선택")

        content_vbox.addWidget(self.tab_widget)
        
        q_vbox.addLayout(content_vbox)
        top_hbox.addWidget(self.q_frame, 1)
        main_vbox.addLayout(top_hbox)
        
        # ==========================================
        # BOTTOM AREA: Answer / Chat Window (Response)
        # ==========================================
        self.a_frame = QFrame(self)
        self.a_frame.setObjectName("AnswerFrame")
        self.a_frame.setStyleSheet("""
            QFrame#AnswerFrame {
                background-color: #F9F8F3;
                border: 2px solid #D32F2F;
                border-radius: 15px;
            }
        """)
        
        # Answer Frame Shadow Effect
        shadow2 = QGraphicsDropShadowEffect(self)
        shadow2.setBlurRadius(15)
        shadow2.setColor(Qt.black)
        shadow2.setOffset(0, 4)
        self.a_frame.setGraphicsEffect(shadow2)
        
        a_vbox = QVBoxLayout(self.a_frame)
        a_vbox.setContentsMargins(15, 28, 15, 5)
        a_vbox.setSpacing(15)
        
        # C-1. Answer State / Text Label (Moved next to buttons in actions layout)
        
        # C-2. Result Data Table (QTableWidget)
        self.table_widget = QTableWidget(self.a_frame)
        self.table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #E8E5D8;
                border: 1px solid #CBC8B8;
                border-radius: 8px;
                font-size: 12px;
                color: #333333;
            }
            QHeaderView::section {
                background-color: #EFECE1;
                color: #555555;
                font-weight: bold;
                border: 1px solid #CBC8B8;
                padding: 3px;
            }
            QTableWidget::item:selected {
                background-color: #FFCDD2;
                color: black;
            }
        """)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_widget.horizontalHeader().setMinimumSectionSize(60)
        self.table_widget.horizontalHeader().setFixedHeight(28)
        self.table_widget.verticalHeader().setDefaultSectionSize(24)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setFixedHeight(179)
        a_vbox.addWidget(self.table_widget)
        a_vbox.addStretch(1)
        self.table_widget.verticalScrollBar().valueChanged.connect(self.on_table_scroll)
        self.table_widget.horizontalScrollBar().rangeChanged.connect(self.on_hscrollbar_range_changed)
        self.table_widget.cellClicked.connect(self.on_cell_clicked)
        
        # C-3. Control Action Buttons (Detail View, Select Data)
        self.actions_layout = QHBoxLayout()
        self.actions_layout.setSpacing(10)
        
        self.status_label = QLabel("질문을 입력하시면 사내 DB를 조회하여 대답을 드립니다.", self.a_frame)
        self.status_label.setStyleSheet("color: #555555; font-size: 12px; font-weight: bold; font-family: sans-serif;")
        
        # [변경전]
        # self.btn_detail = QPushButton("🔍 상세보기", self.a_frame)
        # self.btn_detail.setStyleSheet(self.get_action_button_style())
        # self.btn_detail.clicked.connect(self.on_detail_view)
        
        self.btn_use_data = QPushButton("✓ 선택자료 사용", self.a_frame)
        self.btn_use_data.setStyleSheet(self.get_action_button_style())
        self.btn_use_data.clicked.connect(self.on_use_data)
        
        self.actions_layout.addWidget(self.status_label)
        self.actions_layout.addStretch()
        # [변경전]
        # self.actions_layout.addWidget(self.btn_detail)
        self.actions_layout.addWidget(self.btn_use_data)
        
        actions_wrapper = QVBoxLayout()
        actions_wrapper.setSpacing(2)
        actions_wrapper.addLayout(self.actions_layout)
        
        self.version_label = QLabel(get_version(), self.a_frame)
        self.version_label.setStyleSheet("color: #9c998f; font-size: 9px;")
        self.version_label.setAlignment(Qt.AlignRight)
        self.version_label.setContentsMargins(0, 0, 5, 0)
        
        actions_wrapper.addWidget(self.version_label)
        
        a_vbox.addLayout(actions_wrapper)
        
        main_vbox.addWidget(self.a_frame, 1)
        
        # C-4. Collapse Toggle Button (▼ / ▲)
        self.btn_toggle_collapse = ToggleTriangleButton(self.a_frame)
        self.btn_toggle_collapse.setObjectName("CollapseToggleBtn")
        self.btn_toggle_collapse.clicked.connect(self.toggle_collapse)
        self.is_collapsed = False
        
        import config
        self.show_admin = getattr(config, 'SHOW_DEVELOPER_PANELS', False)
        
        self.admin_panels = AdminPanelsWidget(self, project_root=PROJECT_ROOT)
        self.admin_panels.cb_fact.currentIndexChanged.connect(self.on_admin_fact_changed)
        main_vbox.addWidget(self.admin_panels)
        
        if self.show_admin:
            self.admin_panels.setVisible(True)
        else:
            self.admin_panels.setVisible(False)
            
        # Initial state: collapsed
        self.set_collapsed_state(True, animate=False)
        
    def get_quick_btn_style(self):
        return """
            QPushButton {
                background-color: transparent;
                color: #D32F2F;
                border: 1px dashed #D32F2F;
                border-radius: 10px;
                padding: 3px 10px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #EFECE1;
            }
        """

    def get_action_button_style(self):
        return """
            QPushButton {
                background-color: #EFECE1;
                color: #333333;
                border: 1px solid #CBC8B8;
                border-radius: 6px;
                padding: 6px 15px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #E3DFD2;
            }
            QPushButton:pressed {
                background-color: #CBC8B8;
            }
        """

    def get_current_input_field(self):
        if self.tab_widget.currentIndex() == 0:
            return self.input_field_gen
        return self.input_field_sel

    def send_immediate_message(self, text):
        input_field = self.get_current_input_field()
        input_field.setText(text)
        self.on_send()
        
    def set_state(self, state: str, text: str = ""):
        self.char_avatar.set_state(state)
        # Speech Bubble updates commented out per request
        # self.speech_bubble.set_state(state, text)
        # if state == "idle":
        #     self.speech_bubble.hide()
            
    def on_selective_item_changed(self):
        self.input_field_sel.clear()
        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(0)
        self.status_label.setText("질문을 입력하시면 사내 DB를 조회하여 대답을 드립니다.")
        self.set_state("idle")
        
    def on_admin_fact_changed(self):
        code = self.admin_panels.cb_fact.currentData()
        if code:
            self.set_current_fact(code)
            
    def set_current_fact(self, fact):
        self.current_fact = fact
        if not fact:
            self.marquee_widget.setVisible(False)
            self.lbl_hint_gen.setVisible(False)
            return
            
        first_char = fact[0].upper()
        if first_char in self.recommendations_map:
            items = self.recommendations_map[first_char]
            self.marquee_widget.set_items(items)
            self.marquee_widget.setVisible(True)
            self.lbl_hint_gen.setVisible(True)
        else:
            self.marquee_widget.setVisible(False)
            self.lbl_hint_gen.setVisible(False)
            
        self.load_selective_programs()
        
    def load_selective_programs(self):
        if self.programs_thread and self.programs_thread.isRunning():
            try:
                self.programs_thread.finished_signal.disconnect(self.on_programs_loaded)
            except (TypeError, RuntimeError):
                pass
            self.programs_thread.terminate()
            self.programs_thread.wait()
            
        self.programs_thread = ApiProgramsThread(
            fact=self.current_fact,
            lang=self.lang,
            idno=self.idno
        )
        self.programs_thread.finished_signal.connect(self.on_programs_loaded)
        self.programs_thread.start()
        
    def on_programs_loaded(self, programs):
        if not programs:
            programs = [
                {"code_code": "1", "name": "거래처 조회", "intent": "vend_search"},
                {"code_code": "2", "name": "모델정보 조회", "intent": "model_search"},
                {"code_code": "3", "name": "제품코드 조회", "intent": "prod_code_search"},
                {"code_code": "4", "name": "부품정보 조회", "intent": "part_detail_search"},
                {"code_code": "5", "name": "부품특성코드 조회", "intent": "part_tcod_search"},
                {"code_code": "6", "name": "내선번호 조회", "intent": "phone_search"}
            ]
            
        self.cb_sql_list.blockSignals(True)
        old_intent = self.cb_sql_list.currentData()
        self.cb_sql_list.clear()
        
        emojis = [
            "📁", "📊", "🔑", "⚙️", "🏷️", "📞", "📦", "📋", "💼", "🏢",
            "🚚", "🏭", "📅", "👤", "💰", "🔍", "📈", "📉", "🛡️", "✉️",
            "🛠️", "💻", "📱", "💾", "🔗", "✏️"
        ]
        
        intent_emojis = {
            "vend_search": "📁",
            "model_search": "📊",
            "prod_code_search": "🔑",
            "part_detail_search": "⚙️",
            "part_tcod_search": "🏷️",
            "phone_search": "📞"
        }
        
        for i, prog in enumerate(programs):
            code = str(prog.get("code_code", "")).strip()
            name = str(prog.get("name", "")).strip()
            intent = str(prog.get("intent", "")).strip()
            
            emoji = intent_emojis.get(intent)
            if not emoji:
                emoji = emojis[i % len(emojis)]
                
            label = f"{emoji} {i+1}. {name}"
            self.cb_sql_list.addItem(label, intent)
            
        if old_intent:
            idx = self.cb_sql_list.findData(old_intent)
            if idx >= 0:
                self.cb_sql_list.setCurrentIndex(idx)
            else:
                self.cb_sql_list.setCurrentIndex(0)
        else:
            self.cb_sql_list.setCurrentIndex(0)
            
        self.cb_sql_list.blockSignals(False)
        self.on_selective_item_changed()
        
    def on_send(self):
        # Prevent double submit or running background queries
        if self.query_thread and self.query_thread.isRunning():
            return  # 이미 조회 중인 경우 중복 전송 요청 무시 (QThread 중첩 및 가비지 컬렉션 세그폴트 강제 종료 예방)
            
        text = self.get_current_input_field().text().strip()
        
        if not text:
            # Show "Insert Text!" on chatbot avatar overlay for 2 seconds (2000 ms)
            self.char_avatar.show_mini_message("Insert Text!", is_success=False, duration_ms=2000)
            if self.current_mode == "general":
                self.status_label.setText("⚠️ 질문을 입력해 주세요.")
            else:
                self.status_label.setText("⚠️ 검색어를 입력해 주세요.")
            return
            
        import time
        self.query_start_time = time.time()
        self.set_state("thinking")
        self.status_label.setText("데이터베이스 조회 중...")
        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(0)
        
        self.current_offset = 0
        self.has_more_data = True
        self.search_results = []
        self.current_search_params = {
            "mode": self.current_mode,
            "text": text,
            "fact": self.current_fact,
            "intent": self.cb_sql_list.currentData() if self.current_mode == "selective" else None
        }
        
        # Start QThread based on mode
        fact_val = self.current_fact
        self.query_thread = ApiQueryThread(
            message=text if self.current_mode == "general" else "",
            intent=self.current_search_params["intent"],
            fact=fact_val,
            as_find=text if self.current_mode == "selective" else "",
            limit=50,
            offset=0
        )
            
        self.query_thread.finished_signal.connect(self.on_query_finished)
        self.query_thread.start()
        
    def on_query_finished(self, response: dict):
        import time
        elapsed = time.time() - getattr(self, "query_start_time", 0)
        delay = max(0.0, 1.0 - elapsed) # 최소 1.0초 동안 thinking 애니메이션 유지
        
        if delay > 0.0:
            QTimer.singleShot(int(delay * 1000), lambda: self._process_query_finished(response))
        else:
            self._process_query_finished(response)

    def _process_query_finished(self, response: dict):
        msg = response.get("message", "데이터를 불러왔습니다.")
        self.set_state("talking", msg)
        
        # Reset to idle after 5 seconds
        QTimer.singleShot(5000, lambda: self.set_state("idle"))
        
        query_script = response.get("query_script", "")
        intent_found = response.get("intent", "None") != "None"  # intent가 "None"이 아니면 매칭 성공한 것
        input_text = self.get_current_input_field().text().strip()
        if hasattr(self, 'admin_panels'):
            self.admin_panels.set_sql_script(query_script, input_text=input_text, intent_found=intent_found)
            
        new_results = response.get("result", [])
        
        if not new_results and self.current_offset == 0:
            self.char_avatar.show_mini_message("No data!", is_success=False)
            self.status_label.setText("[0건 조회]")
            self.table_widget.clearContents()
            self.table_widget.setRowCount(0)
            self.table_widget.setColumnCount(0)
            self.has_more_data = False
            self.set_collapsed_state(False, animate=True)
            return
            
        self.char_avatar.show_mini_message("Complete!", is_success=True)
        self.search_results.extend(new_results)
        self.set_collapsed_state(False, animate=True)
        
        if len(new_results) < 50:
            self.has_more_data = False
        else:
            self.has_more_data = True
            
        self.status_label.setText(f"[{len(self.search_results)}건 조회]")
            
        # Display data in table
        self.update_table_view(new_results, self.current_offset)
        
    def update_table_view(self, new_results, new_results_offset):
        if not self.search_results:
            return
            
        columns = list(self.search_results[0].keys())
        
        if new_results_offset == 0:
            self.table_widget.clearContents()
            self.table_widget.setRowCount(0)
            self.table_widget.setColumnCount(len(columns) + 1)
            # [순번 헤더 명칭 설정] 아래의 "NO."를 변경하여 순번 컬럼의 헤더 이름을 수정할 수 있습니다.
            self.table_widget.setHorizontalHeaderLabels(["NO."] + columns)
            
            fm = QFontMetrics(self.table_widget.font())
            no_col_width = max(40, max(fm.horizontalAdvance("999") + 16, fm.horizontalAdvance("NO.") + 16))
            self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
            self.table_widget.setColumnWidth(0, no_col_width)
            for c in range(1, len(columns) + 1):
                self.table_widget.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeToContents)
        
        start_row = self.table_widget.rowCount()
        self.table_widget.setRowCount(start_row + len(new_results))
        
        for i, row_data in enumerate(new_results):
            row_idx = start_row + i
            # [NO.] Column
            no_item = QTableWidgetItem(str(row_idx + 1))
            no_item.setTextAlignment(Qt.AlignCenter)
            no_item.setFlags(no_item.flags() ^ Qt.ItemIsEditable)
            self.table_widget.setItem(row_idx, 0, no_item)
            
            for col_idx, col_name in enumerate(columns):
                val = row_data[col_name]
                item = QTableWidgetItem(str(val) if val is not None else "")
                # Make cells read-only
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.table_widget.setItem(row_idx, col_idx + 1, item)
                
        QTimer.singleShot(10, self._adjust_columns_to_fill)

    def _adjust_columns_to_fill(self):
        if not self.table_widget.isVisible():
            return
            
        cols = self.table_widget.columnCount()
        if cols <= 1:
            return
            
        total_width = 0
        for c in range(cols):
            total_width += self.table_widget.horizontalHeader().sectionSize(c)
            
        viewport_width = self.table_widget.viewport().width()
        
        # If total width is less than viewport, stretch columns to fill the empty space
        if total_width > 0 and total_width < viewport_width:
            for c in range(1, cols):
                self.table_widget.horizontalHeader().setSectionResizeMode(c, QHeaderView.Stretch)
        else:
            for c in range(1, cols):
                self.table_widget.horizontalHeader().setSectionResizeMode(c, QHeaderView.Interactive)

    def on_cell_clicked(self, row, column):
        if column == 0:
            self.table_widget.selectRow(row)

    def on_table_scroll(self, value):
        scrollbar = self.table_widget.verticalScrollBar()
        if scrollbar.maximum() > 0 and value >= scrollbar.maximum() - 2:
            if self.has_more_data and (not self.query_thread or not self.query_thread.isRunning()):
                self.load_next_page()

    def on_hscrollbar_range_changed(self, min, max):
        # [변경전]
        # if max > 0:
        #     self.table_widget.setFixedHeight(167)
        # else:
        #     self.table_widget.setFixedHeight(150)
        self.table_widget.setFixedHeight(179)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'btn_toggle_collapse') and hasattr(self, 'a_frame'):
            btn_x = self.a_frame.width() - 45
            # Center vertically when collapsed (height <= 35), else position at top margin (y = 8)
            if self.a_frame.height() <= 35:
                btn_y = (self.a_frame.height() - self.btn_toggle_collapse.height()) / 2
            else:
                btn_y = 8
            self.btn_toggle_collapse.move(btn_x, btn_y)

    def toggle_collapse(self):
        self.set_collapsed_state(not self.is_collapsed, animate=True)

    def set_collapsed_state(self, collapse: bool, animate: bool = True):
        self.is_collapsed = collapse
        
        # [변경전]
        # if self.show_admin:
        #     expanded_h = 780
        #     collapsed_h = 538
        # else:
        #     expanded_h = 462
        #     collapsed_h = 220
        # Adjusted collapsed height to 230 (no admin) / 548 (admin) to give a_frame a minimum height of 30px, 
        # which allows Qt border-radius: 15px to render rounded corners correctly.
        if self.show_admin:
            expanded_h = 780
            collapsed_h = 548
        else:
            expanded_h = 462
            collapsed_h = 230
            
        target_h = collapsed_h if collapse else expanded_h
        
        # Update custom button collapsed status to trigger vector repaint (▼ / ▲)
        self.btn_toggle_collapse.set_collapsed(collapse)
        
        # Performance optimization: immediately hide table and buttons to prevent layout recalculation lags on resize
        if collapse:
            self._update_a_frame_children_visibility(False)
            
        if not animate:
            self.resize(self.width(), target_h)
            self._update_a_frame_children_visibility(not collapse)
            self.btn_toggle_collapse.set_collapsed(collapse)
            return
            
        # Smooth transition animation targeting window size
        from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QSize
        self.collapse_anim = QPropertyAnimation(self, b"size")
        self.collapse_anim.setDuration(300)
        self.collapse_anim.setStartValue(self.size())
        self.collapse_anim.setEndValue(QSize(self.width(), target_h))
        self.collapse_anim.setEasingCurve(QEasingCurve.OutQuad)
        
        # Show children after expand animation completes
        if not collapse:
            self.collapse_anim.finished.connect(lambda: self._update_a_frame_children_visibility(True))
            
        self.collapse_anim.start()
        
    def _update_a_frame_children_visibility(self, visible: bool):
        self.table_widget.setVisible(visible)
        self.status_label.setVisible(visible)
        self.btn_use_data.setVisible(visible)
        self.version_label.setVisible(visible)

    def load_next_page(self):
        if self.query_thread and self.query_thread.isRunning():
            return
            
        if not self.has_more_data:
            return
            
        import time
        self.query_start_time = time.time()
        self.set_state("thinking")
        self.current_offset += 50
        self.status_label.setText(f"데이터베이스 추가 조회 중... (Loaded: {len(self.search_results)})")
        
        params = self.current_search_params
        mode = params.get("mode")
        text = params.get("text")
        fact = params.get("fact")
        intent = params.get("intent")
        
        self.query_thread = ApiQueryThread(
            message=text if mode == "general" else "",
            intent=intent,
            fact=fact,
            as_find=text if mode == "selective" else "",
            limit=50,
            offset=self.current_offset
        )
        self.query_thread.finished_signal.connect(self.on_query_finished)
        self.query_thread.start()
        
    def on_detail_view(self):
        selected_ranges = self.table_widget.selectedRanges()
        if not selected_ranges:
            self.status_label.setText("💡 상세보기를 하려면 테이블의 행을 선택하세요.")
            return
        
        row = selected_ranges[0].topRow()
        cols = self.table_widget.columnCount()
        
        details = []
        for c in range(1, cols):
            col_name = self.table_widget.horizontalHeaderItem(c).text()
            val = self.table_widget.item(row, c).text()
            details.append(f"{col_name}: {val}")
            
        details_str = " | ".join(details)
        self.status_label.setText(f"📋 선택항목 상세: {details_str}")
        
    def on_use_data(self):
        selected_ranges = self.table_widget.selectedRanges()
        if not selected_ranges:
            self.status_label.setText("💡 사용할 데이터를 테이블에서 선택해 주세요.")
            return
            
        r_range = selected_ranges[0]
        lines = []
        for r in range(r_range.topRow(), r_range.bottomRow() + 1):
            row_vals = []
            for c in range(r_range.leftColumn(), r_range.rightColumn() + 1):
                if c == 0 and r_range.leftColumn() == 0 and r_range.rightColumn() > 0:
                    continue
                item = self.table_widget.item(r, c)
                row_vals.append(item.text() if item else "")
            lines.append("\t".join(row_vals))
        selected_text = "\n".join(lines)
        
        if not selected_text.strip():
            row = r_range.topRow()
            item = self.table_widget.item(row, 1)
            selected_text = item.text() if item else ""
            
        from PySide6.QtGui import QGuiApplication
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(selected_text)
        
        # Show temporary "[복사했습니다]" message
        original_msg = self.status_label.text()
        self.status_label.setText("✓ [복사했습니다]")
        
        QTimer.singleShot(1500, lambda: self.status_label.setText(original_msg))
        
    # ==========================================
    # MOUSE EVENTS: Allow window drag & move
    # ==========================================
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Check if clicked on character or header bar to allow dragging
            local_pos = event.position().toPoint()
            # If clicked character or within question window frame (header bar area)
            if self.char_container.geometry().contains(local_pos) or self.q_frame.geometry().contains(local_pos):
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
                
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
            
    def mouseReleaseEvent(self, event):
        self.drag_position = None
        
    def minimize_to_tray(self):
        if hasattr(self, 'anim_group') and self.anim_group.state() == QPropertyAnimation.Running:
            return
            
        curr_pos = self.pos()
        target_pos = QPoint(curr_pos.x(), curr_pos.y() + 80)
        
        self.pos_anim = QPropertyAnimation(self, b"pos")
        self.pos_anim.setDuration(250)
        self.pos_anim.setStartValue(curr_pos)
        self.pos_anim.setEndValue(target_pos)
        self.pos_anim.setEasingCurve(QEasingCurve.InCubic)
        
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(250)
        self.opacity_anim.setStartValue(1.0)
        self.opacity_anim.setEndValue(0.0)
        self.opacity_anim.setEasingCurve(QEasingCurve.InCubic)
        
        self.anim_group = QParallelAnimationGroup()
        self.anim_group.addAnimation(self.pos_anim)
        self.anim_group.addAnimation(self.opacity_anim)
        
        def on_finished():
            self.hide()
            self.setWindowOpacity(1.0)
            self.move(curr_pos)
            
        self.anim_group.finished.connect(on_finished)
        self.anim_group.start()

    def restore_from_tray(self):
        if self.isVisible() and not (hasattr(self, 'anim_group') and self.anim_group.state() == QPropertyAnimation.Running):
            self.raise_()
            self.activateWindow()
            return
            
        if hasattr(self, 'anim_group') and self.anim_group.state() == QPropertyAnimation.Running:
            self.anim_group.stop()
            
        target_pos = self.pos()
        start_pos = QPoint(target_pos.x(), target_pos.y() + 80)
        
        self.move(start_pos)
        self.setWindowOpacity(0.0)
        self.show()
        
        self.pos_anim = QPropertyAnimation(self, b"pos")
        self.pos_anim.setDuration(250)
        self.pos_anim.setStartValue(start_pos)
        self.pos_anim.setEndValue(target_pos)
        self.pos_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(250)
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        self.opacity_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        self.anim_group = QParallelAnimationGroup()
        self.anim_group.addAnimation(self.pos_anim)
        self.anim_group.addAnimation(self.opacity_anim)
        
        def on_finished():
            self.raise_()
            self.activateWindow()
            
        self.anim_group.finished.connect(on_finished)
        self.anim_group.start()
        
    def closeEvent(self, event):
        event.ignore()
        self.minimize_to_tray()
